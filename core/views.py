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
from .models import Product, Category, Order, OrderItem, VendorApplication, SellerRegistration, MensagemSuporte, SolicitacaoProduto
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
    categories = Category.objects.all()
    products = Product.objects.filter(is_active=True).order_by('-created_at')[:6]
    
    context = {
        'categories': categories,
        'products': products,
    }
    return render(request, 'core/home.html', context)

def login_view(request):
    """View de login"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bem-vindo ao sistema, {username}!')
                if user.is_superuser:
                    return redirect('core:superadmin_dashboard')
                elif hasattr(user, 'vendedor'):
                    return redirect('core:seller_dashboard')
                return redirect('core:home')
            else:
                messages.error(request, 'Credenciais inválidas. Verifique seu usuário e senha.')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    """View de logout"""
    logout(request)
    messages.info(request, 'Sessão encerrada com sucesso.')
    return redirect('core:login')

def generate_email_confirmation_token(user):
    return urlsafe_base64_encode(force_bytes(user.pk))

def confirm_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = Usuario.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        user = None

    if user is not None:
        user.is_active = True
        user.save()
        messages.success(request, 'Seu e-mail foi confirmado com sucesso! Agora você pode fazer login.')
        return redirect('core:login')
    else:
        messages.error(request, 'O link de confirmação é inválido ou já foi usado.')
        return redirect('core:home')

def send_confirmation_email(user, request):
    try:
        token = generate_email_confirmation_token(user)
        confirmation_url = request.build_absolute_uri(f'/confirmar-email/{token}/')
        
        subject = 'Confirme seu e-mail - AgroMais'
        message = render_to_string('registration/email_confirmation.html', {
            'user': user,
            'confirmation_url': confirmation_url,
        })
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
            html_message=message,  # Adiciona versão HTML do e-mail
        )
        
        return True
    except Exception as e:
        # Em desenvolvimento, loga o erro
        if settings.DEBUG:
            print(f"Erro ao enviar e-mail de confirmação: {str(e)}")
        return False

def seller_registration(request):
    """Página de registro de vendedor"""
    if request.method == 'POST':
        try:
            # Validar e-mail
            email = request.POST.get('email')
            
            if Usuario.objects.filter(email=email).exists():
                messages.error(request, 'Este e-mail já está em uso.')
                return render(request, 'core/seller_registration.html', {'form_data': request.POST})
            
            # Validar CPF
            cpf = ''.join(filter(str.isdigit, request.POST.get('cpf', '')))
            if not validate_cpf(cpf):
                messages.error(request, 'CPF inválido.')
                return render(request, 'core/seller_registration.html', {'form_data': request.POST})
            
            if Usuario.objects.filter(cpf=cpf).exists():
                messages.error(request, 'Este CPF já está cadastrado.')
                return render(request, 'core/seller_registration.html', {'form_data': request.POST})
            
            # Criar usuário
            user = Usuario.objects.create_user(
                email=email,
                password=None,  # Senha será definida posteriormente
                nome=request.POST.get('first_name'),
                cpf=cpf,
                telefone=request.POST.get('phone'),
                cep=request.POST.get('zip_code'),
                rua=request.POST.get('address'),
                numero=request.POST.get('number', 'S/N'),
                hectares_atendidos=0,  # Valor padrão
                is_active=False  # Será ativado após confirmação do e-mail
            )
            
            # Validar e salvar documento
            document_file = request.FILES.get('document_file')
            if not document_file:
                messages.error(request, 'Por favor, envie o documento.')
                user.delete()
                return render(request, 'core/seller_registration.html', {'form_data': request.POST})
            
            # Criar vendedor
            vendedor = Vendedor.objects.create(
                usuario=user,
                razao_social=f"{request.POST.get('first_name')} {request.POST.get('last_name')}",
                cnpj=None,  # CPF não deve ser salvo como CNPJ
                telefone=request.POST.get('phone'),
                cep=request.POST.get('zip_code').replace('-', ''),  # Remove o hífen antes de salvar
                endereco=request.POST.get('address'),
                cidade=request.POST.get('city'),
                estado=request.POST.get('state'),
            )
            
            # Enviar e-mail de confirmação
            if send_confirmation_email(user, request):
                messages.success(request, 'Cadastro realizado com sucesso! Por favor, verifique seu e-mail para confirmar sua conta.')
            else:
                messages.warning(request, 'Cadastro realizado, mas houve um problema ao enviar o e-mail de confirmação. Entre em contato com o suporte.')
            
            return redirect('core:login')
            
        except Exception as e:
            messages.error(request, f'Erro ao realizar cadastro: {str(e)}')
            return render(request, 'core/seller_registration.html', {'form_data': request.POST})
    
    return render(request, 'core/seller_registration.html')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def category_list(request):
    """Lista todas as categorias"""
    categories = Category.objects.all()
    return render(request, 'core/category_list.html', {'categories': categories})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def category_create(request):
    """Cria uma nova categoria"""
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Category.objects.create(name=name)
            messages.success(request, 'Categoria criada com sucesso!')
            return redirect('core:category_list')
        messages.error(request, 'Nome da categoria é obrigatório.')
    return render(request, 'core/category_form.html', {'title': 'Nova Categoria'})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def category_update(request, pk):
    """Atualiza uma categoria existente"""
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            category.name = name
            category.save()
            messages.success(request, 'Categoria atualizada com sucesso!')
            return redirect('core:category_list')
        messages.error(request, 'Nome da categoria é obrigatório.')
    return render(request, 'core/category_form.html', {
        'category': category,
        'title': 'Editar Categoria'
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def category_delete(request, pk):
    """Exclui uma categoria"""
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Categoria excluída com sucesso!')
        return redirect('core:category_list')
    return render(request, 'core/category_confirm_delete.html', {'category': category})

@login_required
@user_passes_test(is_superadmin)
def superadmin_dashboard(request):
    """Dashboard do superadmin com estatísticas e informações importantes"""
    # Estatísticas gerais
    total_sellers = Vendedor.objects.count()
    active_sellers = Vendedor.objects.filter(usuario__is_active=True).count()
    pending_sellers = Vendedor.objects.filter(usuario__is_active=False).count()
    total_products = Produto.objects.count()
    total_orders = Venda.objects.count()

    # Estatísticas de vendas
    vendas_por_status = Venda.objects.values('status').annotate(
        total=Count('id'),
        valor_total=Sum('produto__preco')
    )
    
    # Mensagens de suporte pendentes
    mensagens_pendentes = MensagemSuporte.objects.filter(respondido=False).count()
    
    # Últimos vendedores cadastrados
    ultimos_vendedores = Vendedor.objects.select_related('usuario').order_by('-created_at')[:5]
    
    # Últimas vendas
    ultimas_vendas = Venda.objects.select_related('vendedor', 'produto').order_by('-data_criacao')[:5]

    context = {
        'total_sellers': total_sellers,
        'active_sellers': active_sellers,
        'pending_sellers': pending_sellers,
        'total_products': total_products,
        'total_orders': total_orders,
        'vendas_por_status': vendas_por_status,
        'mensagens_pendentes': mensagens_pendentes,
        'ultimos_vendedores': ultimos_vendedores,
        'ultimas_vendas': ultimas_vendas,
    }

    return render(request, 'core/superadmin_dashboard.html', context)

@login_required
def seller_dashboard(request):
    """Dashboard do vendedor"""
    if not hasattr(request.user, 'vendedor'):
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return redirect('core:home')
    
    vendedor = request.user.vendedor
    produtos_recentes = Produto.objects.filter(vendedor=vendedor).order_by('-created_at')[:5]
    pedidos_recentes = Venda.objects.filter(vendedor=request.user).order_by('-data_criacao')[:5]
    
    # Calcula o total de produtos disponíveis
    total_produtos = Produto.objects.filter(vendedor=vendedor).count()
    
    # Calcula o total em vendas
    total_compras = Venda.objects.filter(vendedor=request.user).aggregate(total=Sum('produto__preco'))['total'] or 0
    
    context = {
        'vendedor': vendedor,
        'produtos_recentes': produtos_recentes,
        'pedidos_recentes': pedidos_recentes,
        'total_produtos': total_produtos,
        'total_compras': total_compras,
    }
    return render(request, 'core/seller_dashboard.html', context)

@login_required
@user_passes_test(is_superadmin)
def aprovar_cadastro(request, cadastro_id):
    """Aprova o cadastro de um vendedor"""
    try:
        vendedor = get_object_or_404(Vendedor, id=cadastro_id)
        
        # Verifica se o vendedor já está ativo
        if vendedor.usuario.is_active:
            messages.info(request, 'Este vendedor já está ativo no sistema.')
            return redirect('core:superadmin_dashboard')
        
        # Ativa o usuário
        vendedor.usuario.is_active = True
        vendedor.usuario.save()
        
        # Envia e-mail de confirmação
        try:
            send_mail(
                'Cadastro Aprovado - AgroMarketplace',
                f'Olá {vendedor.usuario.nome},\n\nSeu cadastro foi aprovado! Você já pode acessar o sistema.',
                settings.DEFAULT_FROM_EMAIL,
                [vendedor.usuario.email],
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Erro ao enviar e-mail de aprovação: {str(e)}")
            messages.warning(request, 'Cadastro aprovado, mas não foi possível enviar o e-mail de confirmação.')
        
        messages.success(request, f'Cadastro de {vendedor.usuario.nome} aprovado com sucesso.')
        return redirect('core:superadmin_dashboard')
    
    except Exception as e:
        messages.error(request, 'Não foi possível aprovar o cadastro. Tente novamente.')
        return redirect('core:superadmin_dashboard')

@login_required
@user_passes_test(is_superadmin)
def rejeitar_cadastro(request, cadastro_id):
    """Rejeita o cadastro de um vendedor"""
    try:
        vendedor = get_object_or_404(Vendedor, id=cadastro_id)
        user = vendedor.usuario
        
        # Verifica se o vendedor já está ativo
        if user.is_active:
            messages.warning(request, 'Não é possível rejeitar um vendedor já ativo.')
            return redirect('core:superadmin_dashboard')
        
        # Envia e-mail de rejeição
        try:
            send_mail(
                'Cadastro Rejeitado - AgroMarketplace',
                f'Olá {user.nome},\n\nInfelizmente seu cadastro não foi aprovado. Por favor, entre em contato conosco para mais informações.',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        except Exception as e:
            logger.error(f"Erro ao enviar e-mail de rejeição: {str(e)}")
            messages.warning(request, 'Cadastro rejeitado, mas não foi possível enviar o e-mail de notificação.')
        
        # Remove o vendedor e o usuário
        vendedor.delete()
        user.delete()
        
        messages.success(request, 'Cadastro rejeitado e removido com sucesso.')
        return redirect('core:superadmin_dashboard')
    
    except Exception as e:
        messages.error(request, 'Não foi possível rejeitar o cadastro. Tente novamente.')
        return redirect('core:superadmin_dashboard')

@login_required
def product_create(request):
    """Cria um novo produto"""
    if not hasattr(request.user, 'vendedor'):
        messages.error(request, 'Você não tem permissão para criar produtos.')
        return redirect('core:home')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user.vendedor
            product.save()
            try:
                messages.success(request, 'Produto criado com sucesso!')
            except Exception as e:
                messages.error(request, f'Erro ao criar produto: {str(e)}')
            return redirect('core:products')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'title': 'Criar Novo Produto',
        'categories': Category.objects.all()
    }
    return render(request, 'core/product_form.html', context)

@login_required
@user_passes_test(is_superadmin)
def product_update(request, pk):
    """Atualiza um produto existente"""
    product = get_object_or_404(Product, pk=pk)
    
    # Verifica se o usuário é o vendedor do produto ou um superadmin
    if not request.user.is_superuser and (not hasattr(request.user, 'vendedor') or product.seller != request.user.vendedor):
        messages.error(request, 'Você não tem permissão para editar este produto.')
        return redirect('core:products')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto atualizado com sucesso!')
            return redirect('core:products')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'title': 'Editar Produto',
    }
    return render(request, 'core/product_form.html', context)

@login_required
def product_delete(request, pk):
    """Exclui um produto"""
    product = get_object_or_404(Product, pk=pk)
    
    # Verifica se o usuário é o vendedor do produto ou um superadmin
    if not request.user.is_superuser and (not hasattr(request.user, 'vendedor') or product.seller != request.user.vendedor):
        messages.error(request, 'Você não tem permissão para excluir este produto.')
        return redirect('core:products')
    
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Produto excluído com sucesso!')
        return redirect('core:products')
    
    context = {
        'product': product,
        'categories': Category.objects.all().order_by('name'),
    }
    return render(request, 'core/product_confirm_delete.html', context)

@login_required
def product_detail(request, pk):
    """Exibe os detalhes de um produto"""
    product = get_object_or_404(Product, pk=pk)
    
    # Busca produtos relacionados da mesma categoria
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(
        pk=product.pk
    ).order_by('-created_at')[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
        'categories': Category.objects.all().order_by('name'),
    }
    return render(request, 'core/product_detail.html', context)

@login_required
def profile(request):
    """View do perfil do usuário"""
    return render(request, 'core/profile.html')

@login_required
@user_passes_test(is_superadmin)
def seller_edit(request, seller_id):
    """Edita os dados de um vendedor"""
    vendedor = get_object_or_404(Vendedor, pk=seller_id)
    
    if request.method == 'POST':
        try:
            # Atualiza os campos do vendedor
            vendedor.razao_social = request.POST.get('razao_social', '')
            vendedor.telefone = request.POST.get('telefone', '')
            vendedor.cep = request.POST.get('cep', '').replace('-', '')
            vendedor.endereco = request.POST.get('endereco', '')
            vendedor.cidade = request.POST.get('cidade', '')
            vendedor.estado = request.POST.get('estado', '')
            vendedor.hectares_atendidos = request.POST.get('hectares_atendidos', 0)
            
            # Verifica se uma nova senha foi fornecida
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            
            if new_password:
                if new_password != confirm_password:
                    messages.error(request, 'As senhas não coincidem.')
                    return redirect('core:seller_edit', seller_id=seller_id)
                
                # Define a nova senha
                vendedor.usuario.set_password(new_password)
                messages.success(request, 'Senha atualizada com sucesso!')
            
            # Atualiza o status do usuário
            vendedor.usuario.is_active = True
            vendedor.usuario.save()
            
            # Salva as alterações
            vendedor.save()
            
            messages.success(request, 'Dados do vendedor atualizados com sucesso!')
            return redirect('core:seller_detail', seller_id=seller_id)
            
        except Exception as e:
            logger.error(f"Erro ao atualizar vendedor: {str(e)}")
            messages.error(request, f'Erro ao atualizar dados do vendedor: {str(e)}')
    
    context = {
        'vendedor': vendedor,
    }
    return render(request, 'core/seller_edit.html', context)

@login_required
@user_passes_test(is_superadmin)
def seller_disable(request, seller_id):
    """Desativa um vendedor"""
    if request.method != 'POST':
        return redirect('core:listar_vendedores')
        
    vendedor = get_object_or_404(Vendedor, id=seller_id)
    vendedor.usuario.is_active = False
    vendedor.usuario.save()
    messages.warning(request, f'A conta do vendedor {vendedor.usuario.nome} foi desativada.')
    return redirect('core:listar_vendedores')

@login_required
@user_passes_test(is_superadmin)
def seller_enable(request, seller_id):
    """Ativa um vendedor"""
    if request.method != 'POST':
        return redirect('core:listar_vendedores')
        
    vendedor = get_object_or_404(Vendedor, id=seller_id)
    vendedor.usuario.is_active = True
    vendedor.usuario.save()
    messages.success(request, f'Vendedor {vendedor.usuario.nome} ativado.')
    return redirect('core:listar_vendedores')

@login_required
@user_passes_test(is_superadmin)
def seller_delete(request, seller_id):
    """Exclui a conta de um vendedor"""
    if request.method != 'POST':
        return redirect('core:listar_vendedores')
        
    vendedor = get_object_or_404(Vendedor, pk=seller_id)
    nome = vendedor.razao_social
    vendedor.usuario.delete()
    messages.success(request, f'A conta do vendedor {nome} foi excluída permanentemente.')
    return redirect('core:listar_vendedores')

@login_required
def order_create(request):
    return render(request, 'core/order_form.html')

@login_required
def order_detail(request, order_id):
    return render(request, 'core/order_detail.html')

@login_required
def order_edit(request, order_id):
    return render(request, 'core/order_form.html')

@login_required
def order_approve(request, order_id):
    return redirect('core:order_detail', order_id=order_id)

@login_required
def order_cancel(request, order_id):
    return redirect('core:order_detail', order_id=order_id)

def product_list(request):
    """Lista todos os produtos disponíveis"""
    products = Product.objects.filter(is_active=True).select_related('category')
    
    # Filtro por categoria
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Busca por nome ou descrição
    search = request.GET.get('search')
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Ordenação
    ordenacao = request.GET.get('ordenacao')
    if ordenacao == 'preco_menor':
        products = products.order_by('price')
    elif ordenacao == 'preco_maior':
        products = products.order_by('-price')
    elif ordenacao == 'nome':
        products = products.order_by('name')
    else:
        products = products.order_by('-created_at')
    
    # Paginação
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    categories = Category.objects.all().order_by('name')
    
    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_id,
        'search_query': search,
        'selected_ordenacao': ordenacao,
    }
    
    return render(request, 'core/product_list.html', context)

@login_required
@user_passes_test(is_superadmin)
def listar_vendedores(request):
    """Lista todos os vendedores com filtro de status"""
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    vendedores = Vendedor.objects.all().select_related('usuario')
    
    if status_filter:
        if status_filter == 'active':
            vendedores = vendedores.filter(usuario__is_active=True)
        elif status_filter == 'inactive':
            vendedores = vendedores.filter(usuario__is_active=False)
        elif status_filter == 'pending':
            vendedores = vendedores.filter(usuario__is_active=False)
    
    if search_query:
        vendedores = vendedores.filter(
            Q(usuario__nome__icontains=search_query) |
            Q(usuario__email__icontains=search_query) |
            Q(usuario__cpf__icontains=search_query) |
            Q(usuario__telefone__icontains=search_query)
        )
    
    # Adiciona as opções de status para o filtro
    status_choices = [
        ('', 'Todos os Status'),
        ('active', 'Ativos'),
        ('inactive', 'Inativos'),
        ('pending', 'Pendentes')
    ]
    
    context = {
        'vendedores': vendedores,
        'status_filter': status_filter,
        'search_query': search_query,
        'status_choices': status_choices,
    }
    return render(request, 'core/listar_vendedores.html', context)

@login_required
@user_passes_test(is_superadmin)
def aprovar_vendedor(request, vendedor_id):
    """Aprova um vendedor"""
    if request.method != 'POST':
        return redirect('core:listar_vendedores')
        
    vendedor = get_object_or_404(Vendedor, id=vendedor_id)
    vendedor.usuario.is_active = True
    vendedor.usuario.save()
    messages.success(request, f'Vendedor {vendedor.usuario.nome} aprovado com sucesso!')
    return redirect('core:listar_vendedores')

@login_required
@user_passes_test(is_superadmin)
def reprovar_vendedor(request, vendedor_id):
    """Reprova um vendedor"""
    if request.method != 'POST':
        return redirect('core:listar_vendedores')
        
    vendedor = get_object_or_404(Vendedor, id=vendedor_id)
    vendedor.usuario.is_active = False
    vendedor.usuario.save()
    messages.warning(request, f'Vendedor {vendedor.usuario.nome} reprovado.')
    return redirect('core:listar_vendedores')

@login_required
@user_passes_test(is_superadmin)
def superadmin_products(request):
    """Lista todos os produtos para o superadmin"""
    products = Product.objects.all().select_related('category').order_by('-created_at')
    
    # Filtro por categoria
    category_id = request.GET.get('category')
    if category_id:
        products = products.filter(category_id=category_id)
    
    # Filtro por status
    status = request.GET.get('status')
    if status:
        is_active = status == 'active'
        products = products.filter(is_active=is_active)
    
    # Busca por nome ou descrição
    search = request.GET.get('search')
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search)
        )
    
    categories = Category.objects.all().order_by('name')
    
    context = {
        'products': products,
        'categories': categories,
        'selected_category': category_id,
        'selected_status': status,
        'search_query': search,
    }
    
    return render(request, 'core/superadmin_products.html', context)

@login_required
@user_passes_test(is_superadmin)
def superadmin_product_create(request):
    """Cria um novo produto via painel do superadmin"""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                product = form.save()
                logger.info(f'Produto criado com sucesso: {product.name} (ID: {product.id})')
                messages.success(request, 'Produto criado com sucesso!')
                return redirect('core:superadmin_products')
            except Exception as e:
                logger.error(f'Erro ao criar produto: {str(e)}')
                logger.error(f'Dados do formulário: {request.POST}')
                messages.error(request, f'Erro ao criar produto: {str(e)}')
        else:
            logger.error(f'Erros de validação do formulário: {form.errors}')
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Erro no campo {field}: {error}')
    else:
        form = ProductForm(initial={
            'is_active': True,
            'currency': 'BRL',
            'allow_exchange': False
        })
    
    context = {
        'form': form,
        'title': 'Novo Produto',
        'categories': Category.objects.all().order_by('name'),
        'currency_choices': Product.CURRENCY_CHOICES,
        'product_type_choices': Product.PRODUCT_TYPE_CHOICES,
        'unit_choices': Product.UNIT_CHOICES,
        'packaging_choices': Product.PACKAGING_CHOICES,
    }
    return render(request, 'core/superadmin/product_form.html', context)

@login_required
@user_passes_test(is_superadmin)
def superadmin_product_delete(request, pk):
    """Exclui um produto via painel do superadmin"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        try:
            product.delete()
            messages.success(request, 'Produto excluído com sucesso!')
        except Exception as e:
            messages.error(request, f'Erro ao excluir produto: {str(e)}')
    
    return redirect('core:superadmin_products')

@login_required
def seller_products(request):
    """Lista os produtos disponíveis para o vendedor"""
    if not hasattr(request.user, 'vendedor'):
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return redirect('core:home')
    
    products = Product.objects.filter(is_active=True).order_by('-created_at')
    
    context = {
        'products': products,
    }
    return render(request, 'core/seller_products.html', context)

@login_required
def carrinho(request):
    cart = request.session.get('cart', {'items': [], 'total': 0})
    return render(request, 'core/carrinho.html', {'cart': cart})

def adicionar_ao_carrinho(request, product_id):
    if request.method == 'POST':
        try:
            quantity = float(request.POST.get('quantity', 0))
            if quantity <= 0:
                messages.warning(request, 'A quantidade deve ser maior que zero.')
                return redirect('core:products')

            product = Product.objects.get(pk=product_id)
            if quantity > product.available_volume:
                messages.warning(request, f'Quantidade indisponível. Máximo disponível: {product.available_volume} {product.get_unit_display()}')
                return redirect('core:products')

            cart = request.session.get('cart', {'items': [], 'total': 0})
            
            # Verifica se o produto já está no carrinho
            item_exists = False
            for item in cart['items']:
                if item['product_id'] == product.pk:
                    item['quantity'] += quantity
                    item['subtotal'] = item['quantity'] * item['price']
                    item_exists = True
                    break

            if not item_exists:
                cart['items'].append({
                    'product_id': product.pk,
                    'product_name': product.name,
                    'product_description': product.description,
                    'product_image': product.image.url if product.image else None,
                    'quantity': quantity,
                    'price': float(product.price),
                    'unit': product.get_unit_display(),
                    'subtotal': quantity * float(product.price)
                })

            # Atualiza o total do carrinho
            cart['total'] = sum(item['subtotal'] for item in cart['items'])
            request.session['cart'] = cart
            messages.success(request, f'{product.name} adicionado ao carrinho.')
            
        except ValueError:
            messages.error(request, 'Quantidade inválida. Use apenas números.')
        except Product.DoesNotExist:
            messages.error(request, 'Produto não encontrado no sistema.')
        except Exception as e:
            messages.error(request, 'Não foi possível adicionar o produto ao carrinho.')
            logger.error(f'Erro ao adicionar produto ao carrinho: {str(e)}')

    return redirect('core:products')

def remover_do_carrinho(request, product_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {'items': [], 'total': 0})
        
        # Remove o item do carrinho
        cart['items'] = [item for item in cart['items'] if item['product_id'] != product_id]
        
        # Atualiza o total do carrinho
        cart['total'] = sum(item['subtotal'] for item in cart['items'])
        request.session['cart'] = cart
        
        messages.success(request, 'Produto removido do carrinho com sucesso!')
    
    return redirect('core:carrinho')

@login_required
@user_passes_test(is_superadmin)
def superadmin_orders(request):
    """Lista todos os pedidos para o superadmin"""
    orders = Order.objects.all().order_by('-created_at')
    
    # Filtro por status
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    
    context = {
        'orders': orders,
        'status_choices': Order.STATUS_CHOICES,
        'current_status': status,
    }
    return render(request, 'core/superadmin_orders.html', context)

@login_required
@user_passes_test(is_superadmin)
def superadmin_order_detail(request, order_id):
    """Exibe os detalhes de um pedido para o superadmin"""
    order = get_object_or_404(Order, pk=order_id)
    order_items = OrderItem.objects.filter(order=order).select_related('product')
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status and new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Status do pedido atualizado para {dict(Order.STATUS_CHOICES)[order.status]}')
            return redirect('core:superadmin_order_detail', order_id=order.pk)
    
    context = {
        'order': order,
        'items': order_items,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'core/superadmin_order_detail.html', context)

@login_required
@user_passes_test(is_superadmin)
def superadmin_order_delete(request, order_id):
    """Exclui um pedido"""
    order = get_object_or_404(Order, pk=order_id)
    
    if request.method == 'POST':
        order.delete()
        messages.success(request, 'Pedido excluído com sucesso!')
        return redirect('core:superadmin_orders')
    
    context = {
        'order': order,
    }
    return render(request, 'core/superadmin_order_delete.html', context)

@login_required
@user_passes_test(is_superadmin)
def listar_superadmins(request):
    """Lista todos os superadmins ativos"""
    superadmins = Usuario.objects.filter(is_superuser=True, is_active=True)
    
    context = {
        'superadmins': superadmins,
    }
    return render(request, 'core/listar_superadmins.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def cadastrar_vendedor(request):
    if request.method == 'POST':
        form = SellerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()
            
            # Criar o perfil de vendedor
            vendedor = Vendedor.objects.create(
                usuario=user,
                razao_social=form.cleaned_data['razao_social'],
                nome_fantasia=form.cleaned_data['nome_fantasia'],
                cnpj=form.cleaned_data['cnpj'],
                inscricao_estadual=form.cleaned_data['inscricao_estadual'],
                telefone=form.cleaned_data['telefone'],
                endereco=form.cleaned_data['endereco'],
                cidade=form.cleaned_data['cidade'],
                estado=form.cleaned_data['estado'],
                cep=form.cleaned_data['cep'],
                hectares_atendidos=form.cleaned_data['hectares_atendidos']
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
    vendedor = get_object_or_404(Vendedor, pk=application_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        
        if action == 'approve':
            # Aprova o vendedor
            vendedor.usuario.is_active = True
            vendedor.usuario.save()
            messages.success(request, 'Vendedor aprovado com sucesso!')
        elif action == 'reject':
            # Rejeita o vendedor
            vendedor.usuario.is_active = False
            vendedor.usuario.save()
            messages.success(request, 'Vendedor reprovado.')
        
        return redirect('core:superadmin_dashboard')
    
    context = {
        'application': vendedor,
    }
    return render(request, 'core/review_application.html', context)

def seller_detail(request, seller_id):
    """Visualização detalhada de um vendedor"""
    vendedor = get_object_or_404(Vendedor, pk=seller_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'approve':
            vendedor.usuario.is_active = True
            vendedor.usuario.save()
            messages.success(request, 'Vendedor aprovado com sucesso!')
        elif action == 'reject':
            vendedor.usuario.is_active = False
            vendedor.usuario.save()
            messages.success(request, 'Vendedor reprovado.')
        
        return redirect('core:seller_detail', seller_id=vendedor.pk)
    
    context = {
        'vendedor': vendedor,
    }
    return render(request, 'core/seller_detail.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def superadmin_product_update(request, pk):
    """Atualiza um produto existente (apenas superadmin)"""
    produto = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=produto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto atualizado com sucesso!')
            return redirect('core:superadmin_products')
    else:
        form = ProductForm(instance=produto)
    
    return render(request, 'core/superadmin/product_form.html', {
        'form': form,
        'produto': produto,
        'title': 'Editar Produto',
        'categories': Category.objects.all().order_by('name')
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
@csrf_exempt
def consult_ia(request):
    return JsonResponse({'message': 'Funcionalidade não disponível'})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def consult_ia_page(request):
    return render(request, 'core/consult_ia.html', {'message': 'Funcionalidade não disponível'})

@login_required
def dashboard(request):
    # Verifica o tipo de usuário e redireciona para o dashboard apropriado
    if request.user.is_superuser:
        return redirect('core:superadmin_dashboard')
    elif hasattr(request.user, 'vendedor'):
        # Obtém as estatísticas dos pedidos
        pedidos = Venda.objects.filter(vendedor=request.user)
        total_pedidos = pedidos.count()
        pedidos_pendentes = pedidos.filter(status='PENDENTE').count()
        pedidos_aprovados = pedidos.filter(status='ACEITO').count()
        pedidos_rejeitados = pedidos.filter(status='REJEITADO').count()
        
        # Obtém os últimos pedidos
        ultimos_pedidos = pedidos.order_by('-data_criacao')[:10]
        
        # Conta o número de mensagens pendentes (apenas para superadmin)
        mensagens_pendentes = 0
        if request.user.is_superuser:
            mensagens_pendentes = MensagemSuporte.objects.filter(respondido=False).count()
        
        context = {
            'vendedor': request.user.vendedor,
            'total_pedidos': total_pedidos,
            'pedidos_pendentes': pedidos_pendentes,
            'pedidos_aprovados': pedidos_aprovados,
            'pedidos_rejeitados': pedidos_rejeitados,
            'ultimos_pedidos': ultimos_pedidos,
            'mensagens_pendentes': mensagens_pendentes,
        }
        
        return render(request, 'core/seller_dashboard.html', context)
    else:
        # Usuário comum - redireciona para o catálogo
        return redirect('core:catalogo')

@login_required
def catalogo(request):
    # Obtém os filtros
    categoria = request.GET.get('categoria')
    tipo = request.GET.get('tipo')
    busca = request.GET.get('busca')
    preco_min = request.GET.get('preco_min')
    preco_max = request.GET.get('preco_max')
    ordenar = request.GET.get('ordenar', 'recentes')
    
    # Inicia a query
    produtos = Product.objects.filter(is_active=True)
    
    # Log para depuração
    print(f"Total de produtos antes dos filtros: {produtos.count()}")
    
    # Aplica os filtros
    if categoria:
        produtos = produtos.filter(category_id=categoria)
        print(f"Total de produtos após filtro de categoria: {produtos.count()}")
    if tipo:
        produtos = produtos.filter(product_type=tipo)
        print(f"Total de produtos após filtro de tipo: {produtos.count()}")
    if busca:
        produtos = produtos.filter(name__icontains=busca)
        print(f"Total de produtos após filtro de busca: {produtos.count()}")
    if preco_min:
        produtos = produtos.filter(price__gte=preco_min)
    if preco_max:
        produtos = produtos.filter(price__lte=preco_max)
    
    # Aplica ordenação
    if ordenar == 'preco_menor':
        produtos = produtos.order_by('price')
    elif ordenar == 'preco_maior':
        produtos = produtos.order_by('-price')
    elif ordenar == 'nome':
        produtos = produtos.order_by('name')
    else:  # recentes
        produtos = produtos.order_by('-created_at')
    
    # Paginação
    paginator = Paginator(produtos, 12)  # 12 itens por página
    page = request.GET.get('page')
    produtos = paginator.get_page(page)
    
    # Obtém todas as categorias para o filtro
    categorias = Category.objects.all().order_by('name')
    
    # Obtém os tipos de produtos para o filtro
    tipos = Product.PRODUCT_TYPE_CHOICES
    
    # Conta o número de mensagens pendentes (apenas para superadmin)
    mensagens_pendentes = 0
    if request.user.is_superuser:
        mensagens_pendentes = MensagemSuporte.objects.filter(respondido=False).count()
    
    context = {
        'produtos': produtos,
        'categorias': categorias,
        'tipos': tipos,
        'categoria_selecionada': categoria,
        'tipo_selecionado': tipo,
        'busca': busca,
        'preco_min': preco_min,
        'preco_max': preco_max,
        'ordenar': ordenar,
        'mensagens_pendentes': mensagens_pendentes,
    }
    
    return render(request, 'core/catalogo.html', context)

@login_required
def suporte(request):
    """View para vendedores enviarem mensagens de suporte"""
    # Verifica se o usuário é um vendedor
    if not hasattr(request.user, 'vendedor'):
        messages.error(request, 'Acesso negado. Apenas vendedores podem acessar esta página.')
        return redirect('core:dashboard')
        
    if request.method == 'POST':
        assunto = request.POST.get('assunto')
        mensagem = request.POST.get('mensagem')
        
        if assunto and mensagem:
            MensagemSuporte.objects.create(
                usuario=request.user,
                assunto=assunto,
                mensagem=mensagem
            )
            messages.success(request, 'Mensagem enviada com sucesso! Em breve entraremos em contato.')
            return redirect('core:suporte')
        else:
            messages.error(request, 'Por favor, preencha todos os campos.')
            
    # Buscar mensagens anteriores do usuário
    mensagens = MensagemSuporte.objects.filter(usuario=request.user).order_by('-data_envio')[:5]
    
    context = {
        'mensagens': mensagens
    }
    return render(request, 'core/suporte.html', context)

@login_required
@user_passes_test(is_superadmin)
def superadmin_suporte(request):
    try:
        mensagens = MensagemSuporte.objects.select_related('usuario').order_by('-data_envio')
        status = request.GET.get('status', '')
        
        if status:
            mensagens = mensagens.filter(respondido=False)
        
        mensagens_pendentes = MensagemSuporte.objects.filter(respondido=False).count()
                
        context = {
            'mensagens': mensagens,
            'status_filtro': status,
            'mensagens_pendentes': mensagens_pendentes
        }
        return render(request, 'core/superadmin_suporte.html', context)
    except Exception as e:
        logger.error(f"Erro ao acessar suporte: {str(e)}")
        messages.error(request, 'Erro ao acessar o sistema de suporte. Por favor, tente novamente.')
        return redirect('core:superadmin_dashboard')

@login_required
def solicitar_produto(request):
    if not hasattr(request.user, 'vendedor'):
        messages.error(request, 'Apenas vendedores podem solicitar produtos.')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = SolicitacaoProdutoForm(request.POST)
        if form.is_valid():
            solicitacao = form.save(commit=False)
            solicitacao.vendedor = request.user
            solicitacao.save()
            messages.success(request, 'Sua solicitação foi enviada com sucesso para análise!')
            return redirect('core:dashboard')
    else:
        form = SolicitacaoProdutoForm()
    
    return render(request, 'core/solicitar_produto.html', {'form': form})

@login_required
def minhas_solicitacoes(request):
    if not hasattr(request.user, 'vendedor'):
        messages.error(request, 'Apenas vendedores podem acessar esta página.')
        return redirect('core:dashboard')
    
    solicitacoes = SolicitacaoProduto.objects.filter(vendedor=request.user).order_by('-data_solicitacao')
    return render(request, 'core/minhas_solicitacoes.html', {'solicitacoes': solicitacoes})

@login_required
def detalhes_solicitacao(request, pk):
    if not hasattr(request.user, 'vendedor'):
        messages.error(request, 'Apenas vendedores podem acessar esta página.')
        return redirect('core:dashboard')
    
    try:
        solicitacao = SolicitacaoProduto.objects.get(pk=pk, vendedor=request.user)
    except SolicitacaoProduto.DoesNotExist:
        messages.error(request, 'Solicitação não encontrada.')
        return redirect('core:minhas_solicitacoes')
    
    return render(request, 'core/detalhes_solicitacao.html', {'solicitacao': solicitacao})

@login_required
def superadmin_solicitacoes(request):
    if not request.user.is_superuser:
        messages.error(request, 'Acesso negado. Apenas superadministradores podem acessar esta página.')
        return redirect('core:dashboard')
    
    solicitacoes = SolicitacaoProduto.objects.all().order_by('-data_solicitacao')
    return render(request, 'core/superadmin_solicitacoes.html', {'solicitacoes': solicitacoes})

@login_required
def superadmin_detalhes_solicitacao(request, pk):
    if not request.user.is_superuser:
        messages.error(request, 'Acesso negado. Apenas superadministradores podem acessar esta página.')
        return redirect('core:dashboard')
    
    try:
        solicitacao = SolicitacaoProduto.objects.get(pk=pk)
    except SolicitacaoProduto.DoesNotExist:
        messages.error(request, 'Solicitação não encontrada.')
        return redirect('core:superadmin_solicitacoes')
    
    if request.method == 'POST':
        acao = request.POST.get('acao')
        resposta = request.POST.get('resposta', '')
        
        if acao == 'analisar':
            solicitacao.status = 'ANALISADO'
            solicitacao.resposta_superadmin = resposta
            solicitacao.save()
            messages.success(request, 'Solicitação marcada como analisada com sucesso!')
            return redirect('core:superadmin_solicitacoes')
        elif acao == 'excluir':
            solicitacao.delete()
            messages.success(request, 'Solicitação excluída com sucesso!')
            return redirect('core:superadmin_solicitacoes')
    
    return render(request, 'core/superadmin_detalhes_solicitacao.html', {'solicitacao': solicitacao})

@login_required
def request_product(request):
    if request.method == 'POST':
        form = SolicitacaoProdutoForm(request.POST)
        if form.is_valid():
            solicitacao = form.save(commit=False)
            solicitacao.vendedor = request.user.vendedor
            solicitacao.save()
            messages.success(request, 'Solicitação de produto enviada com sucesso!')
            return redirect('core:seller_dashboard')
    else:
        form = SolicitacaoProdutoForm()
    
    return render(request, 'core/request_product.html', {'form': form})

@login_required
def seller_profile(request):
    vendedor = get_object_or_404(Vendedor, usuario=request.user)
    
    if request.method == 'POST':
        # Atualizar informações do vendedor
        vendedor.razao_social = request.POST.get('razao_social')
        vendedor.nome_fantasia = request.POST.get('nome_fantasia')
        vendedor.cnpj = request.POST.get('cnpj')
        vendedor.telefone = request.POST.get('telefone')
        vendedor.endereco = request.POST.get('endereco')
        vendedor.cidade = request.POST.get('cidade')
        vendedor.estado = request.POST.get('estado')
        vendedor.cep = request.POST.get('cep')
        vendedor.save()

        # Processar redefinição de senha
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if current_password and new_password and confirm_password:
            if not request.user.check_password(current_password):
                messages.error(request, 'Senha atual incorreta.')
            elif new_password != confirm_password:
                messages.error(request, 'As senhas não coincidem.')
            else:
                request.user.set_password(new_password)
                request.user.save()
                messages.success(request, 'Senha alterada com sucesso!')
                return redirect('core:login')

        messages.success(request, 'Perfil atualizado com sucesso!')
        return redirect('core:seller_profile')

    return render(request, 'core/seller_profile.html', {'vendedor': vendedor})

@login_required
def produto_detalhe(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    return render(request, 'core/produto_detalhe.html', {'produto': produto})
