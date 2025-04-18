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
from .models import Product, Order, OrderItem, VendorApplication, SellerRegistration, MensagemSuporte, SolicitacaoProduto, Pedido, Venda, Vendedor
from .forms import ProductForm, OrderForm, OrderItemForm, SellerRegistrationForm, LoginForm, SolicitacaoProdutoForm, SellerProfileForm, AdminProfileForm, VendaPrazoForm
from .utils import validate_file_upload, validate_cpf, is_superadmin, is_vendedor
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, Http404
import logging
from django.db.models import Q
from django.db.models.functions import TruncMonth
from django.core.paginator import Paginator
from vendedor.models import Vendedor
from usuarios.models import Usuario
from produtos.models import Produto
from vendas.models import Pedido, Venda, ItemPedido
import os
import json
from django.views.decorators.csrf import csrf_exempt
from .decorators import superuser_required, is_seller
from django.db import models
from django.contrib.auth.hashers import check_password
from .carrinho import Carrinho
from django.utils.html import strip_tags
from django.contrib.auth import get_user_model
from decimal import Decimal

logger = logging.getLogger(__name__)

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
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
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
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_sellers = Vendedor.objects.count()
    total_users = Usuario.objects.count()
    
    recent_orders = Order.objects.order_by('-created_at')[:5]
    recent_products = Product.objects.order_by('-created_at')[:5]
    recent_sellers = Vendedor.objects.order_by('-created_at')[:5]
    vendas_pendentes = Venda.objects.filter(status='PENDENTE').order_by('-data_criacao')[:5]

    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_sellers': total_sellers,
        'total_users': total_users,
        'recent_orders': recent_orders,
        'recent_products': recent_products,
        'recent_sellers': recent_sellers,
        'vendas_pendentes': vendas_pendentes,
    }
    return render(request, 'core/superadmin_dashboard.html', context)

@login_required
@is_seller
def seller_dashboard(request):
    """Dashboard do vendedor"""
    try:
        vendedor = request.user.vendedor
    except Vendedor.DoesNotExist:
        messages.error(request, 'Você precisa ser um vendedor para acessar esta página.')
        return redirect('core:home')
        
    total_products = Produto.objects.filter(vendedor=vendedor).count()
    
    # Temporariamente substituindo as consultas problemáticas com valores seguros
    total_orders = 0  # Pedido.objects.filter(vendedor=request.user).count()
    total_sales = 0  # sum(pedido.total for pedido in pedidos_aprovados)
    recent_orders = []  # Pedido.objects.filter(vendedor=request.user).order_by('-data_pedido')[:5]
    recent_products = Produto.objects.filter(vendedor=vendedor).order_by('-created_at')[:5]
    
    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_sales': total_sales,
        'recent_orders': recent_orders,
        'recent_products': recent_products,
        'pedidos_pendentes': 0,  # Pedido.objects.filter(vendedor=request.user, status='PENDENTE').count(),
        'pedidos_aprovados': 0,  # Pedido.objects.filter(vendedor=request.user, status='APROVADO').count(),
        'pedidos_rejeitados': 0,  # Pedido.objects.filter(vendedor=request.user, status='REJEITADO').count(),
        'ultimos_pedidos': recent_orders,
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
    """Desativa um vendedor"""
    seller = get_object_or_404(Vendedor, id=seller_id)
    seller.usuario.is_active = False
    seller.usuario.save()
    messages.success(request, 'Vendedor desativado com sucesso!')
    return redirect('core:listar_vendedores')

@login_required
@user_passes_test(is_superadmin)
def seller_enable(request, seller_id):
    """Ativa um vendedor"""
    seller = get_object_or_404(Vendedor, id=seller_id)
    seller.usuario.is_active = True
    seller.usuario.save()
    messages.success(request, 'Vendedor ativado com sucesso!')
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
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.customer_name = request.user.get_full_name()
            order.customer_email = request.user.email
            order.save()
            messages.success(request, 'Pedido criado com sucesso!')
            return redirect('core:order_detail', order_id=order.id)
    else:
        form = OrderForm()
    return render(request, 'core/order_form.html', {'form': form})

@login_required
def order_detail(request, order_id):
    """Mostra os detalhes de um pedido"""
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'core/order_detail.html', {'order': order})

@login_required
def order_edit(request, order_id):
    """Edita um pedido"""
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pedido atualizado com sucesso!')
            return redirect('core:order_detail', order_id=order.id)
    else:
        form = OrderForm(instance=order)
    return render(request, 'core/order_form.html', {'form': form})

@login_required
def order_approve(request, order_id):
    """Aprova um pedido"""
    order = get_object_or_404(Order, id=order_id)
    order.status = 'processing'
    order.save()
    messages.success(request, 'Pedido aprovado com sucesso!')
    return redirect('core:order_detail', order_id=order.id)

@login_required
def order_cancel(request, order_id):
    """Cancela um pedido"""
    order = get_object_or_404(Order, id=order_id)
    order.status = 'cancelled'
    order.save()
    messages.success(request, 'Pedido cancelado com sucesso!')
    return redirect('core:order_detail', order_id=order.id)

def product_list(request):
    """Lista todos os produtos"""
    products = Product.objects.filter(is_active=True)
    return render(request, 'core/product_list.html', {'products': products})

@login_required
@user_passes_test(is_superadmin)
def listar_vendedores(request):
    """Lista todos os vendedores"""
    sellers = Vendedor.objects.all().order_by('-created_at')
    return render(request, 'core/seller_list.html', {'sellers': sellers})

@login_required
@user_passes_test(is_superadmin)
def aprovar_vendedor(request, vendedor_id):
    """Aprova um vendedor"""
    seller = get_object_or_404(Vendedor, id=vendedor_id)
    seller.usuario.is_active = True
    seller.usuario.save()
    seller.data_aprovacao = timezone.now()
    seller.save()
    messages.success(request, 'Vendedor aprovado com sucesso!')
    return redirect('core:listar_vendedores')

@login_required
@user_passes_test(is_superadmin)
def reprovar_vendedor(request, vendedor_id):
    """Reprova um vendedor"""
    seller = get_object_or_404(Vendedor, id=vendedor_id)
    seller.usuario.is_active = False
    seller.usuario.save()
    seller.data_aprovacao = None
    seller.save()
    messages.success(request, 'Vendedor reprovado com sucesso!')
    return redirect('core:listar_vendedores')

@login_required
@user_passes_test(is_superadmin)
def superadmin_products(request):
    """Lista todos os produtos para o superadmin"""
    category = request.GET.get('category')
    status = request.GET.get('status')
    search_query = request.GET.get('search')

    # Obter produtos tanto do modelo Produto quanto do modelo Product
    produtos_model = Produto.objects.all()
    
    try:
        # Tenta obter produtos do modelo Product também
        from core.models import Product
        product_model = Product.objects.all()
        
        # Converter campos do Product para mapeá-los para o formato do Produto
        products_converted = []
        for p in product_model:
            products_converted.append({
                'id': p.id,  # Removido o prefixo 'core_'
                'nome': p.name,
                'descricao': p.description,
                'preco': p.price,
                'categoria': p.product_type,
                'tipo': p.product_type,
                'ativo': p.is_active,
                'imagem': p.image.url if p.image else None,
                'created_at': p.created_at,
                'modelo': 'Product'  # Adicionado campo para identificar o modelo
            })
    except:
        products_converted = []
    
    # Aplicar filtros nos produtos do modelo Produto
    if category:
        produtos_model = produtos_model.filter(categoria=category)
    if status:
        is_active = status == 'active'
        produtos_model = produtos_model.filter(ativo=is_active)
    if search_query:
        produtos_model = produtos_model.filter(
            Q(nome__icontains=search_query) |
            Q(descricao__icontains=search_query)
        )

    # Ordenar por data de criação
    produtos_model = produtos_model.order_by('-created_at')
    
    # Converter produtos do modelo Produto para lista de dicionários para template
    produtos_list = []
    for produto in produtos_model:
        produto_dict = {
            'id': produto.pk,  # Removido o prefixo 'prod_'
            'nome': produto.nome,
            'descricao': produto.descricao,
            'preco': float(produto.preco) if produto.preco else 0,
            'volume_disponivel': float(produto.volume_disponivel) if produto.volume_disponivel else 0,
            'categoria': produto.get_categoria_display(),  # Agora usando o método
            'tipo': produto.get_tipo_display(),  # Agora usando o método
            'unidade_medida': produto.get_unidade_medida_display(),  # Agora usando o método
            'created_at': produto.created_at,
            'imagem': produto.imagem.url if produto.imagem else None,
            'ativo': produto.ativo,
            'modelo': 'Produto'  # Adicionado campo para identificar o modelo
        }
        produtos_list.append(produto_dict)
    
    # Combinar os produtos dos dois modelos
    all_products = produtos_list + products_converted
    
    # Categorias para o filtro
    categories = [
        {'id': choice[0], 'name': choice[1]} 
        for choice in Produto.CATEGORIA_CHOICES
    ]
    
    context = {
        'products': all_products,
        'categories': categories,
        'selected_category': category,
        'selected_status': status,
        'search_query': search_query,
    }
    return render(request, 'core/superadmin_products.html', context)

@login_required
@user_passes_test(is_superadmin)
def superadmin_product_create(request):
    """Cria um novo produto como superadmin"""
    if request.method == 'POST':
        print("="*50)
        print("Dados do POST recebidos:")
        for key, value in request.POST.items():
            print(f"{key}: {value}")
        print("Arquivos recebidos:", request.FILES)
        print("="*50)
        
        form = ProductForm(request.POST, request.FILES)
        print("Formulário é válido:", form.is_valid())
        if not form.is_valid():
            print("Erros do formulário:")
            for field, errors in form.errors.items():
                print(f"{field}: {errors}")
        
        if form.is_valid():
            try:
                product = form.save(commit=False)
                print("Produto antes de salvar:")
                for key, value in product.__dict__.items():
                    print(f"{key}: {value}")
                
                product.save()
                print("Produto salvo com sucesso! ID:", product.id)
                messages.success(request, 'Produto criado com sucesso!')
                return redirect('core:superadmin_products')
            except Exception as e:
                print("Erro ao salvar:", str(e))
                messages.error(request, f'Erro ao salvar o produto: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'title': 'Criar Novo Produto'
    }
    return render(request, 'core/superadmin_product_form.html', context)

@login_required
@user_passes_test(is_superadmin)
def superadmin_product_delete(request, pk):
    """Deleta um produto como superadmin"""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Produto deletado com sucesso!')
        return redirect('core:superadmin_products')
    return render(request, 'core/superadmin_product_confirm_delete.html', {'product': product})

@login_required
def seller_products(request):
    """Lista os produtos de um vendedor"""
    try:
        vendedor = request.user.vendedor
        if not vendedor.data_aprovacao:
            messages.error(request, 'Você precisa ser aprovado para visualizar seus produtos.')
            return redirect('core:dashboard')
            
        produtos = Produto.objects.filter(vendedor=vendedor).order_by('-created_at')
        
        # Filtros
        categoria = request.GET.get('categoria')
        status = request.GET.get('status')
        busca = request.GET.get('busca')
        
        if categoria:
            produtos = produtos.filter(categoria=categoria)
        if status:
            ativo = status == 'active'
            produtos = produtos.filter(ativo=ativo)
        if busca:
            produtos = produtos.filter(
                Q(nome__icontains=busca) |
                Q(descricao__icontains=busca)
            )
        
        context = {
            'products': produtos,
            'categorias': Produto.CATEGORIA_CHOICES,
            'categoria_selecionada': categoria,
            'status_selecionado': status,
            'busca': busca,
        }
        return render(request, 'core/seller_products.html', context)
    except Vendedor.DoesNotExist:
        messages.error(request, 'Você precisa ser um vendedor para acessar esta página.')
        return redirect('core:dashboard')

@login_required
def carrinho(request):
    if request.method == 'POST':
        tipo_venda = request.POST.get('tipo_venda')
        carrinho = Carrinho(request)
        
        if not carrinho:
            messages.error(request, 'Seu carrinho está vazio.')
            return redirect('core:carrinho')
            
        # Obter o primeiro item do carrinho para referência
        primeiro_item = next(iter(carrinho), None)
        if not primeiro_item:
            messages.error(request, 'Seu carrinho está vazio.')
            return redirect('core:carrinho')
        
        if tipo_venda == 'avista':
            # Criar pedido
            pedido = Pedido.objects.create(
                comprador=request.user,
                vendedor=None,  # Não associar vendedor
                produto=primeiro_item['produto'],
                quantidade=1,  # Será atualizado pelos itens
                preco_unitario=0,  # Será atualizado pelos itens
                total=0,  # Será atualizado pelos itens
                status='PENDENTE',
                nome_propriedade='A definir',
                cnpj='A definir',
                hectares=0,
                cultivo_principal='outros',
                estado='SP',
                cidade='A definir',
                endereco='A definir',
                cep='00000000'
            )
            
            # Criar itens do pedido
            for item in carrinho:
                ItemPedido.objects.create(
                    pedido=pedido,
                    produto=item['produto'],
                    quantidade=item['quantidade'],
                    preco_unitario=item['preco']
                )
            
            carrinho.limpar()
            messages.success(request, 'Pedido realizado com sucesso!')
            return redirect('core:pedidos')
            
        elif tipo_venda == 'prazo':
            venda_prazo_form = VendaPrazoForm(request.POST, request.FILES)
            if venda_prazo_form.is_valid():
                # Criar pedido
                pedido = Pedido.objects.create(
                    comprador=request.user,
                    vendedor=None,  # Não associar vendedor
                    produto=primeiro_item['produto'],
                    quantidade=1,  # Será atualizado pelos itens
                    preco_unitario=0,  # Será atualizado pelos itens
                    total=0,  # Será atualizado pelos itens
                    status='PENDENTE',
                    nome_propriedade='A definir',
                    cnpj='A definir',
                    hectares=0,
                    cultivo_principal='outros',
                    estado='SP',
                    cidade='A definir',
                    endereco='A definir',
                    cep='00000000'
                )
                
                # Criar itens do pedido
                for item in carrinho:
                    ItemPedido.objects.create(
                        pedido=pedido,
                        produto=item['produto'],
                        quantidade=item['quantidade'],
                        preco_unitario=item['preco']
                    )
                
                carrinho.limpar()
                messages.success(request, 'Pedido realizado com sucesso!')
                return redirect('core:pedidos')
            else:
                messages.error(request, 'Por favor, corrija os erros no formulário.')
                return render(request, 'core/carrinho.html', {
                    'carrinho': carrinho,
                    'venda_prazo_form': venda_prazo_form
                })
    else:
        carrinho = Carrinho(request)
        venda_prazo_form = VendaPrazoForm()
        return render(request, 'core/carrinho.html', {
            'carrinho': carrinho,
            'venda_prazo_form': venda_prazo_form
        })

def adicionar_ao_carrinho(request, product_id):
    produto = get_object_or_404(Product, id=product_id)
    carrinho = Carrinho(request)
    carrinho.adicionar(produto)
    messages.success(request, f'{produto.name} adicionado ao carrinho!')
    return redirect('core:carrinho')

def remover_do_carrinho(request, product_id):
    produto = get_object_or_404(Produto, id=product_id)
    carrinho = Carrinho(request)
    carrinho.remover(produto)
    messages.success(request, f'{produto.nome} removido do carrinho!')
    return redirect('core:carrinho')

@login_required
@user_passes_test(is_superadmin)
def superadmin_orders(request):
    """Lista todos os pedidos para o superadmin"""
    orders = Order.objects.all()
    return render(request, 'core/superadmin_orders.html', {'orders': orders})

@login_required
@user_passes_test(is_superadmin)
def superadmin_order_detail(request, order_id):
    """Mostra os detalhes de um pedido para o superadmin"""
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'core/superadmin_order_detail.html', {'order': order})

@login_required
@user_passes_test(is_superadmin)
def superadmin_order_delete(request, order_id):
    """Deleta um pedido como superadmin"""
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        order.delete()
        messages.success(request, 'Pedido deletado com sucesso!')
        return redirect('core:superadmin_orders')
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
    return render(request, 'core/suporte.html')

@login_required
@user_passes_test(is_superadmin)
def superadmin_suporte(request):
    """Página de suporte para superadmin"""
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
                    messages.error(request, f"{form.fields[field].label}: {error}")
    else:
        form = SolicitacaoProdutoForm()
    
    return render(request, 'core/solicitar_produto.html', {'form': form})

@login_required
def minhas_solicitacoes(request):
    """Lista as solicitações de produto do usuário"""
    solicitacoes = SolicitacaoProduto.objects.filter(vendedor=request.user)
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
    if request.method == 'POST':
        form = SolicitacaoProdutoForm(request.POST)
        if form.is_valid():
            solicitacao = form.save(commit=False)
            solicitacao.vendedor = request.user
            
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
    """Lista todas as vendas pendentes de aprovação"""
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
    
    # Temporariamente substituindo a consulta problemática
    # pedidos = Pedido.objects.filter(vendedor=vendedor).order_by('-data_pedido')
    pedidos = []
    
    # Filtros
    status = request.GET.get('status')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    
    context = {
        'pedidos': pedidos,
        'status_choices': [('PENDENTE', 'Pendente'), ('APROVADO', 'Aprovado'), ('REJEITADO', 'Rejeitado')],  # Substituição temporária para Pedido.STATUS_CHOICES
        'status_selecionado': status,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
        'aviso_manutencao': 'Sistema em manutenção. Histórico de pedidos temporariamente indisponível.'
    }
    return render(request, 'core/historico_pedidos.html', context)

@login_required
@user_passes_test(is_superadmin)
def historico_pedidos_vendedor_admin(request, vendedor_id):
    vendedor = get_object_or_404(Vendedor, id=vendedor_id)
    usuario = vendedor.usuario  # Obtém o objeto Usuario associado ao vendedor
    
    # Filtros
    status = request.GET.get('status')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    
    # Temporariamente substituindo a consulta problemática
    # pedidos = Pedido.objects.filter(vendedor=usuario).order_by('-data_pedido')
    pedidos = []
    
    context = {
        'vendedor': vendedor,
        'pedidos': pedidos,
        'status_choices': [('PENDENTE', 'Pendente'), ('APROVADO', 'Aprovado'), ('REJEITADO', 'Rejeitado')],  # Substituição temporária para Pedido.STATUS_CHOICES
        'aviso_manutencao': 'Sistema em manutenção. Histórico de pedidos temporariamente indisponível.'
    }
    return render(request, 'core/historico_pedidos.html', context)

@login_required
def checkout(request):
    if request.method == 'POST':
        # Obter vendas pendentes do usuário
        vendas = Venda.objects.filter(comprador=request.user, status='PENDENTE')
        
        if not vendas.exists():
            messages.error(request, 'Seu carrinho está vazio.')
            return redirect('core:carrinho')

        # Atualizar status das vendas para PROCESSANDO
        for venda in vendas:
            venda.status = 'PROCESSANDO'
            venda.save()

        messages.success(request, 'Pedido registrado com sucesso!')
        return redirect('core:pedidos')

    # Se for GET, mostrar o formulário
    vendas = Venda.objects.filter(comprador=request.user, status='PENDENTE')
    if not vendas.exists():
        messages.error(request, 'Seu carrinho está vazio.')
        return redirect('core:carrinho')

    # Calcular o total do carrinho
    total = sum(venda.quantidade * venda.preco_unitario for venda in vendas)
    
    context = {
        'carrinho': {
            'itens': vendas,
            'total': total
        }
    }
    return render(request, 'core/checkout.html', context)

@login_required
def pedidos(request):
    pedidos = Pedido.objects.filter(comprador=request.user).order_by('-data_pedido')
    
    context = {
        'pedidos': pedidos
    }
    return render(request, 'core/pedidos.html', context)

@login_required
@user_passes_test(is_superadmin)
def superadmin_compras_vendedores(request):
    """Lista o histórico de compras de todos os vendedores"""
    # Filtros
    vendedor_id = request.GET.get('vendedor')
    status = request.GET.get('status')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    
    # Lista de vendedores para o filtro
    vendedores = Vendedor.objects.all().order_by('nome_fantasia')
    
    # Obter todas as vendas (temporariamente usaremos o modelo Venda)
    vendas = Venda.objects.filter(status__in=['ACEITO', 'PROCESSANDO']).order_by('-data_criacao')
    
    # Aplicar filtros
    if vendedor_id:
        try:
            vendedor = Vendedor.objects.get(id=vendedor_id)
            vendas = vendas.filter(vendedor=vendedor)
        except Vendedor.DoesNotExist:
            pass
    
    if status:
        vendas = vendas.filter(status=status)
        
    if data_inicio:
        try:
            data_inicio = timezone.datetime.strptime(data_inicio, '%Y-%m-%d')
            vendas = vendas.filter(data_criacao__gte=data_inicio)
        except ValueError:
            pass
            
    if data_fim:
        try:
            data_fim = timezone.datetime.strptime(data_fim, '%Y-%m-%d')
            data_fim = data_fim.replace(hour=23, minute=59, second=59)
            vendas = vendas.filter(data_criacao__lte=data_fim)
        except ValueError:
            pass
    
    # Paginação
    paginator = Paginator(vendas, 20)  # 20 itens por página
    page = request.GET.get('page')
    vendas_paginadas = paginator.get_page(page)
    
    context = {
        'vendas': vendas_paginadas,
        'vendedores': vendedores,
        'filtro_vendedor': vendedor_id,
        'filtro_status': status,
        'filtro_data_inicio': data_inicio,
        'filtro_data_fim': data_fim,
        'status_choices': [
            ('PENDENTE', 'Pendente'),
            ('PROCESSANDO', 'Processando'),
            ('ACEITO', 'Aceito'),
            ('REJEITADO', 'Rejeitado')
        ],
    }
    return render(request, 'core/superadmin_compras_vendedores.html', context)

@login_required
@superuser_required
def superadmin_pedidos(request):
    from vendas.models import Pedido  # Importa o modelo correto
    pedidos = Pedido.objects.all().order_by('-data_pedido')
    
    # Filtros (opcional, pode ajustar conforme necessário)
    status = request.GET.get('status')
    tipo_venda = request.GET.get('tipo_venda')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    
    if status:
        pedidos = pedidos.filter(status=status)
    
    if tipo_venda:
        pedidos = pedidos.filter(tipo_venda=tipo_venda)
    
    if data_inicio:
        pedidos = pedidos.filter(data_pedido__date__gte=data_inicio)
    
    if data_fim:
        pedidos = pedidos.filter(data_pedido__date__lte=data_fim)
    
    context = {
        'pedidos': pedidos,
        'status_choices': Pedido.STATUS_CHOICES,
    }
    
    return render(request, 'core/superadmin_pedidos.html', context)

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
