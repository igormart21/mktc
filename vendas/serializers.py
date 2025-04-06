from rest_framework import serializers
from .models import Venda
from produtos.serializers import ProdutoSerializer
from usuarios.serializers import UsuarioSerializer

class VendaSerializer(serializers.ModelSerializer):
    produto = ProdutoSerializer(read_only=True)
    vendedor = UsuarioSerializer(read_only=True)
    comprador = UsuarioSerializer(read_only=True)
    
    class Meta:
        model = Venda
        fields = [
            'id',
            'produto',
            'vendedor',
            'comprador',
            'quantidade',
            'preco_unitario',
            'preco_total',
            'status',
            'observacoes',
            'data_criacao',
            'data_venda',
            'estoque_atualizado'
        ]
        read_only_fields = ['id', 'data_criacao', 'data_venda', 'estoque_atualizado']

    def validate(self, data):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Usuário não está autenticado")

        produto = data.get('produto')
        if not produto:
            raise serializers.ValidationError("Produto é obrigatório")

        # Verifica se há estoque suficiente
        if produto.quantidade < data.get('quantidade', 1):
            raise serializers.ValidationError("Estoque insuficiente para este produto.")

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        produto = validated_data.get('produto')
        
        # Calcula preço unitário e total
        if not validated_data.get('preco_unitario'):
            validated_data['preco_unitario'] = produto.preco
        
        if not validated_data.get('preco_total'):
            validated_data['preco_total'] = validated_data['quantidade'] * validated_data['preco_unitario']
        
        # Cria a venda com o vendedor atual
        venda = Venda.objects.create(
            vendedor=request.user,
            **validated_data
        )
        return venda 