from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate, logout
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
from .models import Product, Order, OrderItem, VendorApplication, SellerRegistration, MensagemSuporte, SolicitacaoProduto
from .forms import ProductForm, OrderForm, OrderItemFormSet, SellerRegistrationForm, LoginForm, SolicitacaoProdutoForm, SellerProfileForm, AdminProfileForm
from .utils import validate_file_upload, validate_cpf, is_superadmin, is_vendedor
from django.http import HttpResponse, JsonResponse
import logging
from django.db.models import Q
from django.db.models.functions import TruncMonth
from django.core.paginator import Paginator
from vendedor.models import Vendedor
from usuarios.models import Usuario
from produtos.models import Produto
from vendas.models import Venda, Pedido
import os
import json
from django.views.decorators.csrf import csrf_exempt
from .decorators import superuser_required, is_seller
from django.db import models

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
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            
            # Criar o vendedor associado
            vendedor = Vendedor.objects.create(
                usuario=user,
                razao_social=form.cleaned_data['razao_social'],
                nome_fantasia=form.cleaned_data['nome_fantasia'],
                cnpj=form.cleaned_data['cnpj'],
                inscricao_estadual=form.cleaned_data['inscricao_estadual'],
                telefone=form.cleaned_data['telefone'],
                rua=form.cleaned_data['rua'],
                numero=form.cleaned_data['numero'],
                cidade=form.cleaned_data['cidade'],
                estado=form.cleaned_data['estado'],
                cep=form.cleaned_data['cep'],
                hectares_atendidos=form.cleaned_data['hectares_atendidos'],
                rg=form.cleaned_data['rg'],
                cnh=form.cleaned_data['cnh']
            )
            
            send_confirmation_email(user, request)
            messages.success(request, 'Por favor, confirme seu email para completar o registro.')
            return redirect('core:login')
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
    seller = request.user.vendedor
    total_products = Product.objects.filter(seller=seller).count()
    total_orders = Order.objects.filter(seller=seller).count()
    total_sales = Order.objects.filter(seller=seller, status='delivered').aggregate(total=Sum('total_value'))['total'] or 0
    
    recent_orders = Order.objects.filter(seller=seller).order_by('-created_at')[:5]
    recent_products = Product.objects.filter(seller=seller).order_by('-created_at')[:5]
    
    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_sales': total_sales,
        'recent_orders': recent_orders,
        'recent_products': recent_products,
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
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'core/product_detail.html', {'product': product})

@login_required
def profile(request):
    """Mostra o perfil do usuário"""
    return render(request, 'core/profile.html')

@login_required
@user_passes_test(is_superadmin)
def seller_edit(request, seller_id):
    """Edita um vendedor"""
    seller = get_object_or_404(Vendedor, id=seller_id)
    if request.method == 'POST':
        # Atualizar dados do usuário
        seller.usuario.first_name = request.POST.get('first_name')
        seller.usuario.last_name = request.POST.get('last_name')
        seller.usuario.email = request.POST.get('email')
        seller.usuario.cpf = request.POST.get('cpf')
        seller.usuario.document_type = request.POST.get('document_type')
        seller.usuario.cep = request.POST.get('cep')
        seller.usuario.rua = request.POST.get('rua')
        seller.usuario.numero = request.POST.get('numero')
        seller.usuario.bairro = request.POST.get('bairro')
        seller.usuario.cidade = request.POST.get('cidade')
        seller.usuario.estado = request.POST.get('estado')
        
        # Atualizar dados do vendedor
        seller.telefone = request.POST.get('phone')
        seller.razao_social = request.POST.get('razao_social')
        seller.nome_fantasia = request.POST.get('nome_fantasia')
        seller.cnpj = request.POST.get('cnpj')
        seller.inscricao_estadual = request.POST.get('inscricao_estadual')
        seller.hectares_atendidos = request.POST.get('hectares_atendidos')
        
        # Processar redefinição de senha
        new_password = request.POST.get('new_password')
        if new_password:
            seller.usuario.set_password(new_password)
        
        # Salvar alterações
        seller.usuario.save()
        seller.save()
        
        messages.success(request, 'Vendedor atualizado com sucesso!')
        return redirect('core:seller_detail', seller_id=seller.id)
        
    return render(request, 'core/seller_edit.html', {'seller': seller})

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
    sellers = Vendedor.objects.all()
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
    # Filtros
    category = request.GET.get('category')
    status = request.GET.get('status')
    search_query = request.GET.get('search')

    # Query base
    products = Product.objects.all()

    # Aplicar filtros
    if category:
        products = products.filter(product_type=category)
    if status:
        is_active = status == 'active'
        products = products.filter(is_active=is_active)
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Ordenar por data de criação
    products = products.order_by('-created_at')

    # Categorias para o filtro
    categories = [
        {'id': choice[0], 'name': choice[1]} 
        for choice in Product.PRODUCT_TYPE_CHOICES
    ]
    
    context = {
        'products': products,
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
    seller = request.user.vendedor
    products = Product.objects.filter(seller=seller)
    return render(request, 'core/seller_products.html', {'products': products})

@login_required
def carrinho(request):
    """Mostra o carrinho de compras"""
    return render(request, 'core/carrinho.html')

def adicionar_ao_carrinho(request, product_id):
    """Adiciona um produto ao carrinho"""
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    cart_item = cart.get(str(product_id), {'quantity': 0, 'price': str(product.price)})
    cart_item['quantity'] += 1
    cart[str(product_id)] = cart_item
    request.session['cart'] = cart
    messages.success(request, 'Produto adicionado ao carrinho!')
    return redirect('core:carrinho')

def remover_do_carrinho(request, product_id):
    """Remove um produto do carrinho"""
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
        messages.success(request, 'Produto removido do carrinho!')
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

@login_required
@user_passes_test(lambda u: u.is_superuser)
def superadmin_product_update(request, pk):
    """Atualiza um produto como superadmin"""
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto atualizado com sucesso!')
            return redirect('core:superadmin_products')
    else:
        form = ProductForm(instance=product)
    return render(request, 'core/superadmin_product_form.html', {'form': form})

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

    # Filtra os produtos
    produtos = Produto.objects.all()

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
        'categorias': Produto.CATEGORIAS,
        'tipos': Produto.TIPOS,
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
    if request.method == 'POST':
        form = SolicitacaoProdutoForm(request.POST)
        if form.is_valid():
            solicitacao = form.save(commit=False)
            solicitacao.vendedor = request.user
            solicitacao.save()
            messages.success(request, 'Solicitação enviada com sucesso!')
            return redirect('core:minhas_solicitacoes')
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
def superadmin_solicitacoes(request):
    """Lista todas as solicitações de produto"""
    solicitacoes = SolicitacaoProduto.objects.all()
    return render(request, 'core/superadmin_solicitacoes.html', {'solicitacoes': solicitacoes})

@login_required
def superadmin_detalhes_solicitacao(request, pk):
    """Mostra os detalhes de uma solicitação para o superadmin"""
    solicitacao = get_object_or_404(SolicitacaoProduto, pk=pk)
    if request.method == 'POST':
        resposta = request.POST.get('resposta')
        solicitacao.resposta_superadmin = resposta
        solicitacao.status = 'ANALISADO'
        solicitacao.save()
        messages.success(request, 'Resposta enviada com sucesso!')
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
            solicitacao.save()
            messages.success(request, 'Solicitação enviada com sucesso!')
            return redirect('core:minhas_solicitacoes')
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
    pedidos = Pedido.objects.filter(vendedor=vendedor).order_by('-data_pedido')
    
    # Filtros
    status = request.GET.get('status')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    
    if status:
        pedidos = pedidos.filter(status=status)
    if data_inicio:
        pedidos = pedidos.filter(data_pedido__gte=data_inicio)
    if data_fim:
        pedidos = pedidos.filter(data_pedido__lte=data_fim)
    
    context = {
        'pedidos': pedidos,
        'status_choices': Pedido.STATUS_CHOICES,
        'status_selecionado': status,
        'data_inicio': data_inicio,
        'data_fim': data_fim,
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
    
    # Consulta base
    pedidos = Pedido.objects.filter(vendedor=usuario).order_by('-data_pedido')
    
    # Aplicar filtros
    if status:
        pedidos = pedidos.filter(status=status)
    if data_inicio:
        pedidos = pedidos.filter(data_pedido__gte=data_inicio)
    if data_fim:
        pedidos = pedidos.filter(data_pedido__lte=data_fim)
    
    context = {
        'vendedor': vendedor,
        'pedidos': pedidos,
        'status_choices': Pedido.STATUS_CHOICES,
    }
    return render(request, 'core/historico_pedidos.html', context)
