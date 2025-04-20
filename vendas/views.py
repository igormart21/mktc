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
from .models import Venda, Pedido, ItemPedido
from .serializers import VendaSerializer
from .permissions import IsVendedorAprovado
from produtos.models import Produto
from .forms import PedidoForm
from core.models import Pedido as CorePedido
from usuarios.models import Usuario
from django.db.utils import OperationalError
from django.contrib.auth import get_user_model
from core.carrinho import Carrinho

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

class VendaListView(ListView):
    model = Venda
    template_name = 'vendas/historico_vendas.html'
    context_object_name = 'vendas'
    paginate_by = 10
    ordering = ['-data_pedido']

    def get_queryset(self):
        return Venda.objects.filter(vendedor=self.request.user).order_by('-data_pedido')

@login_required
def solicitar_compra(request, produto_id):
    try:
        produto = get_object_or_404(Produto, id=produto_id)
        
        # Verifica se o usuário é vendedor do produto
        if hasattr(request.user, 'vendedor') and produto.vendedor == request.user.vendedor:
            messages.error(request, 'Você não pode comprar seus próprios produtos.')
            return redirect('core:produto_detalhe', produto_id=produto_id)
        
        if not produto.ativo:
            messages.error(request, 'Este produto não está disponível para compra no momento.')
            return redirect('core:produto_detalhe', produto_id=produto_id)
        
        if request.method == 'POST':
            quantidade = request.POST.get('quantidade', 1)
            observacoes = request.POST.get('observacoes', '')
            
            try:
                quantidade = int(quantidade)
                if quantidade <= 0:
                    raise ValueError('Quantidade inválida')
                    
                # Adicionar ao carrinho
                carrinho = Carrinho(request)
                carrinho.adicionar(produto, quantidade)
                
                messages.success(request, f'{produto.nome} adicionado ao carrinho!')
                return redirect('core:carrinho')
                
            except ValueError as e:
                messages.error(request, str(e))
                return redirect('core:produto_detalhe', produto_id=produto_id)
                
        return redirect('core:produto_detalhe', produto_id=produto_id)
        
    except Exception as e:
        messages.error(request, f'Erro ao processar a solicitação: {str(e)}')
        return redirect('core:produto_detalhe', produto_id=produto_id)

@login_required
def meus_pedidos(request):
<<<<<<< HEAD
    vendedor = getattr(request.user, 'vendedor', None)
    if vendedor:
        pedidos = Pedido.objects.filter(vendedor=vendedor).order_by('-data_pedido')
    else:
        pedidos = []
    return render(request, 'vendas/meus_pedidos.html', {'pedidos': pedidos})
=======
    try:
        # Tenta obter a instância do modelo Usuario correspondente ao usuário autenticado
        usuario = Usuario.objects.get(email=request.user.email)
        
        try:
            # Primeiro tenta buscar os pedidos do app vendas
            pedidos = list(Pedido.objects.filter(comprador=usuario).order_by('-data_pedido'))
        except (ImportError, OperationalError):
            # Se não encontrar, busca do core
            pedidos = []
        
        try:
            # Busca as vendas usando o modelo Venda do app vendas
            vendas = Venda.objects.filter(vendedor=request.user).order_by('-data_criacao')
        except (ImportError, OperationalError):
            vendas = []
        
        return render(request, 'vendas/meus_pedidos.html', {
            'pedidos': pedidos,
            'vendas': vendas
        })
    except Usuario.DoesNotExist:
        messages.error(request, 'Seu perfil de usuário não está configurado corretamente.')
        return redirect('core:home')
>>>>>>> fde08519d84a5fa5a718dec41d10f5357d309d6d

@login_required
def cancelar_pedido(request, pedido_id):
    try:
        # Tenta obter a instância do modelo Usuario correspondente ao usuário autenticado
        usuario = Usuario.objects.get(email=request.user.email)
        
        try:
            # Primeiro tenta buscar o pedido do app vendas
            from vendas.models import Pedido as VendasPedido
            pedido = get_object_or_404(VendasPedido, id=pedido_id, comprador=usuario)
        except (ImportError, OperationalError):
            # Se não encontrar, busca do core
            pedido = get_object_or_404(CorePedido, id=pedido_id, comprador=usuario)
        
        # Verifica se o pedido pode ser cancelado
        if pedido.status not in ['PROCESSANDO', 'PENDENTE']:
            messages.error(request, 'Não é possível cancelar um pedido que não está em processamento.')
        else:
            pedido.status = 'REJEITADO' if hasattr(pedido, 'REJEITADO') else 'CANCELADO'
            pedido.save()
            messages.success(request, 'Pedido cancelado com sucesso!')
        
    except Usuario.DoesNotExist:
        messages.error(request, 'Seu perfil de usuário não está configurado corretamente.')
    except Exception as e:
        messages.error(request, f'Ocorreu um erro ao cancelar o pedido. Por favor, tente novamente.')
    
    return redirect('vendas:meus_pedidos')

@login_required
def editar_pedido(request, pedido_id):
    try:
        # Tenta obter a instância do modelo Usuario correspondente ao usuário autenticado
        usuario = Usuario.objects.get(email=request.user.email)
        
        try:
            # Primeiro tenta buscar o pedido do app vendas
            from vendas.models import Pedido as VendasPedido
            pedido = get_object_or_404(VendasPedido, id=pedido_id, comprador=usuario)
            is_vendas_pedido = True
        except (ImportError, OperationalError):
            # Se não encontrar, busca do core
            pedido = get_object_or_404(CorePedido, id=pedido_id, comprador=usuario)
            is_vendas_pedido = False
        
        # Verifica se o pedido pode ser editado
        if pedido.status not in ['PROCESSANDO', 'PENDENTE']:
            messages.error(request, 'Não é possível editar um pedido que não está em processamento.')
            return redirect('vendas:meus_pedidos')
        
        if request.method == 'POST':
            # Adapte conforme necessário para os campos do CorePedido
            pedido.nome_propriedade = request.POST.get('nome_propriedade', pedido.nome_propriedade)
            pedido.cnpj = request.POST.get('cnpj', pedido.cnpj)
            
            # Campo hectares pode ser um decimal ou inteiro
            hectares = request.POST.get('hectares')
            if hectares:
                try:
                    pedido.hectares = float(hectares)
                except ValueError:
                    pass  # Mantém o valor atual
            
            pedido.cultivo_principal = request.POST.get('cultivo_principal', pedido.cultivo_principal)
            pedido.endereco = request.POST.get('endereco', pedido.endereco)
            pedido.cidade = request.POST.get('cidade', pedido.cidade)
            pedido.estado = request.POST.get('estado', pedido.estado)
            pedido.cep = request.POST.get('cep', pedido.cep)
            pedido.referencia = request.POST.get('referencia', pedido.referencia)
            pedido.observacoes = request.POST.get('observacoes', pedido.observacoes)
            pedido.save()
            
            messages.success(request, 'Pedido atualizado com sucesso!')
            return redirect('vendas:meus_pedidos')
        
        return render(request, 'vendas/editar_pedido.html', {
            'pedido': pedido,
            'is_vendas_pedido': is_vendas_pedido
        })
    except Usuario.DoesNotExist:
        messages.error(request, 'Seu perfil de usuário não está configurado corretamente.')
        return redirect('vendas:meus_pedidos')
    except Exception as e:
        messages.error(request, f'Ocorreu um erro ao processar o pedido. Por favor, tente novamente.')
        return redirect('vendas:meus_pedidos')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def lista_pedidos_admin(request):
    pedidos = CorePedido.objects.all().order_by('-data_pedido')
    return render(request, 'vendas/admin/lista_pedidos.html', {'pedidos': pedidos})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def aprovar_pedido(request, pedido_id):
    pedido = get_object_or_404(CorePedido, id=pedido_id)
    
    if request.method == 'POST':
        acao = request.POST.get('acao')
        
        if acao == 'aprovar':
            pedido.status = 'APROVADO'
            # CorePedido pode não ter esses campos, então ajuste conforme necessário
            # pedido.aprovado_por = request.user
            # pedido.data_aprovacao = timezone.now()
            messages.success(request, 'Pedido aprovado com sucesso!')
        elif acao == 'rejeitar':
            pedido.status = 'REJEITADO'
            # CorePedido pode não ter o campo motivo_rejeicao, então salve nas observações se necessário
            pedido.observacoes = request.POST.get('motivo_rejeicao', '')
            messages.success(request, 'Pedido rejeitado com sucesso!')
        
        pedido.save()
    
    return redirect('vendas:lista_pedidos_admin')
