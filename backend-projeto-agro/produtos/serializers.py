from rest_framework import serializers
from .models import Produto
from vendedores.serializers import VendedorSerializer
from datetime import datetime, date

class ProdutoPublicoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = [
            'id',
            'nome',
            'descricao',
            'preco',
            'unidade_medida',
            'categoria',
            'tipo',
            'fabricante',
            'imagem',
            'permite_troca',
            'validade',
        ]

class ProdutoSerializer(serializers.ModelSerializer):
    vendedor = VendedorSerializer(read_only=True)
    vendedor_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Produto
        fields = [
            'id',
            'nome',
            'descricao',
            'preco',
            'quantidade',
            'vendedor',
            'vendedor_id',
            'categoria',
            'tipo',
            'peneira',
            'variedade',
            'lote',
            'volume_disponivel',
            'unidade_medida',
            'embalagem',
            'moeda',
            'fabricante',
            'quantidade_minima',
            'validade',
            'permite_troca',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_internal_value(self, data):
        if 'validade' in data:
            try:
                data['validade'] = datetime.strptime(data['validade'], '%Y-%m-%d').date()
            except (ValueError, TypeError):
                pass
        return super().to_internal_value(data)

    def create(self, validated_data):
        vendedor_id = validated_data.pop('vendedor_id', None)
        if vendedor_id:
            validated_data['vendedor_id'] = vendedor_id
        return super().create(validated_data)

    def update(self, instance, validated_data):
        vendedor_id = validated_data.pop('vendedor_id', None)
        if vendedor_id:
            validated_data['vendedor_id'] = vendedor_id
        return super().update(instance, validated_data) 