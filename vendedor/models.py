from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

class Vendedor(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vendedor')
    nome_fantasia = models.CharField(max_length=200, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True, null=True)
    endereco = models.CharField(max_length=200, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=2, blank=True, null=True)
    cep = models.CharField(max_length=9, blank=True, null=True)
    hectares_atendidos = models.IntegerField(
        default=10,
        null=False,
        blank=False,
        help_text='Quantidade de hectares atendidos pelo vendedor (entre 10 e 300)',
        validators=[
            MinValueValidator(10, message='O mínimo de hectares é 10'),
            MaxValueValidator(300, message='O máximo de hectares é 300')
        ]
    )
    rg = models.FileField(upload_to='documentos/rg/', blank=True, null=True)
    cnh = models.FileField(upload_to='documentos/cnh/', blank=True, null=True)
    data_aprovacao = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nome_fantasia or self.usuario.username}"

    class Meta:
        verbose_name = 'Vendedor'
        verbose_name_plural = 'Vendedores'
        ordering = ['-created_at']
