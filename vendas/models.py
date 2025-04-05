from django.db import models
from django.conf import settings
from produtos.models import Produto

class Venda(models.Model):
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('ACEITO', 'Aceito'),
        ('REJEITADO', 'Rejeitado'),
        ('CANCELADO', 'Cancelado'),
    ]

    comprador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vendas_compras')
    vendedor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vendas_vendas')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE')
    observacoes = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    estoque_atualizado = models.BooleanField(default=False)

    def __str__(self):
        return f"Venda {self.id} - {self.produto.nome}"

    def save(self, *args, **kwargs):
        if self.pk:  # Se é uma atualização
            old_instance = Venda.objects.get(pk=self.pk)
            
            # Impede cancelar venda já aprovada
            if old_instance.status == 'ACEITO' and self.status == 'CANCELADO':
                raise ValueError("Não é possível cancelar uma venda já aprovada.")
            
            # Atualiza estoque quando aceita a venda
            if (old_instance.status != 'ACEITO' and self.status == 'ACEITO' and 
                not self.estoque_atualizado and self.produto.estoque > 0):
                self.produto.estoque -= 1
                self.produto.save()
                self.estoque_atualizado = True

        super().save(*args, **kwargs)
