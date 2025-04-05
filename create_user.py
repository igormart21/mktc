import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from usuarios.models import Usuario

User = get_user_model()

# Criar usuário
email = 'airmilesviagens@gmail.com'
password = 'Agro@2024#'

if not User.objects.filter(email=email).exists():
    user = User.objects.create_user(
        email=email,
        password=password,
        is_staff=True,
        is_superuser=True
    )
    print(f'Usuário criado com sucesso!\nEmail: {email}\nSenha: {password}')
else:
    print('Usuário já existe!') 