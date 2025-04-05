from django.db import models
from django.conf import settings
from produtos.models import Produto
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from vendedores.models import Vendedor

class Venda(models.Model):
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('ACEITO', 'Aceito'),
        ('REJEITADO', 'Rejeitado'),
        ('CANCELADO', 'Cancelado'),
    ]

    comprador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vendas_compras')
    vendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE')
    observacoes = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    estoque_atualizado = models.BooleanField(default=False)
    aprovado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vendas_aprovadas'
    )
    data_aprovacao = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.produto.nome} - {self.get_status_display()}"

    def save(self, *args, **kwargs):
        if self.status == 'ACEITO' and not self.estoque_atualizado:
            if self.produto.quantidade > 0:
                self.produto.quantidade -= 1
                self.produto.save()
                self.estoque_atualizado = True
                self.aprovado_por = self.vendedor.usuario
                self.data_aprovacao = timezone.now()

        if self.observacoes:
            self.observacoes = strip_tags(self.observacoes)

        super().save(*args, **kwargs)

    def enviar_email_status(self):
        """Envia e-mail para o comprador sobre a mudança de status da venda."""
        if self.status == 'ACEITO':
            assunto = "Seu pedido foi aprovado"
            template = 'vendas/email_aprovado.html'
        else:
            assunto = "Seu pedido foi recusado"
            template = 'vendas/email_recusado.html'

        context = {
            'venda': self,
            'produto': self.produto,
            'vendedor': self.vendedor,
            'observacoes': self.observacoes
        }

        html_message = render_to_string(template, context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject=assunto,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.comprador.email],
            fail_silently=False,
        )
