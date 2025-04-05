from django.db import models
from django.core.validators import MinValueValidator, FileExtensionValidator
from vendedores.models import Vendedor
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
import os
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

def validate_image_size(value):
    # Verifica se a imagem não está corrompida
    try:
        img = Image.open(value)
        img.verify()
    except Exception as e:
        raise ValidationError('Arquivo de imagem corrompido ou inválido')

def validate_image_dimensions(value):
    # Verifica dimensões mínimas
    img = Image.open(value)
    if img.width < 300 or img.height < 300:
        raise ValidationError('A imagem deve ter pelo menos 300x300 pixels')

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
    validade = models.DateTimeField(default=timezone.now, blank=True, null=True)
    permite_troca = models.BooleanField(default=False, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    estoque = models.PositiveIntegerField(null=True, blank=True)
    estoque_inicial = models.PositiveIntegerField(null=True, blank=True)
    imagem = models.ImageField(
        upload_to='produtos/',
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png']),
            validate_image_size,
            validate_image_dimensions
        ],
        null=True,
        blank=True
    )

    def save(self, *args, **kwargs):
        # Verifica se é um novo produto ou atualização
        if not self.pk:  # Novo produto
            self.estoque_inicial = self.estoque
        
        # Processa a imagem antes de salvar
        if self.imagem:
            try:
                # Abre a imagem
                img = Image.open(self.imagem)
                
                # Converte para RGB se necessário
                if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                    img = img.convert('RGB')
                
                # Redimensiona se for muito grande
                if img.width > 1200 or img.height > 1200:
                    output_size = (1200, 1200)
                    img.thumbnail(output_size, Image.LANCZOS)
                
                # Salva a imagem otimizada
                buffer = BytesIO()
                img.save(buffer, format='JPEG', quality=85, optimize=True)
                buffer.seek(0)
                
                # Gera novo nome para o arquivo
                filename = os.path.basename(self.imagem.name)
                name, ext = os.path.splitext(filename)
                new_filename = f"{name}_optimized.jpg"
                
                # Salva o arquivo otimizado
                self.imagem.save(new_filename, ContentFile(buffer.getvalue()), save=False)
                
            except Exception as e:
                raise ValidationError(f'Erro ao processar imagem: {str(e)}')
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nome} - {self.vendedor.usuario.nome if self.vendedor else 'Sem vendedor'}"

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['-created_at']
