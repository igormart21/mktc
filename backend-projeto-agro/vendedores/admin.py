from django.contrib import admin
from .models import Vendedor
from django.utils.html import format_html

@admin.register(Vendedor)
class VendedorAdmin(admin.ModelAdmin):
    list_display = ('get_nome', 'status_aprovacao', 'data_aprovacao')
    list_filter = ('status_aprovacao',)
    search_fields = ('usuario__nome', 'usuario__cpf', 'usuario__numero_documento')
    readonly_fields = ('data_aprovacao', 'get_documento', 'get_tipo_documento', 'get_numero_documento')
    
    def get_nome(self, obj):
        return obj.usuario.nome
    get_nome.short_description = 'Nome'
    get_nome.admin_order_field = 'usuario__nome'
    
    def get_documento(self, obj):
        if obj.usuario.documento:
            return format_html('<a href="{}" target="_blank">Ver {}</a>', 
                             obj.usuario.documento.url, 
                             obj.usuario.tipo_documento)
        return '-'
    get_documento.short_description = 'Documento'

    def get_tipo_documento(self, obj):
        return obj.usuario.get_tipo_documento_display() if obj.usuario.tipo_documento else '-'
    get_tipo_documento.short_description = 'Tipo de Documento'

    def get_numero_documento(self, obj):
        if obj.usuario.tipo_documento == 'RG':
            return f"{obj.usuario.numero_documento} - {obj.usuario.orgao_emissor}/{obj.usuario.uf_documento}"
        return obj.usuario.numero_documento if obj.usuario.numero_documento else '-'
    get_numero_documento.short_description = 'Número do Documento'

    fieldsets = (
        ('Informações do Vendedor', {
            'fields': ('usuario', 'status_aprovacao', 'data_aprovacao')
        }),
        ('Documentos', {
            'fields': ('get_tipo_documento', 'get_numero_documento', 'get_documento'),
            'classes': ('collapse',)
        }),
        ('Observações', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
    )
