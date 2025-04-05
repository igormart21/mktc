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
from .forms import ProductForm, OrderForm, OrderItemFormSet, SellerRegistrationForm, LoginForm, SolicitacaoProdutoForm
from .utils import validate_file_upload, validate_cpf
from django.http import HttpResponse, JsonResponse
import logging
from django.db.models import Q
from django.db.models.functions import TruncMonth
from django.core.paginator import Paginator
from vendedor.models import Vendedor
from usuarios.models import Usuario
from produtos.models import Produto
from vendas.models import Venda
import os
import json
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)

def is_superadmin(user):
    return user.is_superuser

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
    
    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_sellers': total_sellers,
        'total_users': total_users,
        'recent_orders': recent_orders,
        'recent_products': recent_products,
        'recent_sellers': recent_sellers,
    }
    return render(request, 'core/superadmin_dashboard.html', context)

@login_required
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
        form = SellerRegistrationForm(request.POST, instance=seller)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vendedor atualizado com sucesso!')
            return redirect('core:listar_vendedores')
    else:
        form = SellerRegistrationForm(instance=seller)
    return render(request, 'core/seller_form.html', {'form': form})

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
    seller.usuario.aprovado = True
    seller.usuario.save()
    messages.success(request, 'Vendedor aprovado com sucesso!')
    return redirect('core:listar_vendedores')

@login_required
@user_passes_test(is_superadmin)
def reprovar_vendedor(request, vendedor_id):
    """Reprova um vendedor"""
    seller = get_object_or_404(Vendedor, id=vendedor_id)
    seller.usuario.aprovado = False
    seller.usuario.save()
    messages.success(request, 'Vendedor reprovado com sucesso!')
    return redirect('core:listar_vendedores')

@login_required
@user_passes_test(is_superadmin)
def superadmin_products(request):
    """Lista todos os produtos para o superadmin"""
    products = Product.objects.all()
    return render(request, 'core/superadmin_products.html', {'products': products})

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

@login_required
@user_passes_test(lambda u: u.is_superuser)
def cadastrar_vendedor(request):
    """Cadastra um novo vendedor"""
    if request.method == 'POST':
        form = SellerRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()
            
            # Criar o vendedor associado ao usuário
            vendedor = Vendedor.objects.create(
                usuario=user,
                razao_social=form.cleaned_data['nome'],
                nome_fantasia=form.cleaned_data['nome'],
                cnpj=form.cleaned_data.get('cpf'),
                telefone=form.cleaned_data['telefone'],
                endereco=form.cleaned_data['rua'],
                cep=form.cleaned_data['cep']
            )
            
            messages.success(request, 'Vendedor cadastrado com sucesso!')
            return redirect('core:listar_vendedores')
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
    products = Product.objects.filter(is_active=True)
    return render(request, 'core/catalogo.html', {'products': products})

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
    seller = request.user.vendedor
    if request.method == 'POST':
        form = SellerRegistrationForm(request.POST, instance=seller)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('core:seller_profile')
    else:
        form = SellerRegistrationForm(instance=seller)
    return render(request, 'core/seller_profile.html', {'form': form})

@login_required
def produto_detalhe(request, produto_id):
    """Mostra os detalhes de um produto"""
    produto = get_object_or_404(Produto, id=produto_id)
    return render(request, 'core/produto_detalhe.html', {'produto': produto})
