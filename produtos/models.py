from django.db import models
from django.core.validators import MinValueValidator
from vendedor.models import Vendedor
from django.utils import timezone

def product_image_path(instance, filename):
    return f'produtos/{filename}'

class Produto(models.Model):
    UNIDADE_CHOICES = [
        ('kg', 'Quilograma (kg)'),
        ('l', 'Litro (L)'),
        ('un', 'Unidade (un)'),
    ]

    TIPO_CHOICES = [
        ('soja', 'Soja'),
        ('milho', 'Milho'),
        ('pastagem', 'Pastagem'),
        ('sorgo', 'Sorgo'),
    ]

    MOEDA_CHOICES = [
        ('BRL', 'Real (R$)'),
        ('USD', 'Dólar ($)'),
        ('EUR', 'Euro (€)'),
    ]

    CATEGORIA_CHOICES = [
        ('HERBICIDA', 'Herbicida'),
        ('INSETICIDA', 'Inseticida'),
        ('FUNGICIDA', 'Fungicida'),
        ('OLEO_MINERAL', 'Óleo Mineral'),
        ('SEMENTE', 'Semente'),
    ]

    TIPO_SEMENTE_CHOICES = [
        ('branca', 'Semente Branca'),
        ('tratada', 'Semente Tratada'),
    ]

    # Campos básicos
    nome = models.CharField(max_length=200)
    categoria = models.CharField(max_length=100, choices=CATEGORIA_CHOICES)
    descricao = models.TextField(blank=True)
    core_product_id = models.PositiveIntegerField(null=True, blank=True, unique=True, verbose_name='ID do Produto Core')
    
    # Preço e volume
    preco = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    moeda = models.CharField(max_length=3, choices=MOEDA_CHOICES, default='BRL')
    volume_disponivel = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unidade_medida = models.CharField(max_length=2, choices=UNIDADE_CHOICES, default='un')
    
    # Classificação
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='soja')
    embalagem = models.CharField(max_length=50, default='Saco')
    
    # Informações adicionais
    fabricante = models.CharField(max_length=100, blank=True, null=True)
    lote = models.CharField(max_length=50, blank=True, null=True)
    validade = models.DateField(null=True, blank=True)
    quantidade_minima = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Informações da semente
    peneira = models.CharField(max_length=50, blank=True, null=True)
    variedade = models.CharField(max_length=100, blank=True, null=True)
    
    # Imagem
    imagem = models.ImageField(upload_to=product_image_path, null=True, blank=True)
    
    # Status
    ativo = models.BooleanField(default=True)
    
    # Metadados
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    tipo_da_semente = models.CharField(
        max_length=20,
        choices=TIPO_SEMENTE_CHOICES,
        blank=True,
        null=True,
        verbose_name='Tipo da Semente'
    )
    tratamento_da_semente = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Tratamento da Semente'
    )

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['-created_at']

    def __str__(self):
        return self.nome

    def get_categoria_display(self):
        """Retorna o valor de exibição para o campo categoria"""
        return dict(self.CATEGORIA_CHOICES).get(self.categoria, self.categoria)

    def get_tipo_display(self):
        """Retorna o valor de exibição para o campo tipo"""
        return dict(self.TIPO_CHOICES).get(self.tipo, self.tipo)

    def get_unidade_medida_display(self):
        """Retorna o valor de exibição para o campo unidade_medida"""
        return dict(self.UNIDADE_CHOICES).get(self.unidade_medida, self.unidade_medida)

    def get_moeda_display(self):
        """Retorna o valor de exibição para o campo moeda"""
        return dict(self.MOEDA_CHOICES).get(self.moeda, self.moeda)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.quantidade_minima and self.quantidade_minima > self.volume_disponivel:
            raise ValidationError('A quantidade mínima não pode ser maior que o volume disponível.')
        if self.volume_disponivel < 0:
            raise ValidationError('O volume disponível não pode ser negativo.')
        if self.preco is None:
            raise ValidationError('O preço é obrigatório.')
        if self.preco < 0:
            raise ValidationError('O preço não pode ser negativo.')
