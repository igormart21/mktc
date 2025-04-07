from core.models import Product
from vendedor.models import Vendedor

# Pega o primeiro vendedor
vendedor = Vendedor.objects.first()

# Cria o produto
produto = Product.objects.create(
    name='Feijão Carioca',
    description='Feijão de alta qualidade',
    price=10.50,
    available_volume=1000,
    unit='kg',
    product_type='feijao',
    seller=vendedor
)

print(f'Produto criado com sucesso! ID: {produto.id}') 