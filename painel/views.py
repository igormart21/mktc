from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.db.models import Sum, Count
from usuarios.models import Usuario
from vendedor.models import Vendedor
from produtos.models import Produto
from vendas.models import Venda

# Create your views here.

class DashboardAdminAPIView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # Contagem total de usuários
        total_usuarios = Usuario.objects.count()
        
        # Contagem de vendedores aprovados
        total_vendedores_aprovados = Vendedor.objects.filter(status_aprovacao='aprovado').count()
        
        # Contagem total de produtos
        total_produtos = Produto.objects.count()
        
        # Contagem total de vendas
        total_vendas = Venda.objects.count()
        
        # Lucro estimado (soma do valor total de todas as vendas)
        lucro_estimado = Venda.objects.aggregate(total=Sum('valor_total'))['total'] or 0
        
        return Response({
            "total_usuarios": total_usuarios,
            "total_vendedores_aprovados": total_vendedores_aprovados,
            "total_produtos": total_produtos,
            "total_vendas": total_vendas,
            "lucro_estimado": float(lucro_estimado)
        })
