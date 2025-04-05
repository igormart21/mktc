import os
import django
import random
from datetime import datetime, timedelta

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from produtos.models import Produto
from vendas.models import Venda

Usuario = get_user_model()

def criar_vendas():
    # Obter todos os usuários e produtos
    usuarios = list(Usuario.objects.all())
    produtos = list(Produto.objects.all())
    
    if not usuarios or not produtos:
        print("Erro: Não há usuários ou produtos cadastrados no banco de dados.")
        return
    
    # Criar 20 vendas aleatórias
    for _ in range(20):
        comprador = random.choice(usuarios)
        produto = random.choice(produtos)
        vendedor = produto.vendedor
        
        # Garantir que o comprador não seja o vendedor
        while comprador == vendedor:
            comprador = random.choice(usuarios)
        
        # Criar a venda
        venda = Venda.objects.create(
            comprador=comprador,
            vendedor=vendedor,
            produto=produto,
            status=random.choice(['PENDENTE', 'ACEITO', 'REJEITADO', 'CANCELADO']),
            observacoes=f"Venda de teste {_ + 1}",
            data_criacao=datetime.now() - timedelta(days=random.randint(0, 30))
        )
        
        # Se a venda foi aceita, atualizar o estoque
        if venda.status == 'ACEITO':
            venda.estoque_atualizado = True
            venda.quantidade_atualizada = True
            venda.save()
        
        print(f"Venda criada: {venda}")

if __name__ == '__main__':
    print("Iniciando injeção de dados de vendas...")
    criar_vendas()
    print("Injeção de dados de vendas concluída!") 