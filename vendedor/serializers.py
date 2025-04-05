from rest_framework import serializers
from .models import Vendedor

class VendedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendedor
        fields = [
            'id',
            'usuario',
            'cnpj',
            'razao_social',
            'nome_fantasia',
            'inscricao_estadual',
            'telefone',
            'endereco',
            'cidade',
            'estado',
            'cep',
            'hectares_atendidos',
            'rg',
            'cnh',
            # Campos do Jogo
            'nivel',
            'pontos_experiencia',
            'moedas',
            'conquistas',
            'itens_inventario',
            'ultima_missao',
            'missoes_completadas',
            'ranking',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at'] 