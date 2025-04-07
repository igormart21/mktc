from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Produto
from .serializers import ProdutoSerializer
from usuarios.permissions import IsVendedorAprovadoOrSuperAdmin
import logging
from django.db import connection

logger = logging.getLogger(__name__)

# Create your views here.

class ListaProdutosAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProdutoSerializer

    def get_queryset(self):
        queryset = Produto.objects.all()
        
        logger.info("="*50)
        logger.info("Iniciando get_queryset")
        logger.info(f"User: {self.request.user}")
        logger.info(f"User ID: {self.request.user.id}")
        logger.info(f"Is superuser: {self.request.user.is_superuser}")
        logger.info(f"Has vendedor: {hasattr(self.request.user, 'vendedor')}")
        
        # Se o usuário for um vendedor, mostrar apenas seus produtos
        if hasattr(self.request.user, 'vendedor'):
            logger.info(f"Vendedor ID: {self.request.user.vendedor.id}")
            logger.info(f"Vendedor nome_fantasia: {self.request.user.vendedor.nome_fantasia}")
            queryset = queryset.filter(vendedor=self.request.user.vendedor)
            logger.info(f"Produtos do vendedor: {queryset.count()}")
            
            # Log da query SQL
            logger.info("SQL Query:")
            logger.info(str(queryset.query))
            
            # Log dos produtos encontrados
            for produto in queryset:
                logger.info(f"Produto encontrado: {produto.id} - {produto.nome} - Vendedor: {produto.vendedor_id}")
        # Se for superadmin, mostrar todos os produtos
        elif self.request.user.is_superuser:
            queryset = queryset.all()
            logger.info(f"Total de produtos: {queryset.count()}")
        # Se não for nenhum dos dois, não mostrar nada
        else:
            logger.warning("Usuário não é vendedor nem superadmin")
            queryset = queryset.none()
        
        # Filtros
        categoria = self.request.query_params.get('category', None)
        status = self.request.query_params.get('status', None)
        search = self.request.query_params.get('search', None)
        
        if categoria:
            logger.info(f"Filtrando por categoria: {categoria}")
            queryset = queryset.filter(categoria=categoria)
        
        if status:
            logger.info(f"Filtrando por status: {status}")
            if status == 'active':
                queryset = queryset.filter(ativo=True)
            elif status == 'inactive':
                queryset = queryset.filter(ativo=False)
        
        if search:
            logger.info(f"Filtrando por busca: {search}")
            queryset = queryset.filter(nome__icontains=search)
        
        logger.info(f"Queryset final: {queryset.count()} produtos")
        
        # Log de todas as queries executadas
        logger.info("Queries executadas:")
        for query in connection.queries:
            logger.info(f"Query: {query['sql']}")
            logger.info(f"Tempo: {query['time']}")
        
        logger.info("="*50)
        return queryset.order_by('-created_at')

class ProdutoListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsVendedorAprovadoOrSuperAdmin]
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer

    def perform_create(self, serializer):
        if self.request.user.is_superuser:
            serializer.save()
        else:
            serializer.save(vendedor=self.request.user.vendedor)

class ProdutoRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsVendedorAprovadoOrSuperAdmin]
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer

@api_view(['POST'])
@permission_classes([IsVendedorAprovadoOrSuperAdmin])
def toggle_product_status(request, pk):
    try:
        produto = Produto.objects.get(pk=pk)
        produto.ativo = not produto.ativo
        produto.save()
        return Response({
            'success': True,
            'ativo': produto.ativo
        })
    except Produto.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Produto não encontrado'
        }, status=404)
