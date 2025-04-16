from django.db import models
from django.contrib.auth.models import User


class District(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='districts/', null=True, blank=True)

    def __str__(self):
        return self.name


class Building(models.Model):
    address = models.CharField(max_length=200)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    year_built = models.IntegerField()
    image = models.ImageField(upload_to='buildings/', null=True, blank=True)

    def __str__(self):
        return self.address


class Apartment(models.Model):
    FINISHING_CHOICES = [
        ('', 'Любая отделка'),
        ('черновая', 'Черновая'),
        ('чистовая', 'Чистовая'),
        ('евро', 'Евроремонт'),
        ('дизайнерский', 'Дизайнерский'),
    ]

    building = models.ForeignKey(Building, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    bedrooms = models.IntegerField()
    square_footage = models.DecimalField(max_digits=6, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='apartments/images/', null=True, blank=True)
    is_sold = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    sold_date = models.DateField(null=True, blank=True)
    floor = models.IntegerField(null=True, blank=True)
    finishing = models.CharField(
        max_length=20,
        choices=FINISHING_CHOICES,
        default='',
        verbose_name='Тип отделки'
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    allow_multiple_purchases = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.building} - {self.bedrooms} комн. - {self.price} руб"

    def get_main_image(self):
        try:
            return self.images.get(is_main=True).image.url
        except ApartmentImage.DoesNotExist:
            if self.image:
                return self.image.url
            return None


class ApartmentImage(models.Model):
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='apartments/images/')
    alt_text = models.CharField(max_length=255, null=True, blank=True)
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return f'Фото для {self.apartment}'


class InterestRate(models.Model):
    CALCULATOR_CHOICES = [
        ('Banc1', 'Банке не обманывает'),
        ('Banc2', 'Может гдето и обмани'),
        ('Banc3', 'Сто процентов обманываем'),
        ('Banc4', 'Сто процентов не обманываем'),
    ]

    calculator_type = models.CharField(max_length=50, choices=CALCULATOR_CHOICES, unique=True)
    rate = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Процентная ставка (%)")

    def __str__(self):
        return f"{self.get_calculator_type_display()} - {self.rate}%"


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class InfrastructureItem(models.Model):
    INFRASTRUCTURE_TYPES = [
        ('clinic', 'Поликлиника'),
        ('park', 'Парк'),
        ('parking', 'Парковка'),
        ('school', 'Школа'),
        ('kindergarten', 'Детский сад'),
        ('cafe', 'Кафе'),
        ('shop', 'Магазин'),
        ('pharmacy', 'Аптека')
    ]

    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='infrastructure')
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=INFRASTRUCTURE_TYPES)
    address = models.CharField(max_length=300)
    image = models.ImageField(upload_to='infrastructure/', blank=True, null=True)
    working_hours = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.get_type_display()}: {self.name}"