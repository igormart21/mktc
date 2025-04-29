from django.db import models
from django.conf import settings
from decimal import Decimal
from django.db.models import F, Sum
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
import os
from vendedor.models import Vendedor
from usuarios.models import Usuario
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from produtos.models import Produto

def product_image_path(instance, filename):
    return f'products/{filename}'

class Product(models.Model):
    UNIT_CHOICES = [
        ('kg', 'Quilograma (kg)'),
        ('l', 'Litro (L)'),
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

    CURRENCY_CHOICES = [
        ('BRL', 'Real (R$)'),
        ('USD', 'Dólar ($)'),
        ('EUR', 'Euro (€)'),
    ]

    name = models.CharField(max_length=200, verbose_name='Nome')
    description = models.TextField(blank=True, verbose_name='Descrição')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Preço')
    available_volume = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Volume Disponível')
    unit = models.CharField(max_length=2, choices=UNIT_CHOICES, verbose_name='Unidade')
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES, verbose_name='Tipo de Produto')
    packaging = models.CharField(max_length=50, default='Saco', verbose_name='Embalagem')
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='BRL', verbose_name='Moeda')
    image = models.ImageField(upload_to=product_image_path, blank=True, null=True, verbose_name='Imagem')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, verbose_name='Ativo')
    manufacturer = models.CharField(max_length=100, blank=True, null=True, verbose_name='Fabricante')
    lot = models.CharField(max_length=50, blank=True, null=True, verbose_name='Lote')
    expiration_date = models.DateField(null=True, blank=True, verbose_name='Data de Validade')
    minimum_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Quantidade Mínima')
    sieve = models.CharField(max_length=50, blank=True, null=True, verbose_name='Peneira')
    variety = models.CharField(max_length=100, blank=True, null=True, verbose_name='Variedade')
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

class SellerRegistration(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado'),
    ]

    DOCUMENT_TYPES = [
        ('RG', 'RG'),
        ('CNH', 'CNH'),
    ]

    nome = models.CharField(max_length=100, null=True, blank=True)
    sobrenome = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    cpf = models.CharField(max_length=14, null=True, blank=True)
    telefone = models.CharField(max_length=20, null=True, blank=True)
    endereco = models.CharField(max_length=255, null=True, blank=True)
    cidade = models.CharField(max_length=100, null=True, blank=True)
    estado = models.CharField(max_length=2, null=True, blank=True)
    cep = models.CharField(max_length=9, null=True, blank=True)
    tipo_documento = models.CharField(max_length=3, choices=DOCUMENT_TYPES, null=True, blank=True)
    numero_documento = models.CharField(max_length=20, null=True, blank=True)
    documento = models.FileField(upload_to='documentos/', null=True, blank=True)
    hectares_atendidos = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    culturas_atendidas = models.CharField(max_length=255, null=True, blank=True)  # pode ser um campo de texto separado por vírgula
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pendente')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    observacoes = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Cadastro de Vendedor'
        verbose_name_plural = 'Cadastros de Vendedores'
        ordering = ['-data_criacao']

    def __str__(self):
        return f"Cadastro de {self.nome} {self.sobrenome} - {self.email}"

    def get_culturas_descricao(self):
        if not self.culturas_atendidas:
            return ""
        chaves = [c.strip() for c in self.culturas_atendidas.split(',') if c.strip()]
        descricoes = [dict(CULTURAS_CHOICES).get(chave, chave) for chave in chaves]
        return ', '.join(descricoes)

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
    UNIDADE_MEDIDA_CHOICES = [
        ('ton', 'Tonelada'),
        ('kg', 'Quilograma'),
        ('l', 'Litro'),
        ('un', 'Unidade'),
        ('cx', 'Caixa'),
        ('sc', 'Saco')
    ]

    TIPO_PRODUTO_CHOICES = [
        ('ins', 'Insumo'),
        ('sem', 'Semente'),
        ('def', 'Defensivo'),
        ('fer', 'Fertilizante'),
        ('equ', 'Equipamento'),
        ('out', 'Outro')
    ]

    EMBALAGEM_CHOICES = [
        ('big', 'Big Bag'),
        ('sac', 'Saco'),
        ('cax', 'Caixa'),
        ('gal', 'Galão'),
        ('bom', 'Bombona'),
        ('con', 'Container'),
        ('out', 'Outro')
    ]

    vendedor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='solicitacoes', verbose_name='Vendedor', null=True, blank=True)
    nome_produto = models.CharField(max_length=100, verbose_name='Nome do Produto', null=True, blank=True)
    descricao = models.TextField(verbose_name='Descrição', null=True, blank=True)
    categoria_sugerida = models.CharField(max_length=50, verbose_name='Categoria Sugerida', null=True, blank=True)
    quantidade = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Volume', null=True, blank=True)
    unidade_medida = models.CharField(max_length=3, choices=UNIDADE_MEDIDA_CHOICES, verbose_name='Unidade de Medida', null=True, blank=True)
    fabricante = models.CharField(max_length=100, verbose_name='Fabricante', default='Não especificado', null=True, blank=True)
    tipo_produto = models.CharField(max_length=3, choices=TIPO_PRODUTO_CHOICES, blank=True, null=True, verbose_name='Tipo de Produto')
    lote = models.CharField(max_length=50, blank=True, null=True, verbose_name='Lote')
    peneira = models.CharField(max_length=50, blank=True, null=True, verbose_name='Peneira')
    variedade = models.CharField(max_length=100, blank=True, null=True, verbose_name='Variedade')
    embalagem = models.CharField(max_length=3, choices=EMBALAGEM_CHOICES, blank=True, null=True, verbose_name='Embalagem')
    data_validade = models.DateField(blank=True, null=True, verbose_name='Data de Validade')
    observacoes = models.TextField(blank=True, null=True, verbose_name='Observações Adicionais')
    data_solicitacao = models.DateTimeField(auto_now_add=True, verbose_name='Data da Solicitação')
    status = models.CharField(max_length=20, default='pendente', choices=[
        ('pendente', 'Pendente'),
        ('aprovado', 'Aprovado'),
        ('rejeitado', 'Rejeitado')
    ], verbose_name='Status')
    resposta_superadmin = models.TextField(blank=True, null=True, verbose_name='Resposta do Administrador')

    class Meta:
        verbose_name = 'Solicitação de Produto'
        verbose_name_plural = 'Solicitações de Produtos'
        ordering = ['-data_solicitacao']

    def __str__(self):
        return f"Solicitação de {self.nome_produto} por {self.vendedor.username if self.vendedor else 'Usuário não especificado'}"

class Usuario(AbstractUser):
    username = None
    first_name = None
    last_name = None
    
    nome = models.CharField(max_length=100, verbose_name='Nome', null=True, blank=True)
    sobrenome = models.CharField(max_length=100, verbose_name='Sobrenome', null=True, blank=True)
    email = models.EmailField(unique=True, verbose_name='E-mail', null=True, blank=True)
    cpf = models.CharField(max_length=11, unique=True, verbose_name='CPF', null=True, blank=True)
    telefone = models.CharField(max_length=20, verbose_name='Telefone', null=True, blank=True)
    cep = models.CharField(max_length=9, verbose_name='CEP', null=True, blank=True)
    endereco = models.CharField(max_length=255, verbose_name='Endereço', null=True, blank=True)
    cidade = models.CharField(max_length=100, verbose_name='Cidade', null=True, blank=True)
    estado = models.CharField(max_length=2, verbose_name='Estado', null=True, blank=True)
    tipo_documento = models.CharField(
        max_length=3,
        choices=[('RG', 'RG'), ('CNH', 'CNH')],
        verbose_name='Tipo de Documento',
        null=True,
        blank=True
    )
    numero_documento = models.CharField(max_length=20, verbose_name='Número do Documento', null=True, blank=True)
    arquivo_documento = models.FileField(upload_to='documentos/', verbose_name='Arquivo do Documento', null=True, blank=True)
    hectares_atendidos = models.IntegerField(
        default=10,
        validators=[MinValueValidator(10), MaxValueValidator(300)],
        verbose_name='Quantidade de Hectares Atendidos',
        null=True,
        blank=True
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    def __str__(self):
        return f"{self.nome} {self.sobrenome}" if self.nome and self.sobrenome else self.email

CULTIVO_CHOICES = [
    ('feijao', 'Feijão'),
    ('algodao', 'Algodão'),
    ('gergelim', 'Gergelim'),
    ('pastagem', 'Pastagem'),
    ('milho', 'Milho'),
    ('soja', 'Soja'),
]

class Pedido(models.Model):
    STATUS_CHOICES = (
        ('PENDENTE', 'Pendente'),
        ('APROVADO', 'Aprovado'),
        ('REPROVADO', 'Reprovado'),
    )

    TIPO_VENDA_CHOICES = [
        ('avista', 'À Vista'),
        ('prazo', 'A Prazo'),
    ]

    comprador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pedidos')
    vendedor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='pedidos_como_vendedor', null=True, blank=True)
    nome_propriedade = models.CharField(max_length=100)
    cnpj = models.CharField(max_length=18)
    hectares = models.DecimalField(max_digits=10, decimal_places=2)
    cultivo_principal = models.CharField(max_length=20, choices=CULTIVO_CHOICES)
    estado = models.CharField(max_length=2)
    cidade = models.CharField(max_length=100)
    endereco = models.CharField(max_length=200)
    cep = models.CharField(max_length=9)
    referencia = models.CharField(max_length=200, blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    tipo_venda = models.CharField(max_length=10, choices=TIPO_VENDA_CHOICES, default='avista')
    documento_ir = models.FileField(upload_to='documentos/ir/', null=True, blank=True)
    inscricao_estadual = models.FileField(upload_to='documentos/inscricao_estadual/', null=True, blank=True)
    documento_matricula = models.FileField(upload_to='documentos/matricula/', null=True, blank=True)
    is_arrendatario = models.BooleanField(default=False)
    documento_arrendamento = models.FileField(upload_to='documentos/arrendamento/', null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    justificativa_reprovacao = models.TextField(blank=True, null=True)
    aprovado_por = models.ForeignKey('usuarios.Usuario', null=True, blank=True, on_delete=models.SET_NULL, related_name='pedidos_aprovados')
    aprovado_em = models.DateTimeField(null=True, blank=True)
    reprovado_por = models.ForeignKey('usuarios.Usuario', null=True, blank=True, on_delete=models.SET_NULL, related_name='pedidos_reprovados')
    reprovado_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-data_criacao']

    def __str__(self):
        return f'Pedido #{self.id} - {self.nome_propriedade}'

    def calcular_total(self):
        total_itens = sum(item.total for item in self.itens.all())
        total_vendas = sum(venda.total for venda in self.vendas.all())
        self.total = total_itens + total_vendas
        self.save()
        return self.total

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
    quantidade = models.PositiveIntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.total = self.quantidade * self.preco_unitario
        super().save(*args, **kwargs)
        self.pedido.calcular_total()

    def __str__(self):
        return f'Item #{self.id} - {self.produto.nome} ({self.quantidade})'

class Venda(models.Model):
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('PROCESSANDO', 'Processando'),
        ('APROVADO', 'Aprovado'),
        ('REJEITADO', 'Rejeitado'),
        ('ENTREGUE', 'Entregue'),
    ]

    vendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE, related_name='vendas')
    comprador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='compras')
    produto = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='vendas')
    quantidade = models.PositiveIntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE')
    pedido = models.ForeignKey(Pedido, on_delete=models.SET_NULL, null=True, blank=True, related_name='vendas')
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-data_criacao']

    def __str__(self):
        return f'Venda #{self.id} - {self.produto.nome}'

    def save(self, *args, **kwargs):
        # Calcula o total antes de salvar
        self.total = self.quantidade * self.preco_unitario
        super().save(*args, **kwargs)
        
        # Atualiza o total do pedido se existir
        if self.pedido:
            self.pedido.calcular_total()
