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

# Criar vendedor se não existir
if not Vendedor.objects.filter(usuario=user).exists():
    vendedor = Vendedor.objects.create(
        usuario=user,
        razao_social='Air Miles Viagens',
        nome_fantasia='Air Miles',
        cnpj='12345678901234',  # Substitua por um CNPJ válido
        inscricao_estadual='123456789',
        telefone='11999999999',
        endereco='Rua Exemplo, 123',
        cidade='São Paulo',
        estado='SP',
        cep='12345678',
        hectares_atendidos=100.00
    )
    print('Vendedor criado com sucesso!')
else:
    print('Vendedor já existe!') 