from django.contrib import admin
from .models import Vendedor

@admin.register(Vendedor)
class VendedorAdmin(admin.ModelAdmin):
    list_display = (
        'get_nome_usuario',
        'razao_social',
        'nome_fantasia',
        'cnpj',
        'telefone',
        'cidade',
        'estado',
        'created_at'
    )
    list_filter = ('estado', 'created_at')
    search_fields = (
        'usuario__email',
        'usuario__nome',
        'razao_social',
        'nome_fantasia',
        'cnpj',
        'telefone',
        'cidade'
    )
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Informações do Usuário', {
            'fields': ('usuario',)
        }),
        ('Informações da Empresa', {
            'fields': (
                'razao_social',
                'nome_fantasia',
                'cnpj',
                'inscricao_estadual'
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
        ('Informações de Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def get_nome_usuario(self, obj):
        return obj.usuario.nome if obj.usuario.nome else obj.usuario.email
    get_nome_usuario.short_description = 'Nome do Usuário'
    get_nome_usuario.admin_order_field = 'usuario__nome'
