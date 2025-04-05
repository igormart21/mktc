from django.db import models
from usuarios.models import Usuario

class Vendedor(models.Model):
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('APROVADO', 'Aprovado'),
        ('RECUSADO', 'Recusado'),
    ]

    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        verbose_name='Usuário'
    )
    cnpj = models.CharField(
        'CNPJ',
        max_length=14,
        unique=True,
        blank=True,
        null=True
    )
    razao_social = models.CharField(
        'Razão Social',
        max_length=100,
        blank=True,
        null=True
    )
    nome_fantasia = models.CharField(
        'Nome Fantasia',
        max_length=100,
        blank=True,
        null=True
    )
    inscricao_estadual = models.CharField(
        'Inscrição Estadual',
        max_length=20,
        blank=True,
        null=True
    )
    inscricao_municipal = models.CharField(
        'Inscrição Municipal',
        max_length=20,
        blank=True,
        null=True
    )
    status_aprovacao = models.CharField(
        'Status de Aprovação',
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDENTE'
    )
    observacoes = models.TextField(
        'Observações',
        blank=True,
        null=True
    )
    data_aprovacao = models.DateTimeField(
        'Data de Aprovação',
        blank=True,
        null=True
    )

    def __str__(self):
        return f'Vendedor: {self.usuario.nome}'

    class Meta:
        verbose_name = 'Vendedor'
        verbose_name_plural = 'Vendedores'
        db_table = 'vendedores'
