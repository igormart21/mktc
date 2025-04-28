import json
from django.forms import ModelForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib import messages
from django.db.models import Count, Sum, F
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.forms import AuthenticationForm
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import ValidationError
from .models import Product, VendorApplication, SellerRegistration, MensagemSuporte, SolicitacaoProduto, Pedido, Venda, Vendedor, ItemPedido
from .forms import ProductForm, SellerRegistrationForm, LoginForm, SolicitacaoProdutoForm, SellerProfileForm, AdminProfileForm, VendaPrazoForm
from .utils import validate_file_upload, validate_cpf, is_superadmin, is_vendedor
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, Http404
import logging
from django.db.models import Q
from django.db.models.functions import TruncMonth
from django.core.paginator import Paginator
from vendedor.models import Vendedor
from usuarios.models import Usuario
from produtos.models import Produto
from .carrinho import Carrinho
from django.views.decorators.csrf import csrf_exempt
from .decorators import superuser_required, is_seller
from django.db import models
from django.contrib.auth.hashers import check_password
from django.utils.html import strip_tags
from django.contrib.auth import get_user_model
from decimal import Decimal

logger = logging.getLogger(__name__)

Usuario = get_user_model()

def home(request):
    """View principal do site"""
    products = Product.objects.filter(is_active=True).order_by('-created_at')[:6]
    
    context = {
        'products': products,
    }
    return render(request, 'core/home.html', context)

def login_view(request):
    """View de login"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['username']
            password = form.cleaned_data['password']
            from django.contrib.auth import authenticate
            user = authenticate(request, username=email, password=password)
            if user is not None:
                # O objeto retornado por authenticate já tem o backend
                from django.contrib.auth import login
                login(request, user, backend=user.backend)
                return redirect('core:dashboard')
            else:
                messages.error(request, 'Email ou senha inválidos.')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = LoginForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    """View de logout"""
    logout(request)
    return redirect('core:home')

def generate_email_confirmation_token(user):
    """Gera um token para confirmação de email"""
    return urlsafe_base64_encode(force_bytes(user.pk))

def confirm_email(request, uidb64, token):
    """Confirma o email do usuário"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Usuario.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        user = None

    if user is not None:
        user.is_active = True
        user.save()
        messages.success(request, 'Seu email foi confirmado com sucesso!')
        return redirect('core:login')
    else:
        messages.error(request, 'Link de confirmação inválido.')
        return redirect('core:home')

def send_confirmation_email(user, request):
    """Envia email de confirmação"""
    token = generate_email_confirmation_token(user)
    current_site = request.get_host()
    mail_subject = 'Confirme seu email'
    message = render_to_string('core/email_confirmation.html', {
        'user': user,
        'domain': current_site,
        'uid': token,
    })
    send_mail(
        mail_subject,
        message,
        settings.EMAIL_HOST_USER,
        [user.email],
        fail_silently=False,
    )

def seller_registration(request):
    """View de registro de vendedor"""
    if request.method == 'POST':
        form = SellerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, 'Cadastro realizado com sucesso! Aguarde a aprovação do administrador.')
                return redirect('core:login')
            except Exception as e:
                messages.error(request, f'Erro ao cadastrar vendedor: {str(e)}')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = SellerRegistrationForm()
    
    return render(request, 'core/seller_registration.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def superadmin_dashboard(request):
    """Dashboard do superadmin"""
    from django.db.models import Q
    # Métricas principais
    total_vendedores = Vendedor.objects.count()
    vendedores_ativos = Vendedor.objects.filter(usuario__is_active=True).count()
    total_produtos = Produto.objects.count()
    mensagens_pendentes = MensagemSuporte.objects.filter(respondido=False).count()
    total_usuarios = Usuario.objects.count()
    total_pedidos = Pedido.objects.count()

    # Métricas de desempenho
    pedidos_recebidos = Pedido.objects.count()
    vendas_aprovadas = Pedido.objects.filter(status='APROVADO').count()
    if pedidos_recebidos > 0:
        percentual_vendas_aprovadas = int((vendas_aprovadas / pedidos_recebidos) * 100)
    else:
        percentual_vendas_aprovadas = 0

    # Últimos vendedores registrados
    ultimos_vendedores = Vendedor.objects.order_by('-created_at')[:5]

    # Pedidos pendentes
    pedidos_pendentes = Pedido.objects.filter(status='AGUARDANDO_APROVACAO').order_by('-data_criacao')[:5]

    # Pedidos recentes
    pedidos_recentes = Pedido.objects.order_by('-data_criacao')[:5]

    # Produtos recentes
    produtos_recentes = Produto.objects.order_by('-created_at')[:5]

    context = {
        'total_vendedores': total_vendedores,
        'vendedores_ativos': vendedores_ativos,
        'total_produtos': total_produtos,
        'mensagens_pendentes': mensagens_pendentes,
        'total_usuarios': total_usuarios,
        'total_pedidos': total_pedidos,
        'pedidos_recebidos': pedidos_recebidos,
        'vendas_aprovadas': vendas_aprovadas,
        'percentual_vendas_aprovadas': percentual_vendas_aprovadas,
        'ultimos_vendedores': ultimos_vendedores,
        'pedidos_pendentes': pedidos_pendentes,
        'pedidos_recentes': pedidos_recentes,
        'produtos_recentes': produtos_recentes,
    }
    return render(request, 'core/superadmin_dashboard.html', context)

@login_required
@is_seller
def seller_dashboard(request):
    """Dashboard do vendedor"""
    try:
        # Garantir que temos um objeto Usuario válido
        usuario = request.user
        if not isinstance(usuario, Usuario):
            usuario = Usuario.objects.get(pk=request.user.pk)
        
        # Garantir que temos um objeto Vendedor válido
        vendedor = Vendedor.objects.get(usuario=usuario)
    except (Usuario.DoesNotExist, Vendedor.DoesNotExist, AttributeError):
        messages.error(request, 'Você precisa ser um vendedor para acessar esta página.')
        return redirect('core:home')
    
    # Produtos - agora mostrando todos os produtos ativos
    total_products = Produto.objects.filter(ativo=True).count()
    recent_products = Produto.objects.filter(ativo=True).order_by('-created_at')[:5]

    # Pedidos do vendedor - usando o objeto Usuario ao invés do Vendedor
    pedidos = Pedido.objects.filter(vendedor=usuario)
    total_pedidos = pedidos.count()
    pedidos_pendentes = pedidos.filter(status='AGUARDANDO_APROVACAO').count()
    pedidos_aprovados = pedidos.filter(status='APROVADO').count()
    pedidos_rejeitados = pedidos.filter(status='REJEITADO').count()
    ultimos_pedidos = pedidos.order_by('-data_criacao')[:5]
    
    # Calcular o total de vendas somando os itens dos pedidos aprovados
    total_vendas = 0
    for pedido in pedidos.filter(status='APROVADO'):
        for item in pedido.itens.all():
            total_vendas += item.quantidade * item.preco_unitario

    # Calcular vendas por mês para o gráfico
    vendas_por_mes = []
    meses = []
    hoje = timezone.now()
    
    # Pegar os últimos 6 meses
    for i in range(6):
        mes = hoje - timedelta(days=30*i)
        mes_inicio = mes.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        mes_fim = (mes_inicio + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        vendas_mes = 0
        pedidos_mes = pedidos.filter(
            status='APROVADO',
            data_criacao__range=[mes_inicio, mes_fim]
        )
        
        for pedido in pedidos_mes:
            for item in pedido.itens.all():
                vendas_mes += float(item.quantidade) * float(item.preco_unitario)
        
        vendas_por_mes.append(round(vendas_mes, 2))
        meses.append(mes.strftime('%b/%Y'))
    
    # Inverter as listas para mostrar do mais antigo para o mais recente
    vendas_por_mes.reverse()
    meses.reverse()

    # Garantir que temos pelo menos 6 meses de dados
    while len(vendas_por_mes) < 6:
        vendas_por_mes.append(0)
        meses.append((hoje - timedelta(days=30*len(vendas_por_mes))).strftime('%b/%Y'))

    # Mensagens de suporte do vendedor
    mensagens_suporte = MensagemSuporte.objects.filter(usuario=usuario).order_by('-data_envio')

    # Garante que o contexto tenha o usuário correto para o template
    context = {
        'user': usuario,
        'vendedor': vendedor,
        'total_products': total_products,
        'total_pedidos': total_pedidos,
        'pedidos_pendentes': pedidos_pendentes,
        'pedidos_aprovados': pedidos_aprovados,
        'pedidos_rejeitados': pedidos_rejeitados,
        'ultimos_pedidos': ultimos_pedidos,
        'total_vendas': total_vendas,
        'recent_products': recent_products,
        'mensagens_suporte': mensagens_suporte,
        'vendas_por_mes': vendas_por_mes,
        'meses': meses,
    }
    
    return render(request, 'core/seller_dashboard.html', context)

@login_required
@user_passes_test(is_superadmin)
def aprovar_cadastro(request, cadastro_id):
    """Aprova o cadastro de um vendedor"""
    cadastro = get_object_or_404(SellerRegistration, id=cadastro_id)
    if cadastro.status == 'pendente':
        cadastro.status = 'aprovado'
        cadastro.save()
        
        # Cria o vendedor
        vendedor = Vendedor.objects.create(
            usuario=cadastro.user,
            razao_social=cadastro.user.nome,
            nome_fantasia=cadastro.user.nome,
            cnpj=cadastro.user.numero_documento,
            telefone=cadastro.user.telefone,
            endereco=cadastro.user.rua,
            cidade=cadastro.user.cidade,
            estado=cadastro.user.estado,
            cep=cadastro.user.cep,
        )
        
        messages.success(request, 'Cadastro aprovado com sucesso!')
    else:
        messages.error(request, 'Este cadastro já foi processado.')
    return redirect('core:listar_vendedores')

@login_required
@user_passes_test(is_superadmin)
def rejeitar_cadastro(request, cadastro_id):
    """Rejeita o cadastro de um vendedor"""
    cadastro = get_object_or_404(SellerRegistration, id=cadastro_id)
    if cadastro.status == 'pendente':
        cadastro.status = 'rejeitado'
        cadastro.save()
        messages.success(request, 'Cadastro rejeitado com sucesso!')
    else:
        messages.error(request, 'Este cadastro já foi processado.')
    return redirect('core:listar_vendedores')

@login_required
def product_create(request):
    """Cria um novo produto"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            if hasattr(request.user, 'vendedor'):
                product.seller = request.user.vendedor
                product.save()
                messages.success(request, 'Produto criado com sucesso!')
                return redirect('core:product_list')
    else:
        form = ProductForm()
    return render(request, 'core/product_form.html', {'form': form})

@login_required
@user_passes_test(is_superadmin)
def product_update(request, pk):
    """Atualiza um produto"""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto atualizado com sucesso!')
            return redirect('core:product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'core/product_form.html', {'form': form})

@login_required
def product_delete(request, pk):
    """Deleta um produto"""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Produto deletado com sucesso!')
        return redirect('core:product_list')
    return render(request, 'core/product_confirm_delete.html', {'product': product})

@login_required
def product_detail(request, pk):
    """Mostra os detalhes de um produto"""
    try:
        product = get_object_or_404(Product, pk=pk)
        return render(request, 'core/product_detail.html', {'product': product})
    except:
        # Se não encontrar um Product, tenta encontrar um Produto
        from produtos.models import Produto
        try:
            produto = get_object_or_404(Produto, id=pk)
            return render(request, 'core/produto_detalhe.html', {'produto': produto})
        except:
            raise Http404("Produto não encontrado")

@login_required
def profile(request):
    """Mostra o perfil do usuário"""
    return render(request, 'core/profile.html')

@login_required
@user_passes_test(is_superadmin)
def seller_edit(request, seller_id):
    """Edita um vendedor"""
    seller = get_object_or_404(Vendedor.objects.select_related('usuario'), id=seller_id)
    print('DEBUG - Bairro ao carregar vendedor:', seller.bairro)
    
    if request.method == 'POST':
        # Atualizar dados do usuário
        seller.usuario.nome = request.POST.get('nome', '')
        seller.usuario.sobrenome = request.POST.get('sobrenome', '')
        seller.usuario.email = request.POST.get('email', '')
        seller.usuario.cpf = request.POST.get('cpf', '')
        seller.usuario.document_type = request.POST.get('document_type', 'RG')
        
        # Atualizar dados do vendedor
        seller.telefone = request.POST.get('phone', '')
        seller.nome_fantasia = request.POST.get('nome_fantasia', '')
        seller.hectares_atendidos = request.POST.get('hectares_atendidos', 0)
        seller.cep = request.POST.get('cep', '')
        seller.endereco = request.POST.get('rua', '')
        seller.numero = request.POST.get('numero', '')
        seller.bairro = request.POST.get('bairro', '')
        print('DEBUG - Bairro do POST:', request.POST.get('bairro', ''))
        print('DEBUG - Bairro após atribuição:', seller.bairro)
        seller.cidade = request.POST.get('cidade', '')
        seller.estado = request.POST.get('estado', '')
        
        # Atualizar culturas atendidas
        culturas = request.POST.getlist('culturas_atendidas')
        seller.culturas_atendidas = culturas
        
        # Processar redefinição de senha
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password and confirm_password and new_password == confirm_password:
            seller.usuario.set_password(new_password)
        elif new_password or confirm_password:
            messages.error(request, 'As senhas não coincidem.')
            return redirect('core:seller_edit', seller_id=seller.id)
        
        # Salvar alterações
        seller.usuario.save()
        seller.save()
        print('DEBUG - Bairro após salvar:', seller.bairro)
        
        messages.success(request, 'Vendedor atualizado com sucesso!')
        return redirect('core:seller_detail', seller_id=seller.id)
    
    # Preparar o contexto com as culturas disponíveis e as culturas atuais do vendedor
    culturas_disponiveis = Vendedor.CULTURAS_CHOICES
    culturas_atuais = seller.culturas_atendidas or []

    print('DEBUG - Bairro antes de renderizar:', seller.bairro)
    
    return render(request, 'core/seller_edit.html', {
        'seller': seller,
        'culturas_disponiveis': culturas_disponiveis,
        'culturas_atuais': culturas_atuais
    })

@login_required
@user_passes_test(is_superadmin)
def seller_disable(request, seller_id):
    """Desativa um vendedor (não altera status_aprovacao)"""
    seller = get_object_or_404(Vendedor, id=seller_id)
    seller.usuario.is_active = False
    seller.usuario.save()
    messages.success(request, 'Vendedor desativado com sucesso!')
    return redirect('core:listar_vendedores')

@login_required
@user_passes_test(is_superadmin)
def seller_enable(request, seller_id):
    """Ativa um vendedor (apenas se aprovado)"""
    seller = get_object_or_404(Vendedor, id=seller_id)
    if seller.status_aprovacao == 'APROVADO':
        seller.usuario.is_active = True
        seller.usuario.save()
        messages.success(request, 'Vendedor ativado com sucesso!')
    else:
        messages.error(request, 'Só é possível ativar vendedores aprovados.')
    return redirect('core:listar_vendedores')

@login_required
@user_passes_test(is_superadmin)
def seller_delete(request, seller_id):
    """Deleta um vendedor"""
    seller = get_object_or_404(Vendedor, id=seller_id)
    if request.method == 'POST':
        seller.delete()
        messages.success(request, 'Vendedor deletado com sucesso!')
        return redirect('core:listar_vendedores')
    return render(request, 'core/seller_confirm_delete.html', {'seller': seller})

@login_required
def order_create(request):
    """Cria um novo pedido"""
    if request.method == 'POST':
        form = ModelForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.customer_name = request.user.get_full_name()
            order.customer_email = request.user.email
            order.save()
            messages.success(request, 'Pedido criado com sucesso!')
            return redirect('core:pedido_detail', pedido_id=order.id)
    else:
        form = ModelForm()
    return render(request, 'core/order_form.html', {'form': form})

@login_required
def pedido_detail(request, pedido_id):
    """Mostra os detalhes de um pedido"""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    return render(request, 'core/pedido_detail.html', {'pedido': pedido})

@login_required
def pedido_edit(request, pedido_id):
    """Edita um pedido"""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    if request.method == 'POST':
        form = ModelForm(request.POST, instance=pedido)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pedido atualizado com sucesso!')
            return redirect('core:pedido_detail', pedido_id=pedido.id)
    else:
        form = ModelForm(instance=pedido)
    return render(request, 'core/order_form.html', {'form': form})

@login_required
@user_passes_test(is_superadmin)
def superadmin_pedidos(request):
    # Filtros
    status = request.GET.get('status')
    tipo_venda = request.GET.get('tipo_venda')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')

    # Ação de arquivar/desarquivar
    if request.method == 'POST':
        pedido_id = request.POST.get('pedido_id')
        acao = request.POST.get('acao')
        if pedido_id and acao:
            pedido = Pedido.objects.get(id=pedido_id)
            if acao == 'arquivar' and pedido.status == 'APROVADO':
                pedido.status = 'ARQUIVADO'
                pedido.save()
                messages.success(request, f'Pedido #{pedido.id} arquivado com sucesso!')
            elif acao == 'desarquivar' and pedido.status == 'ARQUIVADO':
                pedido.status = 'APROVADO'
                pedido.save()
                messages.success(request, f'Pedido #{pedido.id} desarquivado com sucesso!')
            return redirect('core:superadmin_pedidos')

    # Obter todos os pedidos
    pedidos = Pedido.objects.all().order_by('-data_criacao')

    # Por padrão, não mostrar arquivados, só se filtrar explicitamente
    if not status or status != 'ARQUIVADO':
        pedidos = pedidos.exclude(status='ARQUIVADO')

    # Aplicar filtros
    if status:
        pedidos = pedidos.filter(status=status)
    if tipo_venda:
        pedidos = pedidos.filter(tipo_venda=tipo_venda)
    if data_inicio:
        try:
            data_inicio = timezone.datetime.strptime(data_inicio, '%Y-%m-%d')
            pedidos = pedidos.filter(data_criacao__gte=data_inicio)
        except ValueError:
            pass
    if data_fim:
        try:
            data_fim = timezone.datetime.strptime(data_fim, '%Y-%m-%d')
            data_fim = data_fim.replace(hour=23, minute=59, second=59)
            pedidos = pedidos.filter(data_criacao__lte=data_fim)
        except ValueError:
            pass

    # Paginação
    paginator = Paginator(pedidos, 20)
    page = request.GET.get('page')
    pedidos = paginator.get_page(page)

    context = {
        'pedidos': pedidos,
        'status_choices': Pedido.STATUS_CHOICES,
        'tipo_venda_choices': Pedido.TIPO_VENDA_CHOICES,
        'current_status': status,
        'current_tipo_venda': tipo_venda,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
    }
    return render(request, 'core/superadmin_pedidos.html', context)

@login_required
@user_passes_test(is_superadmin)
def superadmin_order_detail(request, order_id):
    order = get_object_or_404(Pedido, id=order_id)
    if request.method == 'POST':
        novo_status = request.POST.get('status')
        if novo_status and novo_status != order.status:
            order.status = novo_status
            order.save()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'order_id': order.id,
                'status': order.status,
                'status_display': order.get_status_display(),
            })
        return redirect('core:superadmin_pedidos')
    return render(request, 'core/superadmin_order_detail.html', {'order': order})

@login_required
@user_passes_test(is_superadmin)
def superadmin_order_delete(request, order_id):
    """Deleta um pedido como superadmin"""
    order = get_object_or_404(Pedido, id=order_id)
    if request.method == 'POST':
        order.delete()
        messages.success(request, 'Pedido deletado com sucesso!')
        return redirect('core:superadmin_pedidos')
    return render(request, 'core/superadmin_order_confirm_delete.html', {'order': order})

@login_required
@user_passes_test(is_superadmin)
def listar_superadmins(request):
    """Lista todos os superadmins"""
    superadmins = Usuario.objects.filter(is_superuser=True)
    return render(request, 'core/superadmin_list.html', {'superadmins': superadmins})

@superuser_required
def cadastrar_vendedor(request):
    """Cadastra um novo vendedor"""
    if request.method == 'POST':
        form = SellerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                # Criar o usuário
                user = form.save(commit=False)
                user.is_vendedor = True
                user.save()

                # Criar o vendedor
                vendedor = Vendedor.objects.create(
                    usuario=user,
                    nome_fantasia=f"{form.cleaned_data['nome']} {form.cleaned_data['sobrenome']}",
                    telefone=form.cleaned_data['telefone'],
                    endereco=form.cleaned_data['endereco'],
                    cidade=form.cleaned_data['cidade'],
                    estado=form.cleaned_data['estado'],
                    cep=form.cleaned_data['cep'],
                    hectares_atendidos=form.cleaned_data['hectares_atendidos']
                )

                # Salvar o documento
                if 'arquivo_documento' in request.FILES:
                    documento = request.FILES['arquivo_documento']
                    if form.cleaned_data['tipo_documento'] == 'RG':
                        vendedor.rg = documento
                    else:
                        vendedor.cnh = documento
                    vendedor.save()

                messages.success(request, 'Vendedor cadastrado com sucesso!')
                return redirect('core:listar_vendedores')
            except Exception as e:
                messages.error(request, f'Erro ao cadastrar vendedor: {str(e)}')
                return redirect('core:cadastrar_vendedor')
    else:
        form = SellerRegistrationForm()
    
    return render(request, 'core/cadastrar_vendedor.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def review_application(request, application_id):
    """Revisa uma aplicação de vendedor"""
    application = get_object_or_404(VendorApplication, id=application_id)
    if request.method == 'POST':
        status = request.POST.get('status')
        notes = request.POST.get('notes')
        application.status = status
        application.notes = notes
        application.save()
        messages.success(request, 'Aplicação revisada com sucesso!')
        return redirect('core:listar_vendedores')
    return render(request, 'core/review_application.html', {'application': application})

def seller_detail(request, seller_id):
    """Mostra os detalhes de um vendedor"""
    seller = get_object_or_404(Vendedor, id=seller_id)
    products = Product.objects.filter(seller=seller)
    return render(request, 'core/seller_detail.html', {'seller': seller, 'products': products})

@user_passes_test(is_superadmin)
def superadmin_product_update(request, pk):
    produto = get_object_or_404(Produto, pk=pk)
    title = f"Editar Produto: {produto.nome}"
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=produto)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Produto atualizado com sucesso!')
                return redirect('core:superadmin_products')
            except Exception as e:
                messages.error(request, f'Erro ao atualizar produto: {str(e)}')
    else:
        form = ProductForm(instance=produto)
    
    return render(request, 'core/superadmin_product_form.html', {
        'form': form,
        'title': title,
        'produto': produto
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
@csrf_exempt
def consult_ia(request):
    """Consulta a IA para sugestões"""
    if request.method == 'POST':
        data = json.loads(request.body)
        prompt = data.get('prompt')
        # Aqui você implementaria a lógica de consulta à IA
        response = {'suggestion': 'Sugestão da IA'}
        return JsonResponse(response)
    return JsonResponse({'error': 'Método não permitido'}, status=405)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def consult_ia_page(request):
    """Página de consulta à IA"""
    return render(request, 'core/consult_ia.html')

@login_required
def dashboard(request):
    """Dashboard do usuário"""
    if request.user.is_superuser:
        return redirect('core:superadmin_dashboard')
    elif hasattr(request.user, 'vendedor'):
        return redirect('core:seller_dashboard')
    else:
        return redirect('core:home')

@login_required
def catalogo(request):
    """Catálogo de produtos"""
    # Obtém os parâmetros de filtro da URL
    categoria = request.GET.get('categoria')
    tipo = request.GET.get('tipo')
    preco_min = request.GET.get('preco_min')
    preco_max = request.GET.get('preco_max')
    busca = request.GET.get('busca')
    ordenar = request.GET.get('ordenar', 'recentes')

    # Filtra os produtos - mostrar todos os produtos ativos
    produtos = Produto.objects.filter(ativo=True)
    
    # Aplica os filtros
    if categoria:
        produtos = produtos.filter(categoria=categoria)
    if tipo:
        produtos = produtos.filter(tipo=tipo)
    if preco_min:
        produtos = produtos.filter(preco__gte=preco_min)
    if preco_max:
        produtos = produtos.filter(preco__lte=preco_max)
    if busca:
        produtos = produtos.filter(
            models.Q(nome__icontains=busca) | 
            models.Q(descricao__icontains=busca)
        )

    # Aplica a ordenação
    if ordenar == 'preco_menor':
        produtos = produtos.order_by('preco')
    elif ordenar == 'preco_maior':
        produtos = produtos.order_by('-preco')
    elif ordenar == 'nome':
        produtos = produtos.order_by('nome')
    else:  # recentes
        produtos = produtos.order_by('-created_at')

    # Paginação
    paginator = Paginator(produtos, 12)  # 12 produtos por página
    page = request.GET.get('page')
    produtos = paginator.get_page(page)

    context = {
        'produtos': produtos,
        'categorias': Produto.CATEGORIA_CHOICES,
        'tipos': Produto.TIPO_CHOICES,
        'categoria_selecionada': categoria,
        'tipo_selecionado': tipo,
        'preco_min': preco_min,
        'preco_max': preco_max,
        'busca': busca,
        'ordenar': ordenar,
    }
    return render(request, 'core/catalogo.html', context)

@login_required
def suporte(request):
    """Página de suporte"""
    if request.method == 'POST':
        assunto = request.POST.get('assunto')
        mensagem = request.POST.get('mensagem')
        MensagemSuporte.objects.create(
            usuario=request.user,
            assunto=assunto,
            mensagem=mensagem
        )
        messages.success(request, 'Mensagem enviada com sucesso!')
        return redirect('core:suporte')
    # Buscar as mensagens do usuário autenticado
    mensagens = MensagemSuporte.objects.filter(usuario=request.user).order_by('-data_envio')
    return render(request, 'core/suporte.html', {'mensagens': mensagens})

@login_required
@user_passes_test(is_superadmin)
def superadmin_suporte(request):
    """Página de suporte para superadmin"""
    if request.method == 'POST' and 'encerrar_id' in request.POST:
        encerrar_id = request.POST.get('encerrar_id')
        mensagem = MensagemSuporte.objects.filter(id=encerrar_id).first()
        if mensagem:
            mensagem.respondido = True
            if not mensagem.resposta:
                mensagem.resposta = 'Caso encerrado pelo administrador.'
            mensagem.data_resposta = timezone.now()
            mensagem.save()
            messages.success(request, 'Caso encerrado com sucesso!')
        return redirect('core:superadmin_suporte')
    mensagens = MensagemSuporte.objects.all()
    return render(request, 'core/superadmin_suporte.html', {'mensagens': mensagens})

@login_required
def solicitar_produto(request):
    """Solicita um novo produto"""
    # Verifica se o usuário é um vendedor
    if not hasattr(request.user, 'vendedor'):
        messages.error(request, 'Acesso negado. Apenas vendedores podem solicitar produtos.')
        return redirect('core:home')
        
    if request.method == 'POST':
        form = SolicitacaoProdutoForm(request.POST)
        if form.is_valid():
            solicitacao = form.save(commit=False)
            solicitacao.vendedor = request.user.vendedor
            solicitacao.status = 'pendente'
            solicitacao.save()
            messages.success(request, 'Solicitação enviada com sucesso! Aguarde a análise do administrador.')
            return redirect('core:minhas_solicitacoes')
        else:
            # Se o formulário não for válido, mostra os erros
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = SolicitacaoProdutoForm()
    
    return render(request, 'core/solicitar_produto.html', {'form': form})

@login_required
def minhas_solicitacoes(request):
    """Lista as solicitações de produto do usuário"""
    if not hasattr(request.user, 'vendedor'):
        messages.error(request, 'Você precisa ser um vendedor para acessar esta página.')
        return redirect('core:dashboard')
    solicitacoes = SolicitacaoProduto.objects.filter(vendedor=request.user.vendedor)
    return render(request, 'core/minhas_solicitacoes.html', {'solicitacoes': solicitacoes})

@login_required
def detalhes_solicitacao(request, pk):
    """Mostra os detalhes de uma solicitação"""
    solicitacao = get_object_or_404(SolicitacaoProduto, pk=pk)
    return render(request, 'core/detalhes_solicitacao.html', {'solicitacao': solicitacao})

@login_required
@user_passes_test(is_superadmin)
def superadmin_solicitacoes(request):
    """Lista todas as solicitações de produto"""
    solicitacoes = SolicitacaoProduto.objects.all().order_by('-data_solicitacao')
    return render(request, 'core/superadmin_solicitacoes.html', {'solicitacoes': solicitacoes})

@login_required
@user_passes_test(is_superadmin)
def superadmin_detalhes_solicitacao(request, pk):
    """Mostra os detalhes de uma solicitação para o superadmin"""
    solicitacao = get_object_or_404(SolicitacaoProduto, pk=pk)
    
    if request.method == 'POST':
        acao = request.POST.get('acao')
        resposta = request.POST.get('resposta', '')
        
        if acao == 'aprovar':
            solicitacao.status = 'aprovado'
            solicitacao.resposta_superadmin = resposta
            solicitacao.save()
            messages.success(request, 'Solicitação aprovada com sucesso!')
            
        elif acao == 'rejeitar':
            solicitacao.status = 'rejeitado'
            solicitacao.resposta_superadmin = resposta
            solicitacao.save()
            messages.success(request, 'Solicitação rejeitada com sucesso!')
            
        elif acao == 'excluir':
            solicitacao.delete()
            messages.success(request, 'Solicitação excluída com sucesso!')
            return redirect('core:superadmin_solicitacoes')
            
        return redirect('core:superadmin_solicitacoes')
        
    return render(request, 'core/superadmin_detalhes_solicitacao.html', {'solicitacao': solicitacao})

@login_required
def request_product(request):
    """Solicita um novo produto"""
    if not hasattr(request.user, 'vendedor'):
        messages.error(request, 'Você precisa ser um vendedor para acessar esta página.')
        return redirect('core:dashboard')
    if request.method == 'POST':
        form = SolicitacaoProdutoForm(request.POST)
        if form.is_valid():
            solicitacao = form.save(commit=False)
            solicitacao.vendedor = request.user.vendedor
            # Garantir que quantidade tenha um valor padrão se estiver em branco
            if not solicitacao.quantidade:
                solicitacao.quantidade = 1.0
            solicitacao.save()
            messages.success(request, 'Solicitação enviada com sucesso!')
            return redirect('core:minhas_solicitacoes')
        else:
            # Exibir erros de validação
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = SolicitacaoProdutoForm()
    return render(request, 'core/request_product.html', {'form': form})

@login_required
def seller_profile(request):
    """Perfil do vendedor"""
    try:
        seller = request.user.vendedor
    except Vendedor.DoesNotExist:
        messages.error(request, 'Você precisa ser um vendedor para acessar esta página.')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = SellerProfileForm(request.POST, request.FILES, instance=seller)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            
            # Verificar se campos de senha estão preenchidos
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if current_password and new_password and confirm_password:
                # Verificar se a senha atual está correta
                if not request.user.check_password(current_password):
                    messages.error(request, 'Senha atual incorreta.')
                    return redirect('core:seller_profile')
                
                # Verificar se as novas senhas coincidem
                if new_password != confirm_password:
                    messages.error(request, 'As novas senhas não coincidem.')
                    return redirect('core:seller_profile')
                
                # Verificar tamanho mínimo da senha
                if len(new_password) < 8:
                    messages.error(request, 'A nova senha deve ter pelo menos 8 caracteres.')
                    return redirect('core:seller_profile')
                
                # Trocar a senha
                request.user.set_password(new_password)
                request.user.save()
                
                # Atualiza a sessão para evitar logout
                update_session_auth_hash(request, request.user)
                
                messages.success(request, 'Senha alterada com sucesso!')
                
            return redirect('core:seller_profile')
    else:
        form = SellerProfileForm(instance=seller)
    
    context = {
        'form': form,
        'seller': seller,
    }
    return render(request, 'core/seller_profile.html', context)

@login_required
def produto_detalhe(request, produto_id):
    """Mostra os detalhes de um produto"""
    produto = get_object_or_404(Produto, id=produto_id)
    return render(request, 'core/produto_detalhe.html', {'produto': produto})

@login_required
@user_passes_test(is_superadmin)
def admin_profile(request):
    """View para gerenciar o perfil do administrador"""
    user = request.user
    if request.method == 'POST':
        form = AdminProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('core:admin_profile')
    else:
        form = AdminProfileForm(instance=user)
    
    context = {
        'form': form,
        'user': user,
    }
    return render(request, 'core/admin_profile.html', context)

@login_required
@user_passes_test(is_superadmin)
def listar_vendas_pendentes(request):
    """Lista todas as vendas pendentes"""
    vendas_pendentes = Venda.objects.filter(status='PENDENTE').order_by('-data_criacao')
    return render(request, 'core/listar_vendas_pendentes.html', {'vendas': vendas_pendentes})

@login_required
@user_passes_test(is_superadmin)
def aprovar_venda(request, venda_id):
    """Aprova uma venda pendente"""
    venda = get_object_or_404(Venda, id=venda_id)
    if venda.status == 'PENDENTE':
        venda.status = 'ACEITO'
        venda.save()
        messages.success(request, 'Venda aprovada com sucesso!')
    else:
        messages.error(request, 'Esta venda já foi processada.')
    return redirect('core:listar_vendas_pendentes')

@login_required
@user_passes_test(is_superadmin)
def rejeitar_venda(request, venda_id):
    """Rejeita uma venda pendente"""
    venda = get_object_or_404(Venda, id=venda_id)
    if venda.status == 'PENDENTE':
        venda.status = 'REJEITADO'
        venda.save()
        messages.success(request, 'Venda rejeitada com sucesso!')
    else:
        messages.error(request, 'Esta venda já foi processada.')
    return redirect('core:listar_vendas_pendentes')

@login_required
@user_passes_test(is_vendedor)
def historico_pedidos_vendedor(request):
    """Lista o histórico de pedidos do vendedor logado"""
    vendedor = request.user.vendedor
    pedidos = Pedido.objects.filter(vendedor=vendedor).order_by('-data_criacao')
    # Filtros
    status = request.GET.get('status')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    if status:
        pedidos = pedidos.filter(status=status)
    if data_inicio:
        pedidos = pedidos.filter(data_criacao__date__gte=data_inicio)
    if data_fim:
        pedidos = pedidos.filter(data_criacao__date__lte=data_fim)
    context = {
        'pedidos': pedidos,
        'status_choices': [('PENDENTE', 'Pendente'), ('APROVADO', 'Aprovado'), ('REJEITADO', 'Rejeitado')],
        'status_selecionado': status,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
    }
    return render(request, 'core/historico_pedidos.html', context)

@login_required
@user_passes_test(is_superadmin)
def historico_pedidos_vendedor_admin(request, vendedor_id):
    vendedor = get_object_or_404(Vendedor, id=vendedor_id)
    usuario = vendedor.usuario
    
    # Temporariamente substituindo a consulta problemática
    # pedidos = Pedido.objects.filter(vendedor=usuario).order_by('-data_criacao')
    pedidos = []
    
    context = {
        'vendedor': vendedor,
        'pedidos': pedidos,
        'status_choices': [('PENDENTE', 'Pendente'), ('APROVADO', 'Aprovado'), ('REJEITADO', 'Rejeitado')],
        'aviso_manutencao': 'Sistema em manutenção. Histórico de pedidos temporariamente indisponível.'
    }
    return render(request, 'core/historico_pedidos.html', context)

@login_required
def checkout(request):
    from core.carrinho import Carrinho
    from core.models import Venda, Product, Pedido
    from vendedor.models import Vendedor
    from usuarios.models import Usuario

    carrinho = Carrinho(request)
    usuario = request.user

    if request.method == 'POST':
        # Dados mínimos para criar o Pedido
        nome_propriedade = getattr(usuario, 'nome', 'Propriedade do Cliente') or 'Propriedade do Cliente'
        cnpj = getattr(usuario, 'cpf', '00000000000000') or '00000000000000'
        hectares = 10
        cultivo_principal = 'soja'
        estado = getattr(usuario, 'estado', 'SP') or 'SP'
        cidade = getattr(usuario, 'cidade', 'Cidade') or 'Cidade'
        endereco = getattr(usuario, 'endereco', 'Endereço') or 'Endereço'
        cep = getattr(usuario, 'cep', '00000-000') or '00000-000'
        tipo_venda = request.POST.get('tipo_venda', 'avista')
        observacoes = ''
        total = sum(item['preco_total'] for item in carrinho)

        # Descobrir o vendedor a partir do primeiro produto do carrinho
        vendedor = None
        for item in carrinho:
            produto = item['produto']
            if hasattr(produto, 'seller') and produto.seller:
                vendedor = produto.seller.usuario if hasattr(produto.seller, 'usuario') else None
                break

        pedido = Pedido.objects.create(
            comprador=usuario,
            vendedor=vendedor,  # Agora será o usuário do vendedor
            nome_propriedade=nome_propriedade,
            cnpj=cnpj,
            hectares=hectares,
            cultivo_principal=cultivo_principal,
            estado=estado,
            cidade=cidade,
            endereco=endereco,
            cep=cep,
            tipo_venda=tipo_venda,
            observacoes=observacoes,
            total=total
        )

        # Cria vendas e itens do pedido para cada item do carrinho
        for item in carrinho:
            produto = item['produto']
            if not isinstance(produto, Product):
                continue
            quantidade = item['quantidade']
            preco_unitario = item['preco']
            vendedor = produto.seller if hasattr(produto, 'seller') and produto.seller else None
            Venda.objects.create(
                vendedor=vendedor,
                comprador=usuario,
                produto=produto,
                quantidade=quantidade,
                preco_unitario=preco_unitario,
                status='PENDENTE',
                pedido=pedido
            )
            # Buscar o Produto correto para o ItemPedido
            produto_real = Produto.objects.filter(id=produto.id).first()
            ItemPedido.objects.create(
                pedido=pedido,
                produto=produto_real,
                quantidade=quantidade,
                preco_unitario=preco_unitario,
                total=quantidade * preco_unitario
            )
        carrinho.limpar()
        messages.success(request, 'Pedido registrado com sucesso!')
        return redirect('core:pedidos')

    itens = [item for item in carrinho if isinstance(item['produto'], Product)]
    if not itens:
        messages.error(request, 'Seu carrinho está vazio.')
        return redirect('core:carrinho')

    total = sum(item['preco_total'] for item in itens)
    context = {
        'carrinho': {
            'itens': itens,
            'total': total
        }
    }
    return render(request, 'core/checkout.html', context)

@login_required
def pedidos(request):
    # Filtros
    status = request.GET.get('status')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    
    # Obter pedidos do usuário
    pedidos = Pedido.objects.filter(comprador=request.user).order_by('-data_criacao')
    
    # Aplicar filtros
    if status:
        pedidos = pedidos.filter(status=status)
    if data_inicio:
        try:
            data_inicio = timezone.datetime.strptime(data_inicio, '%Y-%m-%d')
            pedidos = pedidos.filter(data_criacao__gte=data_inicio)
        except ValueError:
            pass
    if data_fim:
        try:
            data_fim = timezone.datetime.strptime(data_fim, '%Y-%m-%d')
            data_fim = data_fim.replace(hour=23, minute=59, second=59)
            pedidos = pedidos.filter(data_criacao__lte=data_fim)
        except ValueError:
            pass
    
    context = {
        'pedidos': pedidos,
        'status_choices': Pedido.STATUS_CHOICES,
        'status_selecionado': status,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
    }
    return render(request, 'core/pedidos.html', context)

@login_required
@user_passes_test(is_superadmin)
def superadmin_compras_vendedores(request):
    if not request.user.is_superuser and not request.user.is_staff:
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return redirect('core:index')
    
    # Filtros
    vendedor_id = request.GET.get('vendedor')
    status = request.GET.get('status')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    
    # Query base
    pedidos = Pedido.objects.all().order_by('-data_criacao')
    pedidos = pedidos.filter(vendedor__isnull=False)
    
    # Aplicar filtros
    if vendedor_id:
        pedidos = pedidos.filter(vendedor_id=vendedor_id)
    if status:
        pedidos = pedidos.filter(status=status)
    if data_inicio:
        pedidos = pedidos.filter(data_criacao__date__gte=data_inicio)
    if data_fim:
        pedidos = pedidos.filter(data_criacao__date__lte=data_fim)
    
    # Obter lista de vendedores para o filtro
    vendedores = Vendedor.objects.all()
    
    # Status choices para o filtro
    status_choices = Pedido.STATUS_CHOICES
    
    context = {
        'pedidos': pedidos,
        'vendedores': vendedores,
        'status_choices': status_choices,
    }
    
    return render(request, 'core/superadmin_compras_vendedores.html', context)

def solicitar_compra(request, product_id):
    if request.method == 'POST':
        produto = get_object_or_404(Product, id=product_id)
        quantidade = request.POST.get('quantidade', 1)
        observacoes = request.POST.get('observacoes', '')
        
        try:
            quantidade = int(quantidade)
            if quantidade <= 0:
                raise ValueError('Quantidade inválida')
                
            carrinho = Carrinho(request)
            carrinho.adicionar(produto, quantidade)
            
            messages.success(request, f'{produto.name} adicionado ao carrinho!')
            return redirect('core:carrinho')
            
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('core:produto_detalhe', produto_id=product_id)
            
    return redirect('core:produto_detalhe', produto_id=product_id)

@login_required
@is_seller
def encerrar_caso(request, mensagem_id):
    """View para encerrar um caso de suporte"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Método não permitido'}, status=405)
    
    try:
        # Busca a mensagem usando o ID e o vendedor atual
        mensagem = get_object_or_404(
            MensagemSuporte, 
            id=mensagem_id,
            vendedor__usuario=request.user
        )
        
        # Verifica se a mensagem já foi respondida e não está fechada
        if not mensagem.respondida:
            return JsonResponse({
                'error': 'Não é possível encerrar um caso que ainda não foi respondido'
            }, status=400)
            
        if mensagem.encerrado:
            return JsonResponse({
                'error': 'Este caso já está encerrado'
            }, status=400)
        
        # Encerra o caso
        mensagem.encerrado = True
        mensagem.data_encerramento = timezone.now()
        mensagem.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Caso encerrado com sucesso!'
        })
        
    except MensagemSuporte.DoesNotExist:
        return JsonResponse({
            'error': 'Mensagem não encontrada'
        }, status=404)
    except Exception as e:
        logger.error(f'Erro ao encerrar caso: {str(e)}')
        return JsonResponse({
            'error': 'Erro ao encerrar o caso'
        }, status=500)

@login_required
@user_passes_test(is_superadmin)
def reprovar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    if pedido.status != 'AGUARDANDO_APROVACAO':
        messages.error(request, 'Só é possível reprovar pedidos aguardando aprovação.')
        return redirect('core:superadmin_pedidos')
    if request.method == 'POST':
        justificativa = request.POST.get('justificativa', '').strip()
        if not justificativa:
            messages.error(request, 'A justificativa é obrigatória para reprovar um pedido.')
            return render(request, 'core/pedido_reprovar.html', {'pedido': pedido})
        pedido.status = 'REPROVADO'
        pedido.reprovado_por = request.user
        pedido.reprovado_em = timezone.now()
        pedido.justificativa_reprovacao = justificativa
        pedido.aprovado_por = None
        pedido.aprovado_em = None
        pedido.save()
        messages.success(request, f'Pedido #{pedido.id} reprovado com sucesso!')
        return redirect('core:superadmin_pedidos')
    return render(request, 'core/pedido_reprovar.html', {'pedido': pedido})

@login_required
@user_passes_test(is_superadmin)
def reprovar_vendedor(request, vendedor_id):
    """Reprova um vendedor, exigindo justificativa"""
    vendedor = get_object_or_404(Vendedor, id=vendedor_id)
    if request.method == 'POST':
        justificativa = request.POST.get('justificativa_recusa', '').strip()
        if not justificativa:
            messages.error(request, 'A justificativa da recusa é obrigatória.')
            return redirect('core:seller_detail', seller_id=vendedor.id)
        vendedor.usuario.is_active = False
        vendedor.status_aprovacao = 'RECUSADO'
        vendedor.justificativa_recusa = justificativa
        vendedor.usuario.save()
        vendedor.save()
        messages.success(request, 'Vendedor reprovado com sucesso!')
    return redirect('core:listar_vendedores')

@login_required
def pedido_cancel(request, pedido_id):
    """Cancela um pedido"""
    pedido = get_object_or_404(Pedido, id=pedido_id)
    if pedido.status == 'AGUARDANDO_APROVACAO':
        pedido.status = 'CANCELADO'
        pedido.save()
        messages.success(request, 'Pedido cancelado com sucesso!')
    else:
        messages.error(request, 'Este pedido não pode ser cancelado.')
    return redirect('core:pedidos')

@login_required
@user_passes_test(is_superadmin)
def superadmin_products(request):
    """Lista todos os produtos para o superadmin"""
    produtos = Produto.objects.all().order_by('-created_at')
    return render(request, 'core/superadmin_products.html', {'produtos': produtos})

@login_required
@user_passes_test(is_superadmin)
def superadmin_product_create(request):
    """Cria um novo produto como superadmin"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto criado com sucesso!')
            return redirect('core:superadmin_products')
    else:
        form = ProductForm()
    return render(request, 'core/superadmin_product_form.html', {'form': form})

@login_required
@user_passes_test(is_superadmin)
def superadmin_product_delete(request, pk):
    """Deleta um produto como superadmin"""
    produto = get_object_or_404(Produto, pk=pk)
    if request.method == 'POST':
        produto.delete()
        messages.success(request, 'Produto deletado com sucesso!')
        return redirect('core:superadmin_products')
    return render(request, 'core/superadmin_product_confirm_delete.html', {'produto': produto})

@login_required
@user_passes_test(is_vendedor)
def seller_products(request):
    """Lista os produtos do vendedor"""
    produtos = Produto.objects.filter(vendedor=request.user.vendedor)
    return render(request, 'core/seller_products.html', {'produtos': produtos})

@login_required
def carrinho(request):
    """Mostra o carrinho de compras e exibe o formulário de venda a prazo se necessário"""
    from .forms import VendaPrazoForm
    carrinho = Carrinho(request)
    form = VendaPrazoForm()
    return render(request, 'core/carrinho.html', {'carrinho': carrinho, 'form': form})

@login_required
def adicionar_ao_carrinho(request, product_id):
    """Adiciona um produto ao carrinho (apenas Product do core.models)"""
    from .models import Product
    produto = get_object_or_404(Product, id=product_id)
    carrinho = Carrinho(request)
    quantidade = int(request.POST.get('quantidade', 1))
    carrinho.adicionar(produto, quantidade)
    messages.success(request, 'Produto adicionado ao carrinho!')
    return redirect('core:carrinho')

@login_required
def remover_do_carrinho(request, product_id):
    """Remove um produto do carrinho"""
    carrinho = Carrinho(request)
    produto = get_object_or_404(Produto, id=product_id)
    carrinho.remover(produto)
    messages.success(request, 'Produto removido do carrinho!')
    return redirect('core:carrinho')

@login_required
@user_passes_test(is_superadmin)
def listar_vendedores(request):
    """Lista todos os vendedores"""
    vendedores = Vendedor.objects.all().order_by('-created_at')
    return render(request, 'core/listar_vendedores.html', {'vendedores': vendedores})

@login_required
@user_passes_test(is_superadmin)
def aprovar_vendedor(request, vendedor_id):
    """Aprova um vendedor, inclusive se já foi recusado"""
    vendedor = get_object_or_404(Vendedor, id=vendedor_id)
    vendedor.usuario.is_active = True
    vendedor.status_aprovacao = 'APROVADO'
    vendedor.justificativa_recusa = ''  # Limpa justificativa ao aprovar
    vendedor.usuario.save()
    vendedor.save()
    messages.success(request, 'Vendedor aprovado com sucesso!')
    return redirect('core:listar_vendedores')

@login_required
@user_passes_test(is_superadmin)
def aprovar_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id=pedido_id)
    if pedido.status != 'AGUARDANDO_APROVACAO':
        messages.error(request, 'Só é possível aprovar pedidos aguardando aprovação.')
        return redirect('core:superadmin_pedidos')
    if request.method == 'POST':
        pedido.status = 'APROVADO'
        pedido.aprovado_por = request.user
        pedido.aprovado_em = timezone.now()
        pedido.justificativa_reprovacao = ''
        pedido.reprovado_por = None
        pedido.reprovado_em = None
        pedido.save()
        messages.success(request, f'Pedido #{pedido.id} aprovado com sucesso!')
        return redirect('core:superadmin_pedidos')
    return render(request, 'core/pedido_approve.html', {'pedido': pedido})
