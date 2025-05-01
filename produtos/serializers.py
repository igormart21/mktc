from rest_framework import serializers
from .models import Produto

class ProdutoSerializer(serializers.ModelSerializer):
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
            'data_criacao',
            'updated_at'
        ]
        read_only_fields = ['data_criacao', 'updated_at']

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data) 