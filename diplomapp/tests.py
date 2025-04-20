from django.core import mail
from django.urls import reverse
from .models import InterestRate

def test_subscribe_email_sent(self):
        data = {'email': 'test@example.com'}
        self.client.post(reverse('subscribe'), data)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Вы подписаны на рассылку')

def test_mortgage_calculator(self):
        InterestRate.objects.create(calculator_type='Banc1', rate=7.5)
        form_data = {
            'calculator_type': 'Banc1',
            'price': 1000000,
            'down_payment': 200000,
            'loan_term': 10
        }

        from diplom.diplomapp.views import mortgage_calculator
        result, error = mortgage_calculator(form_data, 1000000)
        self.assertIsNone(error)
        self.assertIn('monthly_payment', result)
