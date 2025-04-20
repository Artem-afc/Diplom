from django.contrib.auth.decorators import login_required
from .models import District, Building, Apartment, InterestRate, InfrastructureItem
from .forms import SubscriberForm, MortgageCalculatorForm, ApartmentForm, ApartmentSearchForm, \
    UserCreationFormWithFullName, LoginForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate, logout
from django.utils import timezone
from .models import Subscriber
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from .forms import SubscribeForm


def district_list(request):
    districts = District.objects.all()
    purchased_apartments = []
    login_error = None

    if request.user.is_authenticated:
        purchased_apartments = Apartment.objects.filter(user=request.user, is_sold=True)


    login_form = LoginForm(request=request, prefix='login')

    if request.method == 'POST' and 'login-submit' in request.POST:
        login_form = LoginForm(request=request, data=request.POST, prefix='login')
        if login_form.is_valid():
            user = login_form.get_user()
            login(request, user)
            return redirect('district_list')
        else:
            login_error = "Неверные учетные данные"

    return render(request, 'diplomapp/district_list.html', {

        'districts': districts,
        'purchased_apartments': purchased_apartments,
        'login_form': login_form,
        'login_error': login_error
    })


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            return render(request, 'diplomapp/login.html', {
                'error': 'Пожалуйста, заполните все поля'
            })

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('district_list')
        else:
            return render(request, 'diplomapp/login.html', {
                'error': 'Неверное имя пользователя или пароль'
            })

    return render(request, 'diplomapp/login.html')


def user_register(request):
    if request.method == 'POST':
        form = UserCreationFormWithFullName(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('district_list')
    else:
        form = UserCreationFormWithFullName()

    return render(request, 'diplomapp/register.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('district_list')


def apartment_detail(request, pk):
    apartment = get_object_or_404(Apartment, pk=pk)
    form = MortgageCalculatorForm()
    result = error_message = None

    if request.method == 'POST':
        if 'buy' in request.POST:
            if not request.user.is_authenticated:
                return redirect('login')
            apartment.user = request.user
            apartment.is_sold = True
            apartment.sold_date = timezone.now().date()
            apartment.save()
            return redirect('purchase_success', apartment_pk=apartment.pk)
        elif 'calculate' in request.POST:
            # Калькулятор доступен всем
            result, error_message = mortgage_calculator(request, apartment.price)

    return render(request, 'diplomapp/apartment_detail.html', {
        'apartment': apartment,
        'form': form,
        'result': result,
        'error_message': error_message
    })


@login_required
def purchase_confirmation(request, pk):
    apartment = get_object_or_404(Apartment, pk=pk)

    if request.method == 'POST':
        apartment.user = request.user
        apartment.is_sold = True
        apartment.sold_date = timezone.now().date()
        apartment.save()
        return redirect('purchase_success', apartment_pk=apartment.pk)

    return render(request, 'diplomapp/purchase_confirm.html', {'apartment': apartment})


def purchase_success(request, apartment_pk):
    apartment = get_object_or_404(Apartment, pk=apartment_pk)
    return render(request, 'diplomapp/purchase_success.html', {'apartment': apartment})

def purchase_success(request, apartment_pk):
    apartment = get_object_or_404(Apartment, pk=apartment_pk)
    return render(request, 'diplomapp/purchase_success.html', {'apartment': apartment})


def district_detail(request, pk):
    district = get_object_or_404(District, pk=pk)
    buildings = Building.objects.filter(district=district)
    return render(request, 'diplomapp/district_detail.html', {
        'district': district,
        'buildings': buildings
    })


def building_detail(request, pk):
    building = get_object_or_404(Building, pk=pk)
    apartments = Apartment.objects.filter(building=building)
    form = ApartmentSearchForm(request.GET)
    search_params = {}

    if form.is_valid():
        if floor := form.cleaned_data.get('floor'):
            apartments = apartments.filter(floor=floor)
            search_params['floor'] = floor
        if bedrooms := form.cleaned_data.get('bedrooms'):
            apartments = apartments.filter(bedrooms=bedrooms)
            search_params['bedrooms'] = bedrooms
        if price_min := form.cleaned_data.get('price_min'):
            apartments = apartments.filter(price__gte=price_min)
            search_params['price_min'] = price_min
        if price_max := form.cleaned_data.get('price_max'):
            apartments = apartments.filter(price__lte=price_max)
            search_params['price_max'] = price_max
        if finishing := form.cleaned_data.get('finishing'):
            apartments = apartments.filter(description__icontains=finishing)
            search_params['finishing'] = finishing

    return render(request, 'diplomapp/building_detail.html', {
        'building': building,
        'form': form,
        'apartments': apartments,
        'search_params': search_params
    })


def mortgage_calculator(request, price):
    form = MortgageCalculatorForm(request.POST)
    if not form.is_valid():
        return None,
    try:
        calculator_type = form.cleaned_data['calculator_type']
        down_payment = form.cleaned_data['down_payment']
        loan_term = form.cleaned_data['loan_term']

        if down_payment > price:
            raise ValidationError("Первоначальный взнос не может быть больше цены")
        if loan_term <= 0:
            raise ValidationError("Срок кредита должен быть больше 0")

        interest_rate = InterestRate.objects.get(calculator_type=calculator_type).rate
        if interest_rate < 0:
            raise ValidationError("Процентная ставка не может быть отрицательной")

        loan_amount = price - down_payment
        monthly_rate = (interest_rate / 100) / 12
        payments = loan_term * 12

        if monthly_rate == 0:
            monthly_payment = loan_amount / payments
        else:
            monthly_payment = (loan_amount * monthly_rate * (1 + monthly_rate) ** payments) / \
                              ((1 + monthly_rate) ** payments - 1)

        return {
            'monthly_payment': round(monthly_payment, 2),
            'total_payment': round(monthly_payment * payments, 2),
            'overpayment': round(monthly_payment * payments - loan_amount, 2),
            'interest_rate': interest_rate
        }, None

    except ValidationError as e:
        return None, str(e)
    except Exception:
        return None, "Ошибка при расчете"


def subscribe(request):
    if request.method == 'POST':
        form = SubscribeForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            send_mail(
                'Вы подписаны на рассылку',
                'Спасибо за подписку! Вы будете получать наши новости.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            return render(request, 'subscribe_success.html')

    else:
        form = SubscribeForm()

    return render(request, 'subscribe.html', {'form': form})

def clean_email(self):
    email = self.cleaned_data['email'].lower()

    try:
        validate_email(email)
    except ValidationError:
        raise ValidationError("Введите корректный email адрес")

    if Subscriber.objects.filter(email__iexact=email).exists():
        raise ValidationError("Этот email уже подписан на рассылку")

    return email

def subscribe_success(request):
    return render(request, 'diplomapp/subscribe_success.html')

def apartment_search(request):
    form = ApartmentSearchForm(request.GET)
    apartments = Apartment.objects.all()

    if form.is_valid():
        if floor := form.cleaned_data.get('floor'):
            apartments = apartments.filter(floor=floor)
        if bedrooms := form.cleaned_data.get('bedrooms'):
            apartments = apartments.filter(bedrooms=bedrooms)
        if price_min := form.cleaned_data.get('price_min'):
            apartments = apartments.filter(price__gte=price_min)
        if price_max := form.cleaned_data.get('price_max'):
            apartments = apartments.filter(price__lte=price_max)
        if finishing := form.cleaned_data.get('finishing'):
            apartments = apartments.filter(description__icontains=finishing)

    return render(request, 'diplomapp/apartment_search.html', {
        'form': form,
        'apartments': apartments
    })


@login_required
def resell_apartment(request, pk):
    apartment = get_object_or_404(Apartment, pk=pk)
    if apartment.user == request.user:
        apartment.user = None
        apartment.is_sold = False
        apartment.sold_date = None
        apartment.save()
    return redirect('diplomapp/apartment_detail', pk=pk)


def trade_in_view(request):
    return render(request, 'diplomapp/trade_in.html')


def infrastructure(request):
    items = InfrastructureItem.objects.all()
    items_by_type = {}

    for item in items:
        if item.type not in items_by_type:
            items_by_type[item.type] = []
        items_by_type[item.type].append(item)

    return render(request, 'infrastructure/infrastructure.html', {
        'items_by_type': items_by_type,
        'title': 'Инфраструктура района'
    })