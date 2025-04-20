from django.core.management.base import BaseCommand
from core.models import Pedido, Usuario, Vendedor
from produtos.models import Produto
from django.utils import timezone
import random

class Command(BaseCommand):
    help = 'Popula o banco com pedidos de teste para o modelo Pedido do app core.'

    def handle(self, *args, **options):
        vendedores = Vendedor.objects.all()
        produtos = Produto.objects.all()
        if not vendedores.exists() or not produtos.exists():
            self.stdout.write(self.style.ERROR('É necessário ter pelo menos um vendedor e um produto no banco.'))
            return
        
        for vendedor in vendedores:
            # Buscar o usuario pelo id no modelo core.models.Usuario
            comprador_id = vendedor.usuario.id
            try:
                comprador = Usuario.objects.get(id=comprador_id)
            except Usuario.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Usuário {vendedor.usuario} não encontrado em core.models.Usuario. Pulando.'))
                continue
            produto = random.choice(produtos)
            if not produto.vendedor:
                self.stdout.write(self.style.WARNING(f'Produto {produto} não possui vendedor. Pulando.'))
                continue
            vendedor_produto_id = produto.vendedor.usuario.id
            try:
                vendedor_usuario = Usuario.objects.get(id=vendedor_produto_id)
            except Usuario.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Vendedor do produto {produto} não encontrado em core.models.Usuario. Pulando.'))
                continue
            pedido = Pedido.objects.create(
                comprador=comprador,
                vendedor=vendedor_usuario,
                nome_propriedade=f'Fazenda {comprador.nome}',
                cnpj='12345678000199',
                hectares=50,
                cultivo_principal='soja',
                estado='SP',
                cidade='São Paulo',
                endereco='Rua Teste, 123',
                cep='01000-000',
                referencia='Próximo ao mercado',
                observacoes='Pedido de teste',
                status='PENDENTE',
                data_criacao=timezone.now(),
                data_atualizacao=timezone.now(),
                tipo_venda='avista',
                total=produto.preco * 10,
                produto=produto,
                quantidade=10,
                preco_unitario=produto.preco
            )
            self.stdout.write(self.style.SUCCESS(f'Criado pedido de teste para comprador {comprador.email}'))
        self.stdout.write(self.style.SUCCESS('Pedidos de teste criados com sucesso!')) 