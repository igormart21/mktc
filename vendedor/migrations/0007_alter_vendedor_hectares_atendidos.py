# Generated by Django 5.1.7 on 2025-04-05 22:33

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendedor', '0006_alter_vendedor_hectares_atendidos'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendedor',
            name='hectares_atendidos',
            field=models.IntegerField(default=10, help_text='Quantidade de hectares atendidos pelo vendedor (entre 10 e 300)', validators=[django.core.validators.MinValueValidator(10, message='O mínimo de hectares é 10'), django.core.validators.MaxValueValidator(300, message='O máximo de hectares é 300')]),
        ),
    ]
