from django.shortcuts import render
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import Venda
from .serializers import VendaSerializer
from .permissions import IsComprador, IsVendedorAprovado

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
            return Venda.objects.filter(vendedor=user)
        return Venda.objects.none()

    def get_permissions(self):
        if self.action == 'create':
            return [IsComprador()]
        elif self.action == 'vendas_recebidas':
            return [IsVendedorAprovado()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['get'])
    def minhas_vendas(self, request):
        vendas = self.get_queryset()
        serializer = self.get_serializer(vendas, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def vendas_recebidas(self, request):
        vendas = self.get_queryset()
        serializer = self.get_serializer(vendas, many=True)
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

class HistoricoVendasView(LoginRequiredMixin, ListView):
    model = Venda
    template_name = 'vendas/historico_vendas.html'
    context_object_name = 'vendas'
    ordering = ['-data_criacao']
    login_url = '/login/'

    def get_queryset(self):
        return Venda.objects.filter(vendedor=self.request.user).order_by('-data_criacao')
