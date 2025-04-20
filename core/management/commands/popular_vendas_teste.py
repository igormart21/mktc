from django.core.management.base import BaseCommand
from vendas.models import Venda
from vendedor.models import Vendedor
from produtos.models import Produto
from django.utils import timezone
from usuarios.models import Usuario
import random

class Command(BaseCommand):
    help = 'Popula o banco com vendas de teste para compradores que são vendedores.'

    def handle(self, *args, **options):
        vendedores = Vendedor.objects.all()
        produtos = Produto.objects.all()
        if not vendedores.exists() or not produtos.exists():
            self.stdout.write(self.style.ERROR('É necessário ter pelo menos um vendedor e um produto no banco.'))
            return
        
        for vendedor in vendedores:
            comprador = vendedor.usuario
            produto = random.choice(produtos)
            if not produto.vendedor:
                self.stdout.write(self.style.WARNING(f'Produto {produto} não possui vendedor. Pulando.'))
                continue
            venda = Venda.objects.create(
                comprador=comprador,
                vendedor=produto.vendedor.usuario,  # CORRIGIDO: agora é Usuario
                produto=produto,
                quantidade=5,
                preco_unitario=produto.preco,
                preco_total=produto.preco * 5,
                status='ACEITO',
                data_venda=timezone.now(),
                estoque_atualizado=True
            )
            self.stdout.write(self.style.SUCCESS(f'Criada venda de teste para comprador {comprador.email}'))
        self.stdout.write(self.style.SUCCESS('Vendas de teste criadas com sucesso!')) 