from django.db import models
from django.conf import settings
from produtos.models import Produto
from django.utils import timezone

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
    quantidade = models.IntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    preco_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE')
    observacoes = models.TextField(blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_venda = models.DateTimeField(null=True, blank=True)
    estoque_atualizado = models.BooleanField(default=False)

    def __str__(self):
        return f"Venda {self.id} - {self.produto.nome}"

    def save(self, *args, **kwargs):
        if not self.preco_unitario and self.produto:
            self.preco_unitario = self.produto.preco
        
        if not self.preco_total and self.quantidade and self.preco_unitario:
            self.preco_total = self.quantidade * self.preco_unitario

        if self.pk:  # Se é uma atualização
            old_instance = Venda.objects.get(pk=self.pk)
            
            # Impede cancelar venda já aprovada
            if old_instance.status == 'ACEITO' and self.status == 'CANCELADO':
                raise ValueError("Não é possível cancelar uma venda já aprovada.")
            
            # Atualiza estoque quando aceita a venda
            if (old_instance.status != 'ACEITO' and self.status == 'ACEITO' and 
                not self.estoque_atualizado and self.produto.quantidade >= self.quantidade):
                self.produto.quantidade -= self.quantidade
                self.produto.save()
                self.estoque_atualizado = True
                self.data_venda = timezone.now()

        super().save(*args, **kwargs)

class Pedido(models.Model):
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('ACEITO', 'Aceito'),
        ('REJEITADO', 'Rejeitado'),
        ('CANCELADO', 'Cancelado'),
    ]

    vendedor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='pedidos')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDENTE')
    data_pedido = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    observacoes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Pedido {self.id} - {self.vendedor.username}"

    def get_total(self):
        return sum(item.get_total() for item in self.itens.all())

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    preco_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Item {self.id} - {self.produto.nome}"

    def get_total(self):
        return self.quantidade * self.preco_unitario

    def save(self, *args, **kwargs):
        self.preco_total = self.get_total()
        super().save(*args, **kwargs)
