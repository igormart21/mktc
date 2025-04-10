from django.contrib import admin
from .models import Vendedor

@admin.register(Vendedor)
class VendedorAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'nome_fantasia', 'telefone', 'cidade', 'estado']
    search_fields = ['usuario__username', 'nome_fantasia', 'telefone']
    list_filter = ['estado', 'cidade']
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Informações do Usuário', {
            'fields': ('usuario',)
        }),
        ('Informações da Empresa', {
            'fields': (
                'nome_fantasia',
            )
        }),
        ('Informações de Contato', {
            'fields': (
                'telefone',
                'endereco',
                'cidade',
                'estado',
                'cep'
            )
        }),
        ('Documentos', {
            'fields': (
                'rg',
                'cnh',
                'hectares_atendidos'
            )
        }),
        ('Informações de Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def get_nome_usuario(self, obj):
        return obj.usuario.nome if obj.usuario.nome else obj.usuario.email
    get_nome_usuario.short_description = 'Nome do Usuário'
    get_nome_usuario.admin_order_field = 'usuario__nome'
