from django.db import models
from django.core.validators import MinValueValidator
from vendedor.models import Vendedor
from django.utils import timezone

class Produto(models.Model):
    CATEGORIAS = [
        ('SEMENTES', 'Sementes'),
        ('FERTILIZANTES', 'Fertilizantes'),
        ('DEFENSIVOS', 'Defensivos'),
        ('MAQUINARIOS', 'Maquinários'),
        ('OUTROS', 'Outros'),
    ]

    TIPOS = [
        ('SOJA', 'Soja'),
        ('MILHO', 'Milho'),
        ('CAFE', 'Café'),
        ('OUTROS', 'Outros'),
    ]

    UNIDADES_MEDIDA = [
        ('KG', 'Quilograma'),
        ('TON', 'Tonelada'),
        ('L', 'Litro'),
        ('ML', 'Mililitro'),
        ('UN', 'Unidade'),
    ]

    MOEDAS = [
        ('BRL', 'Real'),
        ('USD', 'Dólar'),
    ]

    nome = models.CharField(max_length=200)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    quantidade = models.IntegerField(validators=[MinValueValidator(0)], blank=True, null=True)
    vendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE, related_name='produtos', blank=True, null=True)
    categoria = models.CharField(max_length=100, choices=CATEGORIAS, default='OUTROS', blank=True, null=True)
    tipo = models.CharField(max_length=100, choices=TIPOS, default='OUTROS', blank=True, null=True)
    peneira = models.CharField(max_length=100, blank=True, null=True)
    variedade = models.CharField(max_length=100, blank=True, null=True)
    lote = models.CharField(max_length=100, blank=True, null=True)
    volume_disponivel = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)
    unidade_medida = models.CharField(max_length=50, choices=UNIDADES_MEDIDA, default='UN', blank=True, null=True)
    embalagem = models.CharField(max_length=100, blank=True, null=True)
    moeda = models.CharField(max_length=10, choices=MOEDAS, default='BRL', blank=True, null=True)
    fabricante = models.CharField(max_length=100, blank=True, null=True)
    quantidade_minima = models.IntegerField(default=1, blank=True, null=True)
    validade = models.DateField(default=timezone.now, blank=True, null=True)
    permite_troca = models.BooleanField(default=False, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nome} - {self.vendedor.usuario.nome if self.vendedor else 'Sem vendedor'}"

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['-created_at']
