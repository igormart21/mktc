from django.contrib import admin
from .models import SellerRegistration, Product, Pedido

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

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ['id', 'comprador', 'vendedor', 'nome_propriedade', 'status', 'tipo_venda', 'data_criacao']
    list_filter = ['status', 'tipo_venda', 'data_criacao']
    search_fields = ['nome_propriedade', 'cnpj', 'cidade']
    readonly_fields = ['data_criacao', 'data_atualizacao']
