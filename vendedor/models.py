from django.db import models
from django.conf import settings
from django.utils import timezone

class Vendedor(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    cnpj = models.CharField(max_length=14, unique=True, blank=True, null=True)
    razao_social = models.CharField(max_length=200, blank=True, null=True)
    nome_fantasia = models.CharField(max_length=200, blank=True, null=True)
    inscricao_estadual = models.CharField(max_length=20, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    endereco = models.CharField(max_length=200, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True)
    cep = models.CharField(max_length=8, blank=True, null=True)
    hectares_atendidos = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    rg = models.FileField(upload_to='documentos/rg/', blank=True, null=True)
    cnh = models.FileField(upload_to='documentos/cnh/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nome_fantasia or self.razao_social or self.usuario.username}"

    class Meta:
        verbose_name = 'Vendedor'
        verbose_name_plural = 'Vendedores'
        ordering = ['-created_at']
