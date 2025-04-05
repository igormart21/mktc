from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Vendedor
from .serializers import VendedorSerializer, VendedorCreateSerializer
from usuarios.permissions import IsSuperAdmin

# Create your views here.

class VendedorListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Vendedor.objects.all()
    serializer_class = VendedorSerializer

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return VendedorCreateSerializer
        return VendedorSerializer

class VendedorRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Vendedor.objects.all()
    serializer_class = VendedorSerializer
