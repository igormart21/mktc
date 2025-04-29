from django.contrib.auth import get_user_model
from core.models import Pedido, ItemPedido, Produto
from vendedor.models import Vendedor
from decimal import Decimal

# Criar usuário comprador
Usuario = get_user_model()
comprador = Usuario.objects.create(
    email='comprador@teste.com',
    nome='Comprador',
    sobrenome='Teste',
    is_active=True
)
comprador.set_password('123456')
comprador.save()

# Criar usuário vendedor
vendedor = Usuario.objects.create(
    email='vendedor@teste.com',
    nome='Vendedor',
    sobrenome='Teste',
    is_active=True
)
vendedor.set_password('123456')
vendedor.save()

# Criar vendedor
vendedor_obj = Vendedor.objects.create(
    usuario=vendedor,
    nome_fantasia='Vendedor Teste',
    telefone='(11) 99999-9999',
    endereco='Rua Teste, 123',
    cidade='São Paulo',
    estado='SP',
    cep='01234-567'
)

# Criar produto
produto = Produto.objects.create(
    nome='Produto Teste',
    categoria='SEMENTE',
    descricao='Produto de teste para verificação',
    preco=Decimal('100.00'),
    volume_disponivel=Decimal('1000.00'),
    unidade_medida='kg',
    tipo='soja',
    embalagem='Saco',
    fabricante='Teste',
    lote='TESTE001',
    quantidade_minima=Decimal('10.00'),
    ativo=True
)

# Criar pedido
pedido = Pedido.objects.create(
    comprador=comprador,
    vendedor=vendedor,
    nome_propriedade='Fazenda Teste',
    cnpj='12.345.678/0001-90',
    hectares=Decimal('100.00'),
    cultivo_principal='soja',
    estado='SP',
    cidade='São Paulo',
    endereco='Rua Teste, 123',
    cep='01234-567',
    status='PENDENTE',
    tipo_venda='avista',
    total=Decimal('1000.00')
)

# Criar item do pedido
ItemPedido.objects.create(
    pedido=pedido,
    produto=produto,
    quantidade=10,
    preco_unitario=Decimal('100.00'),
    total=Decimal('1000.00')
)

print("Pedido de teste criado com sucesso!")
print(f"ID do Pedido: {pedido.id}")
print(f"Comprador: {comprador.email}")
print(f"Vendedor: {vendedor.email}")
print(f"Produto: {produto.nome}")
print(f"Status: {pedido.status}") 