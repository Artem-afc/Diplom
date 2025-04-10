from django import forms
from .models import Apartment
from .models import Subscriber

class MortgageCalculatorForm(forms.Form):
    CALCULATOR_CHOICES = [
        ('Banc1', 'Банке не обманывает'),
        ('Banc2', 'Может гдето и обмани'),
        ('Banc3', 'Сто процентов обманываем'),
        ('Banc4', 'Сто процентов не обманываем'),
    ]
    calculator_type = forms.ChoiceField(choices=CALCULATOR_CHOICES, label="Тип калькулятора")
    price = forms.DecimalField(label="Стоимость квартиры (руб)", min_value=0)
    down_payment = forms.DecimalField(label="Первоначальный взнос (руб)", min_value=0)
    loan_term = forms.IntegerField(label="Срок кредита (лет)", min_value=1)

from django import forms


class SubscriberForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'Ваш email',
                'class': 'form-control'
            })
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        if Subscriber.objects.filter(email=email).exists():
            raise forms.ValidationError("Этот email уже подписан")
        return email

class ApartmentForm(forms.ModelForm):
    class Meta:
        model = Apartment
        fields = ['building', 'price', 'bedrooms', 'square_footage', 'description', 'image', 'is_sold', 'floor']


class ApartmentSearchForm(forms.Form):

    BEDROOMS_CHOICES = [
        ('', 'Любое количество'),
        (1, '1 комната'),
        (2, '2 комнаты'),
        (3, '3 комнаты'),
        (4, '4 комнаты'),
        (5, '5+ комнат'),
    ]

    floor = forms.IntegerField(
        required=False,
        label='Этаж',
        widget=forms.NumberInput(attrs={
            'min': '1',
            'max': '50',
            'class': 'form-control',
            'placeholder': 'Любой этаж'
        })
    )

    bedrooms = forms.ChoiceField(
        required=False,
        label='Количество комнат',
        choices=BEDROOMS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    price_min = forms.DecimalField(
        required=False,
        label='Цена от (руб)',
        min_value=0,
        max_value=1000000000,
        widget=forms.NumberInput(attrs={
            'step': '100000',
            'class': 'form-control',
            'placeholder': 'Минимальная цена'
        })
    )

    price_max = forms.DecimalField(
        required=False,
        label='Цена до (руб)',
        min_value=0,
        max_value=1000000000,
        widget=forms.NumberInput(attrs={
            'step': '100000',
            'class': 'form-control',
            'placeholder': 'Максимальная цена'
        })
    )
