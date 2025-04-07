from django.shortcuts import render
from rest_framework import viewsets
from .models import Vendedor
from .serializers import VendedorSerializer

# Create your views here.

class VendedorViewSet(viewsets.ModelViewSet):
    queryset = Vendedor.objects.all()
    serializer_class = VendedorSerializer
