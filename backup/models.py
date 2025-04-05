from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from django.db.models import F, Sum
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
import os

def seller_document_path(instance, filename):
    # O arquivo será salvo em MEDIA_ROOT/seller_documents/user_<id>/<filename>
    return f'seller_documents/user_{instance.user.id}/{filename}'

def product_image_path(instance, filename):
    return f'products/{filename}'

class Seller(models.Model):
    STATUS_CHOICES = [
        ('Pendente', 'Pendente'),
        ('Aprovado', 'Aprovado'),
        ('Reprovado', 'Reprovado'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, verbose_name='Nome Completo', null=True, blank=True)
    cpf = models.CharField(max_length=14, unique=True, verbose_name='CPF', null=True, blank=True)
    document_type = models.CharField(max_length=3, choices=[('RG', 'RG'), ('CNH', 'CNH')], verbose_name='Tipo de Documento', null=True, blank=True)
    document_number = models.CharField(max_length=20, unique=True, verbose_name='Número do Documento', null=True, blank=True)
    document_file = models.FileField(
        upload_to=seller_document_path,
        verbose_name='Documento',
        help_text='Faça o upload do documento (RG ou CNH)',
        null=True,
        blank=True
    )
    phone = models.CharField(max_length=20, verbose_name='Telefone', null=True, blank=True)
    cep = models.CharField(max_length=9, verbose_name='CEP', null=True, blank=True)
    address = models.CharField(max_length=200, verbose_name='Endereço', null=True, blank=True)
    number = models.CharField(max_length=10, verbose_name='Número', null=True, blank=True)
    complement = models.CharField(max_length=100, verbose_name='Complemento', null=True, blank=True)
    neighborhood = models.CharField(max_length=100, verbose_name='Bairro', null=True, blank=True)
    city = models.CharField(max_length=100, verbose_name='Cidade', null=True, blank=True)
    state = models.CharField(max_length=2, verbose_name='Estado', null=True, blank=True)
    hectares = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Quantidade de Hectares', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pendente', verbose_name='Status')
    is_approved = models.BooleanField(default=False, verbose_name='Aprovado')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Data de Cadastro')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Data de Atualização')

    def __str__(self):
        return self.full_name or 'Vendedor sem nome'

    def clean(self):
        from .utils import validate_cpf
        if self.cpf and not validate_cpf(self.cpf):
            raise ValidationError('CPF inválido.')

    class Meta:
        verbose_name = 'Vendedor'
        verbose_name_plural = 'Vendedores'
        ordering = ['-created_at']

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['name']

    def __str__(self):
        return self.name

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

    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available_volume = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES)
    is_active = models.BooleanField(default=True)
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES)
    manufacturer = models.CharField(max_length=100, blank=True, null=True)
    lot = models.CharField(max_length=50, blank=True, null=True)
    expiration_date = models.DateField(null=True, blank=True)
    minimum_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    packaging = models.CharField(max_length=20, choices=PACKAGING_CHOICES, blank=True, null=True)
    sieve = models.CharField(max_length=50, blank=True, null=True)
    variety = models.CharField(max_length=100, blank=True, null=True)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='BRL')
    allow_exchange = models.BooleanField(default=False)
    image = models.ImageField(upload_to=product_image_path, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
        currency_symbol = {
            'BRL': 'R$',
            'USD': '$',
            'EUR': '€'
        }.get(self.currency, self.currency)
        return f"{currency_symbol} {self.price:.2f}"

    def get_stock_display(self):
        return f"{self.available_volume} {self.get_unit_display()}"

class Order(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('em_preparacao', 'Em Preparação'),
        ('enviado', 'Enviado'),
        ('entregue', 'Entregue'),
        ('cancelado', 'Cancelado'),
    ]

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name='Cliente')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Data do Pedido')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Atualização')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente', verbose_name='Status')
    total_value = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Valor Total')
    notes = models.TextField(blank=True, null=True, verbose_name='Observações')

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-created_at']

    def __str__(self):
        return f'Pedido #{self.id} - {self.created_by.get_full_name()}'

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

    user = models.OneToOneField(User, on_delete=models.CASCADE)
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
        return f'Cadastro de {self.user.get_full_name()}'

class VendorApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('approved', 'Aprovado'),
        ('rejected', 'Rejeitado'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Aplicação de Vendedor'
        verbose_name_plural = 'Aplicações de Vendedores'
        ordering = ['-created_at']

    def __str__(self):
        return f'Aplicação de {self.user.get_full_name()}'
