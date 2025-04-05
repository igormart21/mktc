from rest_framework import serializers
from .models import Vendedor
from usuarios.serializers import UsuarioSerializer, UsuarioCreateSerializer

class VendedorSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    
    class Meta:
        model = Vendedor
        fields = [
            'id',
            'usuario',
            'cnpj',
            'razao_social',
            'nome_fantasia',
            'inscricao_estadual',
            'inscricao_municipal',
            'status_aprovacao'
        ]
        read_only_fields = ['id']

class VendedorCreateSerializer(serializers.ModelSerializer):
    usuario = UsuarioCreateSerializer()
    
    class Meta:
        model = Vendedor
        fields = [
            'usuario',
            'cnpj',
            'razao_social',
            'nome_fantasia',
            'inscricao_estadual',
            'inscricao_municipal'
        ]

    def create(self, validated_data):
        usuario_data = validated_data.pop('usuario')
        usuario = UsuarioCreateSerializer().create(usuario_data)
        vendedor = Vendedor.objects.create(usuario=usuario, **validated_data)
        return vendedor 