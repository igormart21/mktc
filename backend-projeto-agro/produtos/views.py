from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import Produto
from .serializers import ProdutoSerializer, ProdutoPublicoSerializer
from usuarios.permissions import IsVendedorAprovadoOrSuperAdmin
import logging

logger = logging.getLogger(__name__)

# Create your views here.

class ListaProdutosPublicosAPIView(generics.ListAPIView):
    permission_classes = [AllowAny]
    queryset = Produto.objects.all()
    serializer_class = ProdutoPublicoSerializer

    def list(self, request, *args, **kwargs):
        logger.info("Acessando lista de produtos públicos")
        queryset = self.get_queryset()
        logger.info(f"Total de produtos encontrados: {queryset.count()}")
        serializer = self.get_serializer(queryset, many=True)
        logger.info(f"Dados serializados: {serializer.data}")
        return Response(serializer.data)

class ListaProdutosAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer

class ProdutoListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsVendedorAprovadoOrSuperAdmin]
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer

    def perform_create(self, serializer):
        serializer.save(vendedor=self.request.user.vendedor)

class ProdutoRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsVendedorAprovadoOrSuperAdmin]
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer
