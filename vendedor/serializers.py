from rest_framework import serializers
from .models import Vendedor

class VendedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendedor
        fields = [
            'id',
            'usuario',
            'nome_fantasia',
            'telefone',
            'endereco',
            'cidade',
            'estado',
            'cep',
            'hectares_atendidos',
            'rg',
            'cnh',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at'] 