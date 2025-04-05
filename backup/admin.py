from django.contrib import admin
from .models import Seller, Category, Product, Order, OrderItem, SellerRegistration

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'available_volume', 'unit', 'is_active', 'created_at')
    list_filter = ('is_active', 'category', 'product_type', 'created_at')
    search_fields = ('name', 'description', 'manufacturer')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20
    date_hierarchy = 'created_at'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category')

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'document_type', 'document_number', 'phone', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'document_type', 'created_at')
    search_fields = ('full_name', 'document_number')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20
    date_hierarchy = 'created_at'
    
    actions = ['approve_sellers', 'reject_sellers']
    
    def approve_sellers(self, request, queryset):
        queryset.update(is_approved=True)
    approve_sellers.short_description = "Aprovar vendedores selecionados"
    
    def reject_sellers(self, request, queryset):
        queryset.update(is_approved=False)
    reject_sellers.short_description = "Rejeitar vendedores selecionados"

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['subtotal']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_by', 'status', 'total_value', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['created_by__username', 'id']
    readonly_fields = ['total_value', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    
    def save_model(self, request, obj, form, change):
        if not change:  # Se é uma nova ordem
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'unit_price', 'subtotal')
    list_filter = ('order__status', 'product__category')
    search_fields = ('order__id', 'product__name')

@admin.register(SellerRegistration)
class SellerRegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'tipo_documento', 'numero_documento', 'status', 'data_criacao')
    list_filter = ('status', 'tipo_documento')
    search_fields = ('user__username', 'user__email', 'numero_documento')
    readonly_fields = ('data_criacao', 'data_atualizacao')
