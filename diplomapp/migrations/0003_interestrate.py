# Generated by Django 5.1.7 on 2025-03-16 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diplomapp', '0002_apartmentimage'),
    ]

    operations = [
        migrations.CreateModel(
            name='InterestRate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('calculator_type', models.CharField(choices=[('standard', 'Стандартный калькулятор'), ('preferential', 'Льготный калькулятор'), ('business', 'Бизнес-калькулятор')], max_length=50, unique=True)),
                ('rate', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='Процентная ставка (%)')),
            ],
        ),
    ]
