from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Count, Sum, F
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import ValidationError
from .models import Seller, Product, Category, Order, OrderItem, VendorApplication, SellerRegistration
from .forms import ProductForm, OrderForm, OrderItemFormSet, SellerRegistrationForm
from .utils import validate_file_upload, validate_cpf
from django.http import HttpResponse, JsonResponse
import logging
from django.db.models import Q
from django.db.models.functions import TruncMonth
from django.core.paginator import Paginator

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
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bem-vindo, {username}!')
                if user.is_superuser:
                    return redirect('core:superadmin_dashboard')
                elif hasattr(user, 'seller'):
                    return redirect('core:seller_dashboard')
                return redirect('core:home')
            else:
                messages.error(request, 'Usuário ou senha inválidos.')
        else:
            messages.error(request, 'Usuário ou senha inválidos.')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    """View de logout"""
    logout(request)
    messages.success(request, 'Você saiu com sucesso!')
    return redirect('core:home')

def generate_email_confirmation_token(user):
    return urlsafe_base64_encode(force_bytes(user.pk))

def confirm_email(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
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
            
            if User.objects.filter(email=email).exists():
                messages.error(request, 'Este e-mail já está em uso.')
                return render(request, 'core/seller_registration.html', {'form_data': request.POST})
            
            # Validar CPF
            cpf = ''.join(filter(str.isdigit, request.POST.get('cpf', '')))
            if not validate_cpf(cpf):
                messages.error(request, 'CPF inválido.')
                return render(request, 'core/seller_registration.html', {'form_data': request.POST})
            
            if Seller.objects.filter(cpf=cpf).exists():
                messages.error(request, 'Este CPF já está cadastrado.')
                return render(request, 'core/seller_registration.html', {'form_data': request.POST})
            
            # Criar usuário
            user = User.objects.create_user(
                username=email,  # Usar o e-mail como nome de usuário
                email=email,
                password=None,  # Senha será definida posteriormente
                first_name=request.POST.get('first_name'),
                last_name=request.POST.get('last_name'),
                is_active=False  # Será ativado após confirmação do e-mail
            )
            
            # Validar e salvar documento
            document_file = request.FILES.get('document_file')
            if not document_file:
                messages.error(request, 'Por favor, envie o documento.')
                user.delete()
                return render(request, 'core/seller_registration.html', {'form_data': request.POST})
            
            # Criar vendedor
            seller = Seller.objects.create(
                user=user,
                full_name=f"{request.POST.get('first_name')} {request.POST.get('last_name')}",
                cpf=cpf,
                document_type=request.POST.get('document_type'),
                document_number=request.POST.get('document_number'),
                document_file=document_file,
                phone=request.POST.get('phone'),
                cep=request.POST.get('zip_code').replace('-', ''),  # Remove o hífen antes de salvar
                address=request.POST.get('address'),
                city=request.POST.get('city'),
                state=request.POST.get('state'),
                hectares=request.POST.get('hectares'),
                status='Pendente',
                is_approved=False
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
def superadmin_dashboard(request):
    try:
        # Estatísticas gerais
        total_produtos = Product.objects.count()
        total_pedidos = Order.objects.count()
        total_vendedores = Seller.objects.filter(is_approved=True).count()
        
        # Aplicações pendentes
        applications = Seller.objects.filter(status='Pendente', is_approved=False).order_by('-created_at')
        
        # Dados para o gráfico de pedidos por mês
        pedidos_por_mes = Order.objects.annotate(
            mes=TruncMonth('created_at')
        ).values('mes').annotate(
            total=Count('id')
        ).order_by('mes')
        
        meses = [pedido['mes'].strftime('%B/%Y') for pedido in pedidos_por_mes]
        totais = [pedido['total'] for pedido in pedidos_por_mes]
        
        context = {
            'total_produtos': total_produtos,
            'total_pedidos': total_pedidos,
            'total_vendedores': total_vendedores,
            'applications': applications,
            'meses': meses,
            'totais': totais,
        }
        
        return render(request, 'core/superadmin_dashboard.html', context)
    except Exception as e:
        logger.error(f"Erro no dashboard do superadmin: {str(e)}")
        messages.error(request, 'Ocorreu um erro ao carregar o dashboard.')
        return redirect('core:home')

@login_required
def seller_dashboard(request):
    """Dashboard do vendedor"""
    if not hasattr(request.user, 'seller'):
        messages.error(request, 'Você não tem permissão para acessar esta página.')
        return redirect('core:home')
    
    seller = request.user.seller
    produtos_recentes = Product.objects.filter(is_active=True).order_by('-created_at')[:5]
    pedidos_recentes = Order.objects.filter(created_by=request.user).order_by('-created_at')[:5]
    
    # Calcula o total de produtos disponíveis
    total_produtos = Product.objects.filter(is_active=True).count()
    
    # Calcula o total em compras
    total_compras = Order.objects.filter(created_by=request.user).aggregate(total=Sum('total_value'))['total'] or 0
    
    context = {
        'seller': seller,
        'produtos_recentes': produtos_recentes,
        'pedidos_recentes': pedidos_recentes,
        'total_produtos': total_produtos,
        'total_compras': total_compras,
    }
    return render(request, 'core/seller_dashboard.html', context)

@login_required
@user_passes_test(is_superadmin)
def aprovar_cadastro(request, cadastro_id):
    seller = get_object_or_404(Seller, id=cadastro_id, is_approved=False)
    seller.is_approved = True
    seller.save()
    
    messages.success(request, 'Vendedor aprovado com sucesso!')
    return redirect('core:superadmin_dashboard')

@login_required
@user_passes_test(is_superadmin)
def rejeitar_cadastro(request, cadastro_id):
    seller = get_object_or_404(Seller, id=cadastro_id, is_approved=False)
    user = seller.user
    seller.delete()
    user.delete()
    
    messages.success(request, 'Vendedor rejeitado com sucesso!')
    return redirect('core:superadmin_dashboard')

@login_required
def product_create(request):
    """Cria um novo produto"""
    if not hasattr(request.user, 'seller'):
        messages.error(request, 'Você não tem permissão para criar produtos.')
        return redirect('core:home')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user.seller
            product.save()
            messages.success(request, 'Produto criado com sucesso!')
            return redirect('core:products')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'title': 'Criar Novo Produto',
        'categories': Category.objects.all().order_by('name'),
    }
    return render(request, 'core/product_form.html', context)

@login_required
@user_passes_test(is_superadmin)
def product_update(request, pk):
    """Atualiza um produto existente"""
    product = get_object_or_404(Product, pk=pk)
    
    # Verifica se o usuário é o vendedor do produto ou um superadmin
    if not request.user.is_superuser and (not hasattr(request.user, 'seller') or product.seller != request.user.seller):
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
        'categories': Category.objects.all().order_by('name'),
    }
    return render(request, 'core/product_form.html', context)

@login_required
def product_delete(request, pk):
    """Exclui um produto"""
    product = get_object_or_404(Product, pk=pk)
    
    # Verifica se o usuário é o vendedor do produto ou um superadmin
    if not request.user.is_superuser and (not hasattr(request.user, 'seller') or product.seller != request.user.seller):
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
        id=product.id
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
    vendedor = get_object_or_404(Seller, id=seller_id)
    
    if request.method == 'POST':
        try:
            # Atualiza os campos do vendedor
            vendedor.full_name = request.POST.get('full_name', '')
            vendedor.phone = request.POST.get('phone', '')
            vendedor.cep = request.POST.get('cep', '').replace('-', '')
            vendedor.address = request.POST.get('address', '')
            vendedor.number = request.POST.get('number', '')
            vendedor.complement = request.POST.get('complement', '')
            vendedor.neighborhood = request.POST.get('neighborhood', '')
            vendedor.city = request.POST.get('city', '')
            vendedor.state = request.POST.get('state', '')
            vendedor.hectares = request.POST.get('hectares')
            vendedor.status = request.POST.get('status', 'Pendente')
            
            # Atualiza o status de aprovação baseado no status
            vendedor.is_approved = vendedor.status == 'Aprovado'
            
            # Atualiza o status do usuário
            vendedor.user.is_active = vendedor.status != 'Reprovado'
            vendedor.user.save()
            
            # Salva as alterações
            vendedor.save()
            
            messages.success(request, 'Dados do vendedor atualizados com sucesso!')
            return redirect('core:seller_detail', seller_id=vendedor.id)
            
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
    """Desativa a conta de um vendedor"""
    if request.method != 'POST':
        return redirect('core:listar_vendedores')
        
    vendedor = get_object_or_404(Seller, id=seller_id)
    vendedor.user.is_active = False
    vendedor.user.save()
    messages.success(request, f'Conta do vendedor {vendedor.full_name} desativada com sucesso!')
    return redirect('core:listar_vendedores')

@login_required
@user_passes_test(is_superadmin)
def seller_enable(request, seller_id):
    """Ativa a conta de um vendedor"""
    if request.method != 'POST':
        return redirect('core:listar_vendedores')
        
    vendedor = get_object_or_404(Seller, id=seller_id)
    vendedor.user.is_active = True
    vendedor.user.save()
    messages.success(request, f'Conta do vendedor {vendedor.full_name} ativada com sucesso!')
    return redirect('core:listar_vendedores')

@login_required
@user_passes_test(is_superadmin)
def seller_delete(request, seller_id):
    """Exclui a conta de um vendedor"""
    if request.method != 'POST':
        return redirect('core:listar_vendedores')
        
    vendedor = get_object_or_404(Seller, id=seller_id)
    nome = vendedor.full_name
    vendedor.user.delete()  # Isso também excluirá o vendedor devido ao on_delete=CASCADE
    messages.success(request, f'Conta do vendedor {nome} excluída com sucesso!')
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
    
    vendedores = Seller.objects.all().select_related('user')
    
    if status_filter:
        vendedores = vendedores.filter(status=status_filter)
    
    if search_query:
        vendedores = vendedores.filter(
            Q(full_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(cpf__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    context = {
        'vendedores': vendedores,
        'status_filter': status_filter,
        'search_query': search_query,
        'status_choices': Seller.STATUS_CHOICES,
    }
    return render(request, 'core/listar_vendedores.html', context)

@login_required
@user_passes_test(is_superadmin)
def aprovar_vendedor(request, vendedor_id):
    """Aprova um vendedor"""
    if request.method != 'POST':
        return redirect('core:listar_vendedores')
        
    vendedor = get_object_or_404(Seller, id=vendedor_id)
    vendedor.status = 'Aprovado'
    vendedor.is_approved = True
    vendedor.save()
    messages.success(request, f'Vendedor {vendedor.full_name} aprovado com sucesso!')
    return redirect('core:listar_vendedores')

@login_required
@user_passes_test(is_superadmin)
def reprovar_vendedor(request, vendedor_id):
    """Reprova um vendedor"""
    if request.method != 'POST':
        return redirect('core:listar_vendedores')
        
    vendedor = get_object_or_404(Seller, id=vendedor_id)
    vendedor.status = 'Reprovado'
    vendedor.is_approved = False
    vendedor.save()
    messages.success(request, f'Vendedor {vendedor.full_name} reprovado.')
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
                messages.success(request, 'Produto criado com sucesso!')
                return redirect('core:superadmin_products')
            except Exception as e:
                messages.error(request, f'Erro ao criar produto: {str(e)}')
                logger.error(f'Erro ao criar produto: {str(e)}')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
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
    return render(request, 'core/product_form.html', context)

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
    if not hasattr(request.user, 'seller'):
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
                messages.error(request, 'A quantidade deve ser maior que zero.')
                return redirect('core:products')

            product = Product.objects.get(id=product_id)
            if quantity > product.available_volume:
                messages.error(request, f'Quantidade indisponível. Volume disponível: {product.available_volume} {product.get_unit_display()}')
                return redirect('core:products')

            cart = request.session.get('cart', {'items': [], 'total': 0})
            
            # Verifica se o produto já está no carrinho
            item_exists = False
            for item in cart['items']:
                if item['product_id'] == product.id:
                    item['quantity'] += quantity
                    item['subtotal'] = item['quantity'] * item['price']
                    item_exists = True
                    break

            if not item_exists:
                cart['items'].append({
                    'product_id': product.id,
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
            messages.success(request, 'Produto adicionado ao carrinho com sucesso!')
            
        except ValueError:
            messages.error(request, 'Quantidade inválida.')
        except Product.DoesNotExist:
            messages.error(request, 'Produto não encontrado.')
        except Exception as e:
            messages.error(request, f'Erro ao adicionar produto ao carrinho: {str(e)}')
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
    orders = Order.objects.all().select_related('created_by').order_by('-created_at')
    
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
    order = get_object_or_404(Order.objects.select_related('created_by'), id=order_id)
    items = order.items.select_related('product').all()
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status and new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Status do pedido atualizado para {order.get_status_display()}')
            return redirect('core:superadmin_order_detail', order_id=order.id)
    
    context = {
        'order': order,
        'items': items,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'core/superadmin_order_detail.html', context)

@login_required
@user_passes_test(is_superadmin)
def superadmin_order_delete(request, order_id):
    """Exclui um pedido"""
    order = get_object_or_404(Order, id=order_id)
    
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
    superadmins = User.objects.filter(is_superuser=True, is_active=True)
    
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
            seller = Seller.objects.create(
                user=user,
                company_name=form.cleaned_data['company_name'],
                cnpj=form.cleaned_data['cnpj'],
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                status='active'
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
    seller = get_object_or_404(Seller, id=application_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        
        if action == 'approve':
            # Aprova o vendedor
            seller.status = 'Aprovado'
            seller.is_approved = True
            seller.save()
            
            # Ativa o usuário
            user = seller.user
            user.is_active = True
            user.save()
            
            messages.success(request, 'Vendedor aprovado com sucesso!')
        elif action == 'reject':
            # Rejeita o vendedor
            seller.status = 'Reprovado'
            seller.is_approved = False
            seller.save()
            messages.success(request, 'Vendedor reprovado.')
        
        return redirect('core:superadmin_dashboard')
    
    context = {
        'application': seller,
    }
    return render(request, 'core/review_application.html', context)

@login_required
@user_passes_test(is_superadmin)
def category_list(request):
    """Lista todas as categorias"""
    categories = Category.objects.all().order_by('name')
    context = {
        'categories': categories,
    }
    return render(request, 'core/category_list.html', context)

@login_required
@user_passes_test(is_superadmin)
def category_create(request):
    """Cria uma nova categoria via AJAX"""
    logger.info(f"Requisição de criação de categoria recebida: {request.method}")
    logger.info(f"Headers: {request.headers}")
    logger.info(f"POST data: {request.POST}")
    
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            
            logger.info(f"Dados recebidos - Nome: {name}, Descrição: {description}")
            
            if not name:
                logger.warning("Tentativa de criar categoria sem nome")
                return JsonResponse({'success': False, 'error': 'O nome da categoria é obrigatório.'})
            
            category = Category.objects.create(
                name=name,
                description=description
            )
            
            logger.info(f"Categoria criada com sucesso: {category.id}")
            
            return JsonResponse({
                'success': True,
                'category': {
                    'id': category.id,
                    'name': category.name
                }
            })
        except Exception as e:
            logger.error(f"Erro ao criar categoria: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    logger.warning(f"Método não permitido: {request.method}")
    return JsonResponse({'success': False, 'error': 'Método não permitido.'})

@login_required
@user_passes_test(is_superadmin)
def category_update(request, pk):
    """Atualiza uma categoria existente"""
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        
        if name:
            category.name = name
            category.description = description
            category.save()
            messages.success(request, 'Categoria atualizada com sucesso!')
            return redirect('core:category_list')
        else:
            messages.error(request, 'O nome da categoria é obrigatório.')
    
    context = {
        'category': category,
        'title': 'Editar Categoria',
    }
    return render(request, 'core/category_form.html', context)

@login_required
@user_passes_test(is_superadmin)
def category_delete(request, pk):
    """Exclui uma categoria"""
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        # Verifica se existem produtos associados à categoria
        if category.products.exists():
            messages.error(request, 'Não é possível excluir uma categoria que possui produtos associados.')
            return redirect('core:category_list')
        
        category.delete()
        messages.success(request, 'Categoria excluída com sucesso!')
        return redirect('core:category_list')
    
    context = {
        'category': category,
    }
    return render(request, 'core/category_confirm_delete.html', context)

@login_required
@user_passes_test(is_superadmin)
def seller_detail(request, seller_id):
    """Visualização detalhada de um vendedor"""
    seller = get_object_or_404(Seller, id=seller_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        
        if action == 'approve':
            seller.status = 'Aprovado'
            seller.is_approved = True
            seller.user.is_active = True
            seller.user.save()
            seller.save()
            messages.success(request, 'Vendedor aprovado com sucesso!')
        elif action == 'reject':
            seller.status = 'Reprovado'
            seller.is_approved = False
            seller.user.is_active = False
            seller.user.save()
            seller.save()
            messages.success(request, 'Vendedor reprovado.')
        
        return redirect('core:seller_detail', seller_id=seller.id)
    
    context = {
        'seller': seller,
    }
    return render(request, 'core/seller_detail.html', context)

@login_required
@user_passes_test(is_superadmin)
def superadmin_product_update(request, pk):
    """View para atualizar um produto como superadmin"""
    product = get_object_or_404(Product, pk=pk)
    title = f'Editar Produto: {product.name}'
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto atualizado com sucesso!')
            return redirect('core:superadmin_products')
        else:
            messages.error(request, 'Por favor, corrija os erros abaixo.')
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'title': title,
        'categories': Category.objects.all().order_by('name')
    }
    return render(request, 'core/product_form.html', context)
