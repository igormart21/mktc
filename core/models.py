from django.db import models
from django.conf import settings
from decimal import Decimal
from django.db.models import F, Sum
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
import os
from vendedor.models import Vendedor
from usuarios.models import Usuario
from django.contrib.auth import get_user_model
from django.utils import timezone

def product_image_path(instance, filename):
    return f'products/{filename}'

class Product(models.Model):
    UNIT_CHOICES = [
        ('kg', 'Quilograma (kg)'),
        ('g', 'Grama (g)'),
        ('l', 'Litro (L)'),
        ('ml', 'Mililitro (mL)'),
        ('un', 'Unidade (un)'),
    ]

    PRODUCT_TYPE_CHOICES = [
        ('feijao', 'Feijão'),
        ('algodao', 'Algodão'),
        ('gergelim', 'Gergelim'),
        ('pastagem', 'Pastagem'),
        ('milho', 'Milho'),
        ('soja', 'Soja'),
    ]

    PACKAGING_CHOICES = [
        ('bag', 'Saco'),
        ('box', 'Caixa'),
        ('bottle', 'Garrafa'),
        ('can', 'Lata'),
        ('other', 'Outro'),
    ]

    CURRENCY_CHOICES = [
        ('BRL', 'Real (R$)'),
        ('USD', 'Dólar ($)'),
        ('EUR', 'Euro (€)'),
    ]

    name = models.CharField(max_length=200, verbose_name='Nome')
    description = models.TextField(blank=True, verbose_name='Descrição')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Preço')
    available_volume = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Volume Disponível')
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, verbose_name='Unidade')
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES, verbose_name='Tipo')
    manufacturer = models.CharField(max_length=100, blank=True, null=True, verbose_name='Fabricante')
    lot = models.CharField(max_length=50, blank=True, null=True, verbose_name='Lote')
    expiration_date = models.DateField(null=True, blank=True, verbose_name='Data de Validade')
    minimum_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Quantidade Mínima')
    packaging = models.CharField(max_length=20, choices=PACKAGING_CHOICES, blank=True, null=True, verbose_name='Embalagem')
    sieve = models.CharField(max_length=50, blank=True, null=True, verbose_name='Peneira')
    variety = models.CharField(max_length=100, blank=True, null=True, verbose_name='Variedade')
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='BRL', verbose_name='Moeda')
    allow_exchange = models.BooleanField(default=False, verbose_name='Permite Troca')
    image = models.ImageField(upload_to=product_image_path, null=True, blank=True, verbose_name='Imagem')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Atualizado em')
    seller = models.ForeignKey(Vendedor, on_delete=models.CASCADE, related_name='products', null=True, blank=True, verbose_name='Vendedor')

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_unit_display(self):
        return dict(self.UNIT_CHOICES).get(self.unit, self.unit)

    def get_product_type_display(self):
        return dict(self.PRODUCT_TYPE_CHOICES).get(self.product_type, self.product_type)

    def get_packaging_display(self):
        return dict(self.PACKAGING_CHOICES).get(self.packaging, self.packaging)

    def get_currency_display(self):
        return dict(self.CURRENCY_CHOICES).get(self.currency, self.currency)

    def clean(self):
        if self.available_volume < 0:
            raise ValidationError('O volume disponível não pode ser negativo.')
        if self.price < 0:
            raise ValidationError('O preço não pode ser negativo.')
        if self.minimum_quantity is not None and self.minimum_quantity < 0:
            raise ValidationError('A quantidade mínima não pode ser negativa.')
        if self.minimum_quantity is not None and self.minimum_quantity > self.available_volume:
            raise ValidationError('A quantidade mínima não pode ser maior que o volume disponível.')

    def get_price_display(self):
        currency_symbols = {
            'BRL': 'R$',
            'USD': '$',
            'EUR': '€'
        }
        symbol = currency_symbols.get(self.currency, self.currency)
        return f"{symbol} {self.price:.2f}"

    def get_stock_display(self):
        return f"{self.available_volume} {self.get_unit_display()}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('processing', 'Em Processamento'),
        ('shipped', 'Enviado'),
        ('delivered', 'Entregue'),
        ('cancelled', 'Cancelado'),
    ]

    customer_name = models.CharField(max_length=255, default='Cliente', verbose_name='Nome do Cliente')
    customer_email = models.EmailField(default='cliente@example.com', max_length=254, verbose_name='Email do Cliente')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Data do Pedido')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Atualização')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Status')
    total_value = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Valor Total')
    notes = models.TextField(blank=True, null=True, verbose_name='Observações')
    seller = models.ForeignKey(Vendedor, on_delete=models.CASCADE, related_name='orders', verbose_name='Vendedor', null=True, blank=True)

    @property
    def status_color(self):
        """Retorna a cor do badge baseada no status do pedido"""
        colors = {
            'pending': 'warning',
            'processing': 'info',
            'shipped': 'primary',
            'delivered': 'success',
            'cancelled': 'danger',
        }
        return colors.get(self.status, 'secondary')

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-created_at']

    def __str__(self):
        return f'Pedido #{self.id} - {self.customer_name}'

    def calculate_total(self):
        return sum(item.subtotal for item in self.items.all())

    def update_total(self):
        self.total_value = self.calculate_total()
        self.save()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name='Pedido')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Produto')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Quantidade')
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Preço Unitário', default=0)

    class Meta:
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens do Pedido'

    @property
    def subtotal(self):
        return self.quantity * self.unit_price

class SellerRegistration(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
    ]

    DOCUMENT_TYPES = [
        ('rg', 'RG'),
        ('cnh', 'CNH'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tipo_documento = models.CharField(max_length=3, choices=DOCUMENT_TYPES)
    numero_documento = models.CharField(max_length=20, unique=True)
    documento = models.FileField(upload_to='documentos/')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pendente')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    observacoes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Cadastro de Vendedor'
        verbose_name_plural = 'Cadastros de Vendedores'
        ordering = ['-data_criacao']

    def __str__(self):
        return f"Cadastro de {self.user.get_full_name()}"

class VendorApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('approved', 'Aprovado'),
        ('rejected', 'Rejeitado'),
    ]

    user = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200, default='')
    cnpj = models.CharField(max_length=14, unique=True, default='00000000000000')
    address = models.TextField(default='')
    phone = models.CharField(max_length=20, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    documents = models.FileField(upload_to='vendor_documents/', null=True, blank=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Aplicação de {self.company_name}'

class MensagemSuporte(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    assunto = models.CharField(max_length=200)
    mensagem = models.TextField()
    data_envio = models.DateTimeField(auto_now_add=True)
    respondido = models.BooleanField(default=False)
    resposta = models.TextField(blank=True, null=True)
    data_resposta = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Mensagem de Suporte'
        verbose_name_plural = 'Mensagens de Suporte'
        ordering = ['-data_envio']

    def __str__(self):
        return f"Mensagem de {self.usuario.get_full_name()} - {self.assunto}"

class SolicitacaoProduto(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovada', 'Aprovada'),
        ('rejeitada', 'Rejeitada')
    ]
    
    UNIDADE_CHOICES = [
        ('kg', 'Quilograma'),
        ('g', 'Grama'),
        ('l', 'Litro'),
        ('ml', 'Mililitro'),
        ('un', 'Unidade')
    ]
    
    nome_produto = models.CharField(max_length=200)
    descricao = models.TextField()
    categoria_sugerida = models.CharField(max_length=100)
    quantidade = models.PositiveIntegerField(default=1)
    unidade_medida = models.CharField(max_length=2, choices=UNIDADE_CHOICES, default='un')
    vendedor = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='solicitacoes_produto')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pendente')
    data_solicitacao = models.DateTimeField(auto_now_add=True)
    data_analise = models.DateTimeField(null=True, blank=True)
    resposta_superadmin = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'Solicitação de {self.nome_produto} por {self.vendedor.email}'

    class Meta:
        verbose_name = 'Solicitação de Produto'
        verbose_name_plural = 'Solicitações de Produtos'
