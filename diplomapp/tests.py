from django.core import mail
from django.urls import reverse
from django.test import TestCase
from django.contrib.auth.models import User
from .models import InterestRate, Apartment, Building, District


class SubscribeTest(TestCase):
    def test_subscribe_sends_email(self):
        response = self.client.post(reverse('subscribe'), {'email': 'test@example.com'})

        self.assertRedirects(response, reverse('subscribe_success'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Вы подписаны на рассылку')
        self.assertEqual(mail.outbox[0].to, ['test@example.com'])

    def test_subscribe_invalid_email(self):
        response = self.client.post(reverse('subscribe'), {'email': 'invalid-email'})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'email', 'Введите корректный email адрес')


class MortgageCalculatorTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.rate = InterestRate.objects.create(calculator_type='Bank1', rate=7.5)

    def test_calculator_success(self):
        from .views import mortgage_calculator
        form_data = {
            'calculator_type': 'Bank1',
            'price': 1000000,
            'down_payment': 200000,
            'loan_term': 10
        }
        result, error = mortgage_calculator(form_data, 1000000)

        self.assertIsNone(error)
        self.assertAlmostEqual(result['monthly_payment'], 9289.59, delta=0.01)
        self.assertEqual(result['interest_rate'], 7.5)

    def test_calculator_invalid_data(self):
        from .views import mortgage_calculator
        form_data = {
            'calculator_type': 'Bank1',
            'price': 1000000,
            'down_payment': 2000000,  # Больше чем цена
            'loan_term': 10
        }
        result, error = mortgage_calculator(form_data, 1000000)

        self.assertIsNone(result)
        self.assertEqual(error, "Первоначальный взнос не может быть больше цены")


class ApartmentTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='12345')
        cls.district = District.objects.create(name='Test District')
        cls.building = Building.objects.create(district=cls.district, name='Test Building')
        cls.apartment = Apartment.objects.create(
            building=cls.building,
            price=1000000,
            is_sold=False
        )

    def test_buy_apartment_authenticated(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(
            reverse('apartment_detail', args=[self.apartment.pk]),
            {'buy': ''}
        )

        self.apartment.refresh_from_db()
        self.assertTrue(self.apartment.is_sold)
        self.assertEqual(self.apartment.user, self.user)
        self.assertRedirects(response, reverse('purchase_success', args=[self.apartment.pk]))

    def test_buy_apartment_unauthenticated(self):
        response = self.client.post(
            reverse('apartment_detail', args=[self.apartment.pk]),
            {'buy': ''}
        )
        self.assertRedirects(response,
                             reverse('login') + f'?next={reverse("apartment_detail", args=[self.apartment.pk])}')


class AuthTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_login_success(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': '12345'
        })
        self.assertRedirects(response, reverse('district_list'))

    def test_login_failure(self):
        response = self.client.post(reverse('login'), {
            'username': 'wronguser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Неверное имя пользователя или пароль")

    def test_logout(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('district_list'))


class PurchaseConfirmationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='buyer')
        self.district = District.objects.create(name="Test District")
        self.building = Building.objects.create(district=self.district, name="Test Building")
        self.apartment = Apartment.objects.create(
            building=self.building,
            price=2500000,
            is_sold=False
        )

    def test_purchase_confirmation(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('purchase_confirmation', args=[self.apartment.pk]))

        self.apartment.refresh_from_db()
        self.assertTrue(self.apartment.is_sold)
        self.assertEqual(self.apartment.user, self.user)
        self.assertRedirects(response, reverse('purchase_success', args=[self.apartment.pk]))