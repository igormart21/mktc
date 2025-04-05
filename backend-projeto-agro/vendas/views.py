from django.shortcuts import render
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Venda
from .serializers import VendaSerializer
from .permissions import IsComprador, IsVendedorAprovado
from vendedores.models import Vendedor

# Create your views here.

class VendaViewSet(viewsets.ModelViewSet):
    serializer_class = VendaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        action = self.action

        if action == 'minhas_vendas':
            return Venda.objects.filter(comprador=user)
        elif action == 'vendas_recebidas':
            try:
                vendedor = Vendedor.objects.get(usuario=user)
                return Venda.objects.filter(produto__vendedor=vendedor.usuario)
            except Vendedor.DoesNotExist:
                return Venda.objects.none()
        else:
            return Venda.objects.none()

    def get_permissions(self):
        if self.action == 'create':
            return [IsComprador()]
        elif self.action == 'vendas_recebidas':
            return [IsVendedorAprovado()]
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def minhas_vendas(self, request):
        vendas = self.get_queryset()
        serializer = self.get_serializer(vendas, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def vendas_recebidas(self, request):
        print(f"Usuário autenticado: {request.user.is_authenticated}")
        print(f"ID do usuário: {request.user.id}")
        print(f"Email do usuário: {request.user.email}")
        
        try:
            vendedor = Vendedor.objects.get(usuario=request.user)
            print(f"Vendedor encontrado: {vendedor}")
            vendas = Venda.objects.filter(produto__vendedor=vendedor.usuario)
            print(f"Total de vendas encontradas: {vendas.count()}")
            serializer = self.get_serializer(vendas, many=True)
            return Response(serializer.data)
        except Vendedor.DoesNotExist:
            print(f"Usuário {request.user} não é um vendedor")
            return Response([], status=200)

    @action(detail=True, methods=['patch'])
    def atualizar_status(self, request, pk=None):
        venda = self.get_object()
        novo_status = request.data.get('status')
        
        if not novo_status:
            return Response(
                {'error': 'Status não fornecido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        if novo_status not in ['confirmado', 'cancelado']:
            return Response(
                {'error': 'Status inválido'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Verifica se o usuário é o vendedor do produto
        try:
            vendedor = Vendedor.objects.get(usuario=request.user)
            if venda.produto.vendedor != vendedor:
                return Response(
                    {'error': 'Você não tem permissão para atualizar esta venda'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
        except Vendedor.DoesNotExist:
            return Response(
                {'error': 'Você não é um vendedor'}, 
                status=status.HTTP_403_FORBIDDEN
            )
            
        venda.status = novo_status
        venda.save()
        
        serializer = self.get_serializer(venda)
        return Response(serializer.data)

class ListaVendasAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Venda.objects.all()
    serializer_class = VendaSerializer

class VendaListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsComprador]
    queryset = Venda.objects.all()
    serializer_class = VendaSerializer

    def perform_create(self, serializer):
        serializer.save(comprador=self.request.user)

class VendaRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsVendedorAprovado]
    queryset = Venda.objects.all()
    serializer_class = VendaSerializer
