import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from core.models import Product
from produtos.models import Produto

def sync_products():
    print("Iniciando sincronização de produtos...")
    
    # Buscar todos os produtos do core
    core_products = Product.objects.all()
    total = core_products.count()
    print(f"Total de produtos no core: {total}")
    
    # Para cada produto do core
    for i, core_product in enumerate(core_products, 1):
        print(f"Processando produto {i}/{total}: {core_product.name}")
        
        # Verificar se já existe um produto correspondente
        produto = Produto.objects.filter(core_product_id=core_product.id).first()
        
        if produto:
            # Atualizar dados do produto existente
            produto.nome = core_product.name
            produto.categoria = core_product.product_type
            produto.descricao = core_product.description
            produto.preco = core_product.price
            produto.moeda = core_product.currency
            produto.volume_disponivel = core_product.available_volume
            produto.unidade_medida = core_product.unit
            produto.tipo = core_product.product_type
            produto.embalagem = core_product.packaging
            produto.fabricante = core_product.manufacturer
            produto.lote = core_product.lot
            produto.validade = core_product.expiration_date
            produto.quantidade_minima = core_product.minimum_quantity
            produto.peneira = core_product.sieve
            produto.variedade = core_product.variety
            produto.ativo = core_product.is_active
            produto.save()
            print(f"Produto atualizado: {produto.nome}")
        else:
            # Criar novo produto
            produto = Produto.objects.create(
                core_product_id=core_product.id,
                nome=core_product.name,
                categoria=core_product.product_type,
                descricao=core_product.description,
                preco=core_product.price,
                moeda=core_product.currency,
                volume_disponivel=core_product.available_volume,
                unidade_medida=core_product.unit,
                tipo=core_product.product_type,
                embalagem=core_product.packaging,
                fabricante=core_product.manufacturer,
                lote=core_product.lot,
                validade=core_product.expiration_date,
                quantidade_minima=core_product.minimum_quantity,
                peneira=core_product.sieve,
                variedade=core_product.variety,
                ativo=core_product.is_active
            )
            print(f"Novo produto criado: {produto.nome}")
    
    print("Sincronização concluída!")

if __name__ == '__main__':
    sync_products() 