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
    try:
        produto = get_object_or_404(Produto, id=produto_id)
        
        # Verifica se o usuário é vendedor do produto
        if hasattr(request.user, 'vendedor') and produto.vendedor == request.user.vendedor:
            messages.error(request, 'Você não pode comprar seus próprios produtos.')
            return redirect('core:produto_detalhe', produto_id=produto_id)
        
        if not produto.ativo:
            messages.error(request, 'Este produto não está disponível para compra no momento.')
            return redirect('core:produto_detalhe', produto_id=produto_id)
        
        # Verificar se o usuário autenticado é uma instância de Usuario
        usuario = Usuario.objects.get(email=request.user.email)
        
        if request.method == 'POST':
            form = PedidoForm(request.POST)
            if form.is_valid():
                pedido = form.save(commit=False)
                pedido.comprador = usuario  # Usar a instância de Usuario
                
                # Obter o vendedor para o pedido
                if produto.vendedor:
                    # Se o produto tem um vendedor, use-o
                    pedido.vendedor = produto.vendedor.usuario
                else:
                    # Se o produto não tem vendedor, use um superadmin/admin
                    try:
                        # Tenta encontrar um superusuário
                        admin_user = get_user_model().objects.filter(is_superuser=True).first()
                        if not admin_user:
                            # Se não houver superusuário, use o primeiro staff
                            admin_user = get_user_model().objects.filter(is_staff=True).first()
                        
                        pedido.vendedor = admin_user
                    except:
                        # Se não encontrar nenhum admin, use o próprio comprador 
                        # (apenas como fallback para evitar erro)
                        pedido.vendedor = usuario
                
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
    except Usuario.DoesNotExist:
        messages.error(request, 'Seu perfil de usuário não está configurado corretamente.')
        return redirect('core:home')  # Redirecionar para a página inicial

@login_required
def meus_pedidos(request):
    try:
        # Tenta obter a instância do modelo Usuario correspondente ao usuário autenticado
        usuario = Usuario.objects.get(email=request.user.email)
        
        # Tenta obter os pedidos onde o usuário é o vendedor
        pedidos = []
        
        try:
            # Primeiro tenta carregar dos pedidos do modelo do app vendas (se disponível)
            from vendas.models import Pedido as VendasPedido
            pedidos = list(VendasPedido.objects.filter(vendedor=usuario).order_by('-data_pedido'))
        except (ImportError, OperationalError):
            # Se não conseguir, tenta carregar dos pedidos do core
            pedidos = list(CorePedido.objects.filter(comprador=usuario).order_by('-data_criacao'))
        
        if not pedidos:
            # Se ainda não tiver pedidos, tenta buscar vendas
            try:
                vendas = Venda.objects.filter(vendedor__usuario=usuario).order_by('-data_criacao')
                # Converte vendas para um formato compatível com pedidos para exibição
                pedidos = []
                for venda in vendas:
                    if hasattr(venda, 'pedido') and venda.pedido:
                        pedidos.append(venda.pedido)
            except Exception as e:
                # Em caso de erro, apenas continua com a lista vazia
                pass
        
        # Renderiza o template com os pedidos encontrados
        return render(request, 'vendas/meus_pedidos.html', {
            'pedidos': pedidos
        })
    except Usuario.DoesNotExist:
        messages.error(request, 'Seu perfil de usuário não está configurado corretamente.')
        return render(request, 'vendas/meus_pedidos.html', {
            'pedidos': [],
            'message': 'Seu perfil de usuário não está configurado corretamente.'
        })
    except Exception as e:
        # Trata qualquer outro erro que possa ocorrer
        messages.error(request, f'Ocorreu um erro ao buscar seus pedidos. Estamos trabalhando para resolver isso.')
        return render(request, 'vendas/meus_pedidos.html', {
            'pedidos': [],
            'message': 'Estamos passando por manutenção. Por favor, tente novamente mais tarde.'
        })

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
    pedidos = CorePedido.objects.all().order_by('-data_criacao')
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
