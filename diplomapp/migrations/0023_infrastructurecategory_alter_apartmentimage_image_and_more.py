# Generated by Django 5.1.7 on 2025-04-13 18:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diplomapp', '0022_remove_infrastructureitem_website'),
    ]

    operations = [
        migrations.CreateModel(
            name='InfrastructureCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('icon', models.CharField(help_text='Название иконки из Font Awesome', max_length=50)),
                ('order', models.PositiveIntegerField(default=0, help_text='Порядок отображения')),
            ],
            options={
                'verbose_name': 'Категория инфраструктуры',
                'verbose_name_plural': 'Категории инфраструктуры',
                'ordering': ['order'],
            },
        ),
        migrations.AlterField(
            model_name='apartmentimage',
            name='image',
            field=models.ImageField(upload_to='apartments/images/'),
        ),
        migrations.AddField(
            model_name='infrastructureitem',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='items', to='diplomapp.infrastructurecategory'),
        ),
    ]
