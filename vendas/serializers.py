from rest_framework import serializers
from .models import Venda
from produtos.serializers import ProdutoSerializer
from usuarios.serializers import UsuarioSerializer

class VendaSerializer(serializers.ModelSerializer):
    produto = ProdutoSerializer(read_only=True)
    comprador = UsuarioSerializer(read_only=True)
    vendedor = UsuarioSerializer(read_only=True)
    
    class Meta:
        model = Venda
        fields = [
            'id',
            'produto',
            'comprador',
            'vendedor',
            'quantidade',
            'preco_unitario',
            'preco_total',
            'data_venda',
            'status'
        ]
        read_only_fields = ['id', 'data_venda']

    def validate(self, data):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Usuário não está autenticado")

        produto = data.get('produto')
        if not produto:
            raise serializers.ValidationError("Produto é obrigatório")

        # Verifica se o usuário não está tentando comprar de si mesmo
        if request.user == produto.criado_por:
            raise serializers.ValidationError("Você não pode comprar seus próprios produtos")

        # Verifica se há estoque suficiente
        if produto.estoque < 1:
            raise serializers.ValidationError("Estoque insuficiente para este produto.")

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        produto = validated_data.get('produto')
        
        # Cria a venda com o comprador atual
        venda = Venda.objects.create(
            comprador=request.user,
            vendedor=produto.criado_por,
            **validated_data
        )
        return venda 