from django import forms
from django.contrib.auth.models import User
from .models import Apartment, Subscriber
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from .models import Subscriber
from socket import timeout
from smtplib import SMTPException


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        prefix = kwargs.pop('prefix', None)
        super().__init__(*args, **kwargs)

        if prefix:
            self.prefix = prefix

        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Ваш логин'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Ваш пароль'
        })


class UserCreationFormWithFullName(UserCreationForm):
    first_name = forms.CharField(
        label='Имя',
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    last_name = forms.CharField(
        label='Фамилия',
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        prefix = kwargs.pop('prefix', None)
        super().__init__(*args, **kwargs)
        if prefix:
            self.prefix = prefix

        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise ValidationError("Пользователь с таким именем уже существует")
        return username


class MortgageCalculatorForm(forms.Form):
    CALCULATOR_CHOICES = [
        ('Banc1', 'Банк не обманывает'),
        ('Banc2', 'Банк может обманывать'),
        ('Banc3', 'Банк точно обманывает'),
        ('Banc4', 'Банк точно не обманывает'),
    ]
    calculator_type = forms.ChoiceField(
        choices=CALCULATOR_CHOICES,
        label="Тип калькулятора",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    price = forms.DecimalField(
        label="Стоимость квартиры (руб)",
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    down_payment = forms.DecimalField(
        label="Первоначальный взнос (руб)",
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    loan_term = forms.IntegerField(
        label="Срок кредита (лет)",
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )


class SubscribeForm(forms.ModelForm):
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
        email = self.cleaned_data['email'].lower()

        if Subscriber.objects.filter(email__iexact=email).exists():
            raise ValidationError("Этот email уже подписан")

        return email

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.name = "Подписчик"

        if commit:
            instance.save()
            self.send_confirmation_email(instance.email)

        return instance

def send_confirmation_email(self, email):
    try:
        send_mail(
        'Вы подписаны на рассылку',
        'Спасибо за подписку!',
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
        timeout=10
        )
    except timeout:
        raise ValidationError("Превышено время ожидания отправки письма")
    except SMTPException as e:
        raise ValidationError(f"Ошибка отправки письма: {str(e)}")
    except Exception as e:
        raise ValidationError("Не удалось отправить письмо подтверждения")

def send_confirmation_email(self, email):
    send_mail(
        'Вы подписаны на рассылку',
        'Спасибо за подписку! Теперь вы будете получать наши новости.',
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )

class ApartmentForm(forms.ModelForm):
    class Meta:
        model = Apartment
        fields = ['building', 'price', 'bedrooms', 'square_footage', 'description', 'image', 'is_sold', 'floor']
        widgets = {
            'building': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'bedrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'square_footage': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'floor': forms.NumberInput(attrs={'class': 'form-control'}),
        }


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


class SubscriberForm:
    pass