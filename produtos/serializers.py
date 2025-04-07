from rest_framework import serializers
from .models import Produto
from vendedor.serializers import VendedorSerializer

class ProdutoSerializer(serializers.ModelSerializer):
    vendedor = VendedorSerializer(read_only=True)
    vendedor_id = serializers.IntegerField(write_only=True, required=False)
    
    categoria = serializers.CharField(required=True)
    
    moeda = serializers.ChoiceField(
        choices=Produto.MOEDA_CHOICES,
        required=True,
        error_messages={
            'invalid_choice': 'Faça uma escolha válida para a moeda.'
        }
    )
    
    tipo = serializers.ChoiceField(
        choices=Produto.TIPO_CHOICES,
        required=True,
        error_messages={
            'required': 'Este campo é obrigatório.',
            'invalid_choice': 'Faça uma escolha válida para o tipo.'
        }
    )
    
    class Meta:
        model = Produto
        fields = [
            'id',
            'nome',
            'descricao',
            'preco',
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
            'ativo',
            'imagem',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

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