from rest_framework import serializers
from .models import Produto
from vendedor.serializers import VendedorSerializer

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