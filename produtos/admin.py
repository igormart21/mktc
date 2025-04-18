from django.contrib import admin
from .models import Produto

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'categoria', 'preco', 'volume_disponivel', 'ativo']
    list_filter = ['categoria', 'tipo', 'ativo']
    search_fields = ['nome', 'descricao']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'categoria', 'descricao')
        }),
        ('Preço e Volume', {
            'fields': ('preco', 'moeda', 'volume_disponivel', 'unidade_medida')
        }),
        ('Classificação', {
            'fields': ('tipo', 'embalagem')
        }),
        ('Informações Adicionais', {
            'fields': ('fabricante', 'lote', 'validade', 'quantidade_minima')
        }),
        ('Informações da Semente', {
            'fields': ('peneira', 'variedade')
        }),
        ('Imagem', {
            'fields': ('imagem',)
        }),
        ('Status', {
            'fields': ('ativo',)
        }),
        ('Metadados', {
            'fields': ('vendedor', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def save_model(self, request, obj, form, change):
        if not change:  # Se é uma criação (não uma edição)
            if not obj.vendedor:  # Se o vendedor não foi definido
                if hasattr(request.user, 'vendedor'):  # Se o usuário é um vendedor
                    obj.vendedor = request.user.vendedor
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        # Apenas superadmins podem adicionar produtos
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        # Apenas superadmins podem editar produtos
        return request.user.is_superuser
