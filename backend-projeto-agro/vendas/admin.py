from django.contrib import admin
from .models import Venda
import csv
from django.http import HttpResponse
from django.utils.encoding import smart_str

@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ['produto', 'comprador', 'vendedor', 'status', 'data_criacao']
    list_filter = ['status', 'data_criacao', 'vendedor']
    search_fields = ['produto__nome', 'comprador__nome', 'vendedor__nome']
    readonly_fields = ['data_criacao', 'estoque_atualizado']
    ordering = ['-data_criacao']
    actions = ['exportar_para_csv']

    def exportar_para_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="vendas.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID da Venda',
            'Produto',
            'Comprador',
            'Vendedor',
            'Status',
            'Data da Criação',
            'Observações'
        ])
        
        for venda in queryset:
            writer.writerow([
                smart_str(venda.id),
                smart_str(venda.produto),
                smart_str(venda.comprador),
                smart_str(venda.vendedor),
                smart_str(venda.get_status_display()),
                smart_str(venda.data_criacao),
                smart_str(venda.observacoes or '')
            ])
        
        return response
    
    exportar_para_csv.short_description = "Exportar vendas selecionadas para CSV"
