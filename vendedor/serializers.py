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
            'rg',
            'cnh',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at'] 