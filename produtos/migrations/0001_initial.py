# Generated by Django 5.1.7 on 2025-04-03 15:08

import django.core.validators
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Produto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=200)),
                ('descricao', models.TextField()),
                ('preco', models.DecimalField(decimal_places=2, max_digits=10, validators=[django.core.validators.MinValueValidator(0)])),
                ('quantidade', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('categoria', models.CharField(blank=True, choices=[('SEMENTES', 'Sementes'), ('FERTILIZANTES', 'Fertilizantes'), ('DEFENSIVOS', 'Defensivos'), ('MAQUINARIOS', 'Maquinários'), ('OUTROS', 'Outros')], default='OUTROS', max_length=100, null=True)),
                ('tipo', models.CharField(blank=True, choices=[('SOJA', 'Soja'), ('MILHO', 'Milho'), ('CAFE', 'Café'), ('OUTROS', 'Outros')], default='OUTROS', max_length=100, null=True)),
                ('peneira', models.CharField(blank=True, max_length=100, null=True)),
                ('variedade', models.CharField(blank=True, max_length=100, null=True)),
                ('lote', models.CharField(blank=True, max_length=100, null=True)),
                ('volume_disponivel', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True)),
                ('unidade_medida', models.CharField(blank=True, choices=[('KG', 'Quilograma'), ('TON', 'Tonelada'), ('L', 'Litro'), ('ML', 'Mililitro'), ('UN', 'Unidade')], default='UN', max_length=50, null=True)),
                ('embalagem', models.CharField(blank=True, max_length=100, null=True)),
                ('moeda', models.CharField(blank=True, choices=[('BRL', 'Real'), ('USD', 'Dólar')], default='BRL', max_length=10, null=True)),
                ('fabricante', models.CharField(blank=True, max_length=100, null=True)),
                ('quantidade_minima', models.IntegerField(blank=True, default=1, null=True)),
                ('validade', models.DateField(blank=True, default=django.utils.timezone.now, null=True)),
                ('permite_troca', models.BooleanField(blank=True, default=False, null=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Produto',
                'verbose_name_plural': 'Produtos',
                'ordering': ['-created_at'],
            },
        ),
    ]
