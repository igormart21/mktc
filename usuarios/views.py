from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, viewsets, status
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .permissions import IsSuperAdmin, IsVendedorAprovado, IsAuthenticatedUser, IsOwnerOrAdmin
from .serializers import (
    UsuarioSerializer,
    UsuarioCreateSerializer,
    UsuarioUpdateSerializer,
    PerfilUsuarioSerializer
)
from .models import Usuario
from vendedor.models import Vendedor
from vendedor.serializers import VendedorSerializer

# Create your views here.

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def teste_autenticacao(request):
    return Response({
        'mensagem': 'Você está autenticado!',
        'usuario': request.user.email
    })

@api_view(['GET'])
@permission_classes([IsSuperAdmin])
def area_admin(request):
    return Response({
        'mensagem': 'Bem-vindo à área administrativa!',
        'usuario': request.user.email
    })

@api_view(['GET'])
@permission_classes([IsVendedorAprovado])
def area_vendedor(request):
    return Response({
        'mensagem': 'Bem-vindo à área do vendedor!',
        'usuario': request.user.email
    })

@api_view(['GET'])
@permission_classes([IsAuthenticatedUser])
def area_usuario(request):
    return Response({
        'mensagem': 'Bem-vindo à sua área!',
        'usuario': request.user.email
    })

class PerfilUsuarioAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = PerfilUsuarioSerializer(request.user)
        return Response(serializer.data)

class ListaUsuariosAPIView(generics.ListAPIView):
    permission_classes = [IsSuperAdmin]
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

class ListaVendedoresAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Vendedor.objects.all()
    serializer_class = VendedorSerializer

class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        return Response({
            "mensagem": "Logout realizado com sucesso."
        }, status=200)
