from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Produto
from .serializers import ProdutoSerializer
from usuarios.permissions import IsVendedorAprovadoOrSuperAdmin

# Create your views here.

class ListaProdutosAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer

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
