from django.core.management.base import BaseCommand
from django.db import transaction
from vendas.models import Venda
from produtos.models import Produto
from django.db.models import Sum

class Command(BaseCommand):
    help = 'Verifica a integridade dos dados do sistema'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando verificação de integridade...')
        
        # Verificar vendas
        vendas_problemas = []
        for venda in Venda.objects.all():
            try:
                with transaction.atomic():
                    # Verificar se o produto ainda existe
                    if not venda.produto:
                        vendas_problemas.append(f'Venda {venda.id}: Produto não encontrado')
                        continue
                    
                    # Verificar se o estoque está consistente
                    if venda.status == 'ACEITO' and not venda.estoque_atualizado:
                        vendas_problemas.append(f'Venda {venda.id}: Estoque não atualizado')
                    
                    # Verificar se aprovado_por está preenchido quando necessário
                    if venda.status == 'ACEITO' and not venda.aprovado_por:
                        vendas_problemas.append(f'Venda {venda.id}: Aprovador não definido')
            except Exception as e:
                vendas_problemas.append(f'Venda {venda.id}: Erro ao verificar - {str(e)}')

        # Verificar produtos
        produtos_problemas = []
        for produto in Produto.objects.all():
            try:
                # Verificar se o estoque está consistente com as vendas
                vendas_aceitas = Venda.objects.filter(
                    produto=produto,
                    status='ACEITO'
                ).count()
                
                if produto.estoque < 0:
                    produtos_problemas.append(f'Produto {produto.id}: Estoque negativo')
                elif produto.estoque != (produto.estoque_inicial - vendas_aceitas):
                    produtos_problemas.append(f'Produto {produto.id}: Estoque inconsistente')
            except Exception as e:
                produtos_problemas.append(f'Produto {produto.id}: Erro ao verificar - {str(e)}')

        # Exibir resultados
        if vendas_problemas:
            self.stdout.write(self.style.WARNING('\nProblemas encontrados em vendas:'))
            for problema in vendas_problemas:
                self.stdout.write(f'- {problema}')
        
        if produtos_problemas:
            self.stdout.write(self.style.WARNING('\nProblemas encontrados em produtos:'))
            for problema in produtos_problemas:
                self.stdout.write(f'- {problema}')
        
        if not vendas_problemas and not produtos_problemas:
            self.stdout.write(self.style.SUCCESS('\nNenhum problema encontrado!')) 