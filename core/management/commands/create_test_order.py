from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Pedido, ItemPedido, Produto
from vendedor.models import Vendedor
from decimal import Decimal

class Command(BaseCommand):
    help = 'Cria um pedido de teste para demonstração'

    def handle(self, *args, **kwargs):
        # Obter usuários existentes
        Usuario = get_user_model()
        comprador = Usuario.objects.get(email='comprador@teste.com')
        vendedor = Usuario.objects.get(email='vendedor@teste.com')
        vendedor_obj = Vendedor.objects.get(usuario=vendedor)

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
            status='PENDENTE',  # Status em maiúsculas
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

        self.stdout.write(self.style.SUCCESS('Pedido de teste criado com sucesso!'))
        self.stdout.write(f'ID do Pedido: {pedido.id}')
        self.stdout.write(f'Comprador: {comprador.email}')
        self.stdout.write(f'Vendedor: {vendedor.email}')
        self.stdout.write(f'Produto: {produto.nome}')
        self.stdout.write(f'Status: {pedido.status}') 