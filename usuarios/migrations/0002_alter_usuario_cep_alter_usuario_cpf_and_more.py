# Generated by Django 5.1.7 on 2025-04-06 03:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usuario',
            name='cep',
            field=models.CharField(blank=True, max_length=9, null=True, verbose_name='CEP'),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='cpf',
            field=models.CharField(blank=True, max_length=14, null=True, verbose_name='CPF'),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='email',
            field=models.EmailField(blank=True, max_length=255, null=True, unique=True, verbose_name='Email'),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to.', related_name='usuario_custom_set', related_query_name='usuario_custom', to='auth.group', verbose_name='groups'),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='hectares_atendidos',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Hectares Atendidos'),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='nome',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Nome'),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='numero',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Número'),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='rua',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Rua'),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='telefone',
            field=models.CharField(blank=True, max_length=15, null=True, verbose_name='Telefone'),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='usuario_custom_set', related_query_name='usuario_custom', to='auth.permission', verbose_name='user permissions'),
        ),
    ]
