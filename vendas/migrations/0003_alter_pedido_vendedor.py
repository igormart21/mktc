# Generated by Django 5.1.7 on 2025-04-17 18:46

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendas', '0002_rename_data_criacao_pedido_data_pedido'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='pedido',
            name='vendedor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pedidos_como_vendedor', to=settings.AUTH_USER_MODEL),
        ),
    ]
