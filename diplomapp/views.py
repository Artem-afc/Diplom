from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import District, Building, Apartment, InterestRate, InfrastructureItem
from .forms import SubscriberForm, MortgageCalculatorForm, ApartmentForm, ApartmentSearchForm, UserCreationFormWithFullName, LoginForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, authenticate
from django.core.exceptions import ValidationError
from django.utils import timezone
from django import forms


def apartment_detail(request, pk):
    apartment = get_object_or_404(Apartment, pk=pk)
    form = MortgageCalculatorForm()
    result = None
    error_message = None

    if request.method == 'POST':
        if 'buy' in request.POST:
            apartment.user = request.user
            apartment.is_sold = True
            apartment.sold_date = timezone.now().date()
            apartment.save()

            return render(request, 'diplomapp/apartment_detail.html', {
                'apartment': apartment,
                'form': form,
                'purchase_success': True,
                'result': result,
            })
        else:
            if request.POST.get('price'):
                result, error_message = mortgage_calculator(request, apartment.price)

    return render(request, 'diplomapp/apartment_detail.html', {
        'apartment': apartment,
        'form': form,
        'result': result,
        'error_message': error_message
    })


def district_list(request):
    districts = District.objects.all()
    return render(request, 'diplomapp/district_list.html', {'districts': districts})


def district_detail(request, pk):
    district = get_object_or_404(District, pk=pk)
    buildings = Building.objects.filter(district=district)
    return render(request, 'diplomapp/district_detail.html', {'district': district, 'buildings': buildings})


def building_detail(request, pk):
    building = get_object_or_404(Building, pk=pk)
    apartments = Apartment.objects.filter(building=building)
    form = ApartmentSearchForm(request.GET)
    search_params = {}

    if form.is_valid():
        floor = form.cleaned_data.get('floor')
        bedrooms = form.cleaned_data.get('bedrooms')
        price_min = form.cleaned_data.get('price_min')
        price_max = form.cleaned_data.get('price_max')
        finishing = form.cleaned_data.get('finishing')

        if floor:
            apartments = apartments.filter(floor=floor)
            search_params['floor'] = floor
        if bedrooms:
            apartments = apartments.filter(bedrooms=bedrooms)
            search_params['bedrooms'] = bedrooms
        if price_min:
            apartments = apartments.filter(price__gte=price_min)
            search_params['price_min'] = price_min
        if price_max:
            apartments = apartments.filter(price__lte=price_max)
            search_params['price_max'] = price_max
        if finishing:
            apartments = apartments.filter(description__icontains=finishing)
            search_params['finishing'] = finishing

    return render(request, 'diplomapp/building_detail.html', {'building': building, 'form': form, 'apartments': apartments, 'search_params': search_params})


def purchase_confirmation(request, pk):
    apartment = get_object_or_404(Apartment, pk=pk)
    if request.method == 'POST':
        form = UserCreationFormWithFullName(request.POST)
        if form.is_valid():
            user = form.save()
            apartment.user = user
            apartment.is_sold = True
            apartment.sold_date = timezone.now().date()
            apartment.save()
            login(request, user)
            return redirect('apartment_detail', pk=pk)
    else:
        form = UserCreationFormWithFullName()
    return render(request, 'diplomapp/purchase_confirmation.html', {'apartment': apartment, 'form': form})


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('district_list')
            else:
                return render(request, 'diplomapp/login.html', {'form': form, 'error_message': 'Неверные логин или пароль'})
        else:
            return render(request, 'diplomapp/login.html', {'form': form, 'error_message': 'Неверные логин или пароль'})
    else:
        form = LoginForm()
    return render(request, 'diplomapp/login.html', {'form': form})


def mortgage_calculator(request, price):
    result = None
    error_message = None
    form = MortgageCalculatorForm(request.POST)

    if form.is_valid():
        try:
            calculator_type = form.cleaned_data['calculator_type']
            down_payment = form.cleaned_data['down_payment']
            loan_term = form.cleaned_data['loan_term']

            if down_payment > int(price):
                raise ValidationError("Первоначальный взнос не может быть больше цены.")
            if loan_term <= 0:
                raise ValidationError("Срок кредита должен быть больше 0.")

            interest_rate = InterestRate.objects.get(calculator_type=calculator_type).rate

            if interest_rate < 0:
                raise ValidationError("Процентная ставка не может быть отрицательной.")

            loan_amount = int(price) - down_payment
            monthly_interest_rate = (interest_rate / 100) / 12
            number_of_payments = loan_term * 12

            if monthly_interest_rate == 0:
                monthly_payment = loan_amount / number_of_payments
            else:
                monthly_payment = (
                    loan_amount * monthly_interest_rate * (1 + monthly_interest_rate) ** number_of_payments
                ) / ((1 + monthly_interest_rate) ** number_of_payments - 1)

            total_payment = monthly_payment * number_of_payments
            overpayment = total_payment - loan_amount

            result = {
                'monthly_payment': round(monthly_payment, 2),
                'total_payment': round(total_payment, 2),
                'overpayment': round(overpayment, 2),
                'interest_rate': interest_rate,
            }
        except ValidationError as e:
            error_message = str(e)
        except Exception as e:
            error_message = "Произошла ошибка при расчете."
    return result, error_message


def subscribe(request):
    if request.method == 'POST':
        form = SubscriberForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('district_list')
    else:
        form = SubscriberForm()
    return render(request, 'diplomapp/subscribe.html', {'form': form})


def apartment_create(request):
    if request.method == 'POST':
        form = ApartmentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('apartment_list')
    else:
        form = ApartmentForm()
    return render(request, 'diplomapp/apartment_form.html', {'form': form})


def apartment_update(request, pk):
    apartment = get_object_or_404(Apartment, pk=pk)
    if request.method == 'POST':
        form = ApartmentForm(request.POST, request.FILES, instance=apartment)
        if form.is_valid():
            form.save()
            return redirect('apartment_list')
    else:
        form = ApartmentForm(instance=apartment)
    return render(request, 'diplomapp/apartment_form.html', {'form': form})


def apartment_search(request):
    form = ApartmentSearchForm(request.GET)
    apartments = Apartment.objects.all()

    if form.is_valid():
        floor = form.cleaned_data.get('floor')
        bedrooms = form.cleaned_data.get('bedrooms')
        price_min = form.cleaned_data.get('price_min')
        price_max = form.cleaned_data.get('price_max')
        finishing = form.cleaned_data.get('finishing')

        if floor:
            apartments = apartments.filter(floor=floor)
        if bedrooms:
            apartments = apartments.filter(bedrooms=bedrooms)
        if price_min:
            apartments = apartments.filter(price__gte=price_min)
        if price_max:
            apartments = apartments.filter(price__lte=price_max)
        if finishing:
            apartments = apartments.filter(description__icontains=finishing)

        print("Параметры поиска:", form.cleaned_data)
        print("Найденные квартиры:", apartments)

    return render(request, 'diplomapp/apartment_search.html', {'form': form, 'apartments': apartments})


def purchase_confirmation(request, pk):
    apartment = get_object_or_404(Apartment, pk=pk)
    apartment.user = request.user
    apartment.is_sold = True
    apartment.sold_date = timezone.now().date()
    apartment.save()
    return render(request, 'diplomapp/purchase_confirmation.html', {'apartment': apartment})


def resell_apartment(request, pk):
    apartment = get_object_or_404(Apartment, pk=pk)
    apartment.user = None
    apartment.is_sold = False
    apartment.sold_date = None
    apartment.save()
    return redirect('apartment_detail', pk=pk)


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