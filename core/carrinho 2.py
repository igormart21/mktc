from decimal import Decimal
from django.conf import settings
from produtos.models import Produto
from django.db import models

class Carrinho(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='carrinhos')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Carrinho'
        verbose_name_plural = 'Carrinhos'

    def __str__(self):
        return f'Carrinho de {self.usuario.username}'

    @property
    def total(self):
        return sum(item.total for item in self.itens.all())

    def adicionar_item(self, produto, quantidade=1):
        """Adiciona um item ao carrinho ou atualiza sua quantidade"""
        if not produto.ativo:
            raise ValueError("Este produto não está disponível")
            
        item, created = self.itens.get_or_create(
            produto=produto,
            defaults={
                'preco_unitario': produto.preco,
                'quantidade': quantidade
            }
        )
        
        if not created:
            item.quantidade += quantidade
            item.save()
            
        return item

    def remover_item(self, produto):
        """Remove um item do carrinho"""
        self.itens.filter(produto=produto).delete()

    def atualizar_quantidade(self, produto, quantidade):
        """Atualiza a quantidade de um item"""
        if quantidade <= 0:
            self.remover_item(produto)
            return
            
        item = self.itens.filter(produto=produto).first()
        if item:
            item.quantidade = quantidade
            item.save()

    def limpar(self):
        """Remove todos os itens do carrinho"""
        self.itens.all().delete()

class ItemCarrinho(models.Model):
    carrinho = models.ForeignKey(Carrinho, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = 'Item do Carrinho'
        verbose_name_plural = 'Itens do Carrinho'
        unique_together = ['carrinho', 'produto']

    def __str__(self):
        return f'{self.quantidade} x {self.produto.nome}'

    @property
    def total(self):
        return self.quantidade * self.preco_unitario

    def save(self, *args, **kwargs):
        if not self.preco_unitario:
            self.preco_unitario = self.produto.preco
        super().save(*args, **kwargs)

    def adicionar(self, produto, quantidade=1, atualizar_quantidade=False):
        produto_id = str(produto.id)
        if produto_id not in self.carrinho:
            self.carrinho[produto_id] = {
                'quantidade': 0,
                'preco': str(produto.preco)
            }
        if atualizar_quantidade:
            self.carrinho[produto_id]['quantidade'] = quantidade
        else:
            self.carrinho[produto_id]['quantidade'] += quantidade
        self.salvar()

    def remover(self, produto):
        produto_id = str(produto.id)
        if produto_id in self.carrinho:
            del self.carrinho[produto_id]
            self.salvar()

    def salvar(self):
        self.session.modified = True

    def __iter__(self):
        produto_ids = self.carrinho.keys()
        produtos = Produto.objects.filter(id__in=produto_ids)
        carrinho = self.carrinho.copy()
        for produto in produtos:
            carrinho[str(produto.id)]['produto'] = produto
        for item in carrinho.values():
            item['preco'] = Decimal(item['preco'])
            item['preco_total'] = item['preco'] * item['quantidade']
            yield item

    def __len__(self):
        return sum(item['quantidade'] for item in self.carrinho.values())

    def get_preco_total(self):
        return sum(Decimal(item['preco']) * item['quantidade'] for item in self.carrinho.values()) 