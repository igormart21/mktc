# Generated by Django 5.1.7 on 2025-04-03 15:08

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Email')),
                ('nome', models.CharField(max_length=255, verbose_name='Nome')),
                ('cpf', models.CharField(max_length=14, unique=True, verbose_name='CPF')),
                ('telefone', models.CharField(max_length=15, verbose_name='Telefone')),
                ('cep', models.CharField(max_length=9, verbose_name='CEP')),
                ('rua', models.CharField(max_length=255, verbose_name='Rua')),
                ('numero', models.CharField(max_length=20, verbose_name='Número')),
                ('complemento', models.CharField(blank=True, max_length=255, null=True, verbose_name='Complemento')),
                ('hectares_atendidos', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Hectares Atendidos')),
                ('tipo_documento', models.CharField(blank=True, choices=[('RG', 'RG'), ('CNH', 'CNH')], max_length=3, null=True, verbose_name='Tipo de Documento')),
                ('numero_documento', models.CharField(blank=True, max_length=20, null=True, verbose_name='Número do Documento')),
                ('documento', models.ImageField(blank=True, null=True, upload_to='documentos/', verbose_name='Documento')),
                ('uf_documento', models.CharField(blank=True, choices=[('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'), ('BA', 'Bahia'), ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'), ('GO', 'Goiás'), ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'), ('MG', 'Minas Gerais'), ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'), ('PE', 'Pernambuco'), ('PI', 'Piauí'), ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'), ('RS', 'Rio Grande do Sul'), ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'), ('SP', 'São Paulo'), ('SE', 'Sergipe'), ('TO', 'Tocantins')], max_length=2, null=True, verbose_name='UF do Documento')),
                ('orgao_emissor', models.CharField(blank=True, max_length=10, null=True, verbose_name='Órgão Emissor')),
                ('is_active', models.BooleanField(default=True, verbose_name='Ativo')),
                ('is_staff', models.BooleanField(default=False, verbose_name='Acesso ao Painel')),
                ('is_superuser', models.BooleanField(default=False, verbose_name='Superusuário')),
                ('aprovado', models.BooleanField(default=False, verbose_name='Aprovado')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Data de Cadastro')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to.', related_name='usuario_set', related_query_name='usuario', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='usuario_set', related_query_name='usuario', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Usuário',
                'verbose_name_plural': 'Usuários',
                'db_table': 'usuario',
            },
        ),
    ]
