from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import TokenError
from django.core.exceptions import ObjectDoesNotExist
from .permissions import IsSuperAdmin, IsVendedorAprovado, IsAuthenticatedUser
from .serializers import (
    UsuarioSerializer,
    UsuarioCreateSerializer,
    UsuarioUpdateSerializer,
    PerfilUsuarioSerializer
)
from .models import Usuario
from vendedores.models import Vendedor
from vendedores.serializers import VendedorSerializer

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

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        try:
            print('Recebendo requisição de login:', request.data)
            
            if 'email' not in request.data or 'password' not in request.data:
                return Response({
                    'detail': 'Email e senha são obrigatórios'
                }, status=400)
            
            response = super().post(request, *args, **kwargs)
            print('Resposta do token:', response.data)
            
            if response.status_code == 200:
                try:
                    user = Usuario.objects.get(email=request.data['email'])
                    print('Usuário encontrado:', user.email)
                    
                    if not user.is_active:
                        return Response({
                            'detail': 'Usuário inativo'
                        }, status=401)
                    
                    user_data = {
                        'id': user.id,
                        'email': user.email,
                        'nome': user.nome,
                        'is_staff': user.is_staff,
                        'is_superuser': user.is_superuser,
                        'aprovado': user.aprovado
                    }
                    response.data['user'] = user_data
                    print('Dados do usuário adicionados à resposta')
                except ObjectDoesNotExist:
                    print('Usuário não encontrado:', request.data['email'])
                    return Response({
                        'detail': 'Usuário não encontrado'
                    }, status=404)
            return response
        except TokenError as e:
            print('Erro de token:', str(e))
            return Response({
                'detail': 'Credenciais inválidas'
            }, status=401)
        except Exception as e:
            print('Erro durante o login:', str(e))
            return Response({
                'detail': str(e)
            }, status=400)
