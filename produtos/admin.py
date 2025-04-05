from django.contrib import admin
from .models import Produto

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'get_categoria_display', 'tipo', 'variedade', 'validade', 'preco', 'permite_troca', 'vendedor')
    list_filter = ('categoria', 'tipo', 'moeda', 'validade', 'permite_troca')
    search_fields = ('nome', 'variedade', 'fabricante', 'lote')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': (
                'nome',
                'descricao',
                'vendedor',
                'preco',
                'moeda',
                'permite_troca',
            )
        }),
        ('Categorização', {
            'fields': (
                'categoria',
                'tipo',
                'variedade',
            )
        }),
        ('Detalhes do Produto', {
            'fields': (
                'fabricante',
                'lote',
                'peneira',
                'embalagem',
            )
        }),
        ('Controle de Estoque', {
            'fields': (
                'quantidade',
                'quantidade_minima',
                'volume_disponivel',
                'unidade_medida',
                'validade',
            ),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
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
