from django.contrib import admin
from .models import Venda

@admin.register(Venda)
class VendaAdmin(admin.ModelAdmin):
    list_display = ['produto', 'comprador', 'vendedor', 'status', 'data_criacao']
    list_filter = ['status', 'data_criacao', 'vendedor']
    search_fields = ['produto__nome', 'comprador__nome', 'vendedor__nome']
    readonly_fields = ['data_criacao', 'estoque_atualizado']
    ordering = ['-data_criacao']
