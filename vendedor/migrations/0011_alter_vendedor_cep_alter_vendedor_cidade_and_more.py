# Generated by Django 5.1.7 on 2025-04-12 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vendedor', '0010_auto_20250406_2208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vendedor',
            name='cep',
            field=models.CharField(default='00000-000', max_length=9),
        ),
        migrations.AlterField(
            model_name='vendedor',
            name='cidade',
            field=models.CharField(default='Cidade não informada', max_length=100),
        ),
        migrations.AlterField(
            model_name='vendedor',
            name='endereco',
            field=models.CharField(default='Endereço não informado', max_length=200),
        ),
        migrations.AlterField(
            model_name='vendedor',
            name='estado',
            field=models.CharField(default='SP', max_length=2),
        ),
        migrations.AlterField(
            model_name='vendedor',
            name='nome_fantasia',
            field=models.CharField(default='Sem nome fantasia', max_length=200),
        ),
        migrations.AlterField(
            model_name='vendedor',
            name='telefone',
            field=models.CharField(default='(00) 00000-0000', max_length=20),
        ),
    ]
