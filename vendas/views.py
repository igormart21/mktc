from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Venda, Pedido
from .serializers import VendaSerializer
from .permissions import IsVendedorAprovado
from produtos.models import Produto
from .forms import PedidoForm

# Create your views here.

class VendaViewSet(viewsets.ModelViewSet):
    serializer_class = VendaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        action = self.action

        if action == 'vendas_recebidas':
            return Venda.objects.filter(vendedor=user)
        return Venda.objects.none()

    def get_permissions(self):
        if self.action == 'vendas_recebidas':
            return [IsVendedorAprovado()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['get'])
    def vendas_recebidas(self, request):
        vendas = self.get_queryset()
        serializer = self.get_serializer(vendas, many=True)
        return Response(serializer.data)

class ListaVendasAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Venda.objects.all()
    serializer_class = VendaSerializer

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
def solicitar_compra(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    
    if not produto.vendedor:
        messages.error(request, 'Este produto não tem um vendedor associado.')
        return redirect('core:produto_detalhe', produto_id=produto_id)
    
    if hasattr(request.user, 'vendedor') and produto.vendedor == request.user.vendedor:
        messages.error(request, 'Você não pode comprar seus próprios produtos.')
        return redirect('core:produto_detalhe', produto_id=produto_id)
    
    if not produto.ativo:
        messages.error(request, 'Este produto não está disponível para compra no momento.')
        return redirect('core:produto_detalhe', produto_id=produto_id)
    
    if request.method == 'POST':
        form = PedidoForm(request.POST)
        if form.is_valid():
            pedido = form.save(commit=False)
            pedido.comprador = request.user
            pedido.vendedor = produto.vendedor.usuario
            pedido.produto = produto
            pedido.preco_unitario = produto.preco
            pedido.save()
            
            messages.success(request, 'Pedido realizado com sucesso!')
            return redirect('vendas:meus_pedidos')
    else:
        form = PedidoForm()
    
    return render(request, 'vendas/solicitar_compra.html', {
        'produto': produto,
        'form': form
    })

@login_required
def meus_pedidos(request):
    pedidos = Pedido.objects.filter(comprador=request.user).order_by('-data_pedido')
    pedidos_forms = {}
    for pedido in pedidos:
        pedidos_forms[pedido.id] = PedidoForm(instance=pedido)
    
    return render(request, 'vendas/meus_pedidos.html', {
        'pedidos': pedidos,
        'pedidos_forms': pedidos_forms
    })

@login_required
def cancelar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, comprador=request.user)
    
    if pedido.status != 'PENDENTE':
        messages.error(request, 'Não é possível cancelar um pedido que não está pendente.')
        return redirect('vendas:meus_pedidos')
    
    pedido.status = 'CANCELADO'
    pedido.save()
    
    messages.success(request, 'Pedido cancelado com sucesso!')
    return redirect('vendas:meus_pedidos')

@login_required
def editar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id, comprador=request.user)
    
    if pedido.status != 'PENDENTE':
        messages.error(request, 'Não é possível editar um pedido que não está pendente.')
        return redirect('vendas:meus_pedidos')
    
    if request.method == 'POST':
        form = PedidoForm(request.POST, instance=pedido)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pedido atualizado com sucesso!')
            return redirect('vendas:meus_pedidos')
    else:
        form = PedidoForm(instance=pedido)
    
    return render(request, 'vendas/editar_pedido.html', {
        'pedido': pedido,
        'form': form
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def lista_pedidos_admin(request):
    pedidos = Pedido.objects.all().order_by('-data_criacao')
    return render(request, 'vendas/admin/lista_pedidos.html', {'pedidos': pedidos})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def aprovar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    
    if request.method == 'POST':
        acao = request.POST.get('acao')
        
        if acao == 'aprovar':
            pedido.status = 'APROVADO'
            pedido.aprovado_por = request.user
            pedido.data_aprovacao = timezone.now()
            messages.success(request, 'Pedido aprovado com sucesso!')
        elif acao == 'rejeitar':
            pedido.status = 'REJEITADO'
            pedido.motivo_rejeicao = request.POST.get('motivo_rejeicao')
            messages.success(request, 'Pedido rejeitado com sucesso!')
        
        pedido.save()
    
    return redirect('vendas:lista_pedidos_admin')
