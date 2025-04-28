from django.contrib import admin
from .models import SellerRegistration, Product, Pedido, ItemPedido
from produtos.models import Produto

@admin.register(SellerRegistration)
class SellerRegistrationAdmin(admin.ModelAdmin):
    list_display = ('nome', 'sobrenome', 'email', 'status', 'get_culturas_descricao', 'data_criacao')
    list_filter = ('status', 'tipo_documento')
    search_fields = ('nome', 'sobrenome', 'email', 'cpf', 'numero_documento')
    readonly_fields = ('data_criacao', 'data_atualizacao')
    
    def get_culturas_descricao(self, obj):
        return obj.get_culturas_descricao()
    get_culturas_descricao.short_description = 'Culturas Atendidas'

    class Meta:
        verbose_name = 'Cadastro de Vendedor'
        verbose_name_plural = 'Cadastros de Vendedores'

class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0
    fields = ['produto', 'quantidade', 'preco_unitario', 'total']
    readonly_fields = ['total']
    verbose_name = 'Item do Pedido'
    verbose_name_plural = 'Itens do Pedido'
    autocomplete_fields = ['produto']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('produto')

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['id', 'comprador', 'vendedor', 'nome_propriedade', 'status', 'tipo_venda', 'data_criacao']
    list_filter = ['status', 'tipo_venda', 'data_criacao']
    search_fields = ['nome_propriedade', 'cnpj', 'cidade']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    inlines = [ItemPedidoInline]
