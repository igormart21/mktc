import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from vendedor.models import Vendedor

User = get_user_model()

# Buscar o usuário
email = 'airmilesviagens@gmail.com'
user = User.objects.get(email=email)

print(f'\nInformações do Usuário:')
print(f'Email: {user.email}')
print(f'Nome: {user.nome}')
print(f'É staff: {user.is_staff}')
print(f'É superuser: {user.is_superuser}')

# Verificar se tem vendedor associado
try:
    vendedor = user.vendedor
    print(f'\nInformações do Vendedor:')
    print(f'Nome Fantasia: {vendedor.nome_fantasia}')
    print(f'Razão Social: {vendedor.razao_social}')
    print(f'CNPJ: {vendedor.cnpj}')
except Vendedor.DoesNotExist:
    print('\nUsuário não tem vendedor associado!')
except Exception as e:
    print(f'\nErro ao verificar vendedor: {str(e)}') 