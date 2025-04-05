from usuarios.models import Usuario

# Criar superusuário
Usuario.objects.create_superuser(
    email='admin@agromarketplace.com',
    password='admin123',
    nome='Administrador',
    cpf='12345678909',  # CPF válido de exemplo
    telefone='11999999999',
    cep='12345-678',
    rua='Rua Principal',
    numero='123',
    hectares_atendidos=100
) 