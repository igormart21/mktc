from django.contrib import admin
from .models import Order, OrderItem, SellerRegistration

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['subtotal']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'status', 'total_value', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['customer_name', 'customer_email', 'id']
    readonly_fields = ['total_value', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    
    def save_model(self, request, obj, form, change):
        if not change:  # Se é uma nova ordem
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'unit_price', 'subtotal')
    list_filter = ('order__status',)
    search_fields = ('order__id', 'product__name')

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
