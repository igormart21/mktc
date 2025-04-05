from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Venda
from .serializers import VendaSerializer
from .permissions import IsComprador, IsVendedorAprovado
from produtos.models import Produto

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

@login_required
def meus_pedidos(request):
    # Verifica se o usuário é um vendedor ou superadmin
    if not hasattr(request.user, 'vendedor') and not request.user.is_superuser:
        messages.error(request, 'Acesso negado. Apenas vendedores e administradores podem acessar esta página.')
        return redirect('core:home')
    
    # Obtém os filtros
    status = request.GET.get('status')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    busca = request.GET.get('busca')
    
    # Inicia a query
    if request.user.is_superuser:
        # Superadmin vê todos os pedidos
        pedidos = Venda.objects.all()
    else:
        # Vendedor vê apenas seus pedidos
        pedidos = Venda.objects.filter(vendedor=request.user)
    
    # Aplica os filtros
    if status:
        pedidos = pedidos.filter(status=status)
    if data_inicio:
        pedidos = pedidos.filter(data_criacao__date__gte=data_inicio)
    if data_fim:
        pedidos = pedidos.filter(data_criacao__date__lte=data_fim)
    if busca:
        pedidos = pedidos.filter(produto__nome__icontains=busca) | pedidos.filter(id__icontains=busca)
    
    # Ordena por data de criação (mais recentes primeiro)
    pedidos = pedidos.order_by('-data_criacao')
    
    # Paginação
    paginator = Paginator(pedidos, 10)  # 10 itens por página
    page = request.GET.get('page')
    pedidos = paginator.get_page(page)
    
    context = {
        'pedidos': pedidos,
        'status_choices': Venda.STATUS_CHOICES,
    }
    
    return render(request, 'vendas/meus_pedidos.html', context)

@login_required
def solicitar_compra(request, produto_id):
    # Verifica se o usuário é um vendedor
    if not hasattr(request.user, 'vendedor'):
        messages.error(request, 'Acesso negado. Apenas vendedores podem acessar esta página.')
        return redirect('core:home')
    
    # Obtém o produto
    produto = get_object_or_404(Produto, id=produto_id)
    
    if request.method == 'POST':
        quantidade = request.POST.get('quantidade')
        observacoes = request.POST.get('observacoes')
        
        # Cria o pedido
        Venda.objects.create(
            vendedor=request.user.vendedor,
            produto=produto,
            quantidade=quantidade,
            observacoes=observacoes,
            status='PENDENTE'
        )
        
        messages.success(request, 'Solicitação de compra enviada com sucesso! Aguarde a aprovação.')
        return redirect('vendas:meus_pedidos')
    
    return redirect('core:catalogo')

@login_required
def cancelar_pedido(request, pedido_id):
    # Verifica se o usuário é um vendedor
    if not hasattr(request.user, 'vendedor'):
        messages.error(request, 'Acesso negado. Apenas vendedores podem acessar esta página.')
        return redirect('core:home')
    
    # Obtém o pedido
    pedido = get_object_or_404(Venda, id=pedido_id, vendedor=request.user.vendedor)
    
    # Verifica se o pedido pode ser cancelado
    if pedido.status != 'PENDENTE':
        messages.error(request, 'Apenas pedidos pendentes podem ser cancelados.')
        return redirect('vendas:meus_pedidos')
    
    if request.method == 'POST':
        motivo_cancelamento = request.POST.get('motivo_cancelamento')
        
        # Atualiza o pedido
        pedido.status = 'REJEITADO'
        pedido.observacoes = f'Cancelado pelo vendedor: {motivo_cancelamento}'
        pedido.data_atualizacao = timezone.now()
        pedido.save()
        
        messages.success(request, 'Pedido cancelado com sucesso!')
        return redirect('vendas:meus_pedidos')
    
    return redirect('vendas:meus_pedidos')
