import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from usuarios.models import Usuario
from vendedor.models import Vendedor

User = get_user_model()

# Buscar o usuário
email = 'airmilesviagens@gmail.com'
user = User.objects.filter(email=email).first()

if user:
    print(f'\nInformações do Usuário:')
    print(f'Email: {user.email}')
    print(f'É staff: {user.is_staff}')
    print(f'É superuser: {user.is_superuser}')
    
    # Verificar se é vendedor
    vendedor = Vendedor.objects.filter(usuario=user).first()
    if vendedor:
        print(f'\nInformações do Vendedor:')
        print(f'Nome: {vendedor.nome_fantasia or vendedor.razao_social}')
        print(f'Status: {vendedor.status}')
    else:
        print('\nUsuário não está associado a um vendedor!')
else:
    print('Usuário não encontrado!') 