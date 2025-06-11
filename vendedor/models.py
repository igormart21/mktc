from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class Vendedor(models.Model):
    CULTURAS_CHOICES = [
        ('SOJA', 'Soja'),
        ('MILHO', 'Milho'),
        ('ALGODAO', 'Algodão'),
        ('FEIJAO', 'Feijão'),
        ('GERGELIM', 'Gergelim'),
        ('GIRASOL', 'Girasol'),
        ('PASTAGEM', 'Pastagem'),
        ('MILHO_PIPOCA', 'Milho Pipoca'),
        ('ARROZ', 'Arroz'),
        ('PECUARIA', 'Pecuária'),
    ]

    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vendedor')
    nome_fantasia = models.CharField(max_length=200, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    endereco = models.CharField(max_length=200, blank=True, null=True)
    numero = models.CharField(max_length=10, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True)
    cep = models.CharField(max_length=9, blank=True, null=True)
    culturas_atendidas = models.JSONField(default=list, blank=True, help_text='Lista de culturas atendidas pelo vendedor')
    hectares_livres = models.IntegerField(
        help_text='Quantidade de hectares atendidos pelo vendedor'
    )
    rg = models.FileField(upload_to='documentos/rg/', blank=True, null=True)
    rg_verso = models.FileField(upload_to='documentos/rg/', blank=True, null=True)
    cnh = models.FileField(upload_to='documentos/cnh/', blank=True, null=True)
    cnh_verso = models.FileField(upload_to='documentos/cnh/', blank=True, null=True)
    data_aprovacao = models.DateTimeField(null=True, blank=True)
    status_aprovacao = models.CharField(
        max_length=10,
        choices=[('PENDENTE', 'Pendente'), ('APROVADO', 'Aprovado'), ('RECUSADO', 'Recusado')],
        default='PENDENTE',
        verbose_name='Status de Aprovação'
    )
    justificativa_recusa = models.TextField(blank=True, null=True, verbose_name='Justificativa da Recusa')
    
    data_criacao = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nome_fantasia or self.usuario.email}"

    class Meta:
        verbose_name = 'Vendedor'
        verbose_name_plural = 'Vendedores'
        ordering = ['-data_criacao']
