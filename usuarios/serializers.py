from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Usuario
from vendedor.models import Vendedor

Usuario = get_user_model()

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            'id',
            'email',
            'nome',
            'cpf',
            'telefone',
            'cep',
            'rua',
            'numero',
            'complemento',
            'hectares_atendidos',
            'tipo_documento',
            'numero_documento',
            'documento',
            'uf_documento',
            'orgao_emissor',
            'is_active',
            'is_staff',
            'is_superuser',
            'aprovado',
            'date_joined'
        ]
        read_only_fields = ['id', 'date_joined']

class UsuarioCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Usuario
        fields = (
            'email',
            'nome',
            'cpf',
            'telefone',
            'cep',
            'rua',
            'numero',
            'complemento',
            'hectares_atendidos',
            'tipo_documento',
            'numero_documento',
            'documento',
            'uf_documento',
            'orgao_emissor',
            'password',
            'password2'
        )

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "As senhas não conferem"})

        # Validações de documento
        tipo_documento = attrs.get('tipo_documento')
        if tipo_documento == 'RG':
            if not attrs.get('uf_documento'):
                raise serializers.ValidationError({"uf_documento": "UF do documento é obrigatória para RG"})
            if not attrs.get('orgao_emissor'):
                raise serializers.ValidationError({"orgao_emissor": "Órgão emissor é obrigatório para RG"})
        elif tipo_documento == 'CNH':
            if attrs.get('uf_documento'):
                raise serializers.ValidationError({"uf_documento": "UF do documento não deve ser preenchida para CNH"})
            if attrs.get('orgao_emissor'):
                raise serializers.ValidationError({"orgao_emissor": "Órgão emissor não deve ser preenchido para CNH"})

        if not attrs.get('documento'):
            raise serializers.ValidationError({"documento": "Documento é obrigatório"})
        if not attrs.get('numero_documento'):
            raise serializers.ValidationError({"numero_documento": "Número do documento é obrigatório"})

        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        user = Usuario.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UsuarioUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = (
            'email',
            'nome',
            'cpf',
            'telefone',
            'cep',
            'rua',
            'numero',
            'complemento',
            'hectares_atendidos',
            'tipo_documento',
            'numero_documento',
            'documento',
            'uf_documento',
            'orgao_emissor',
            'is_active',
            'is_staff',
            'is_superuser'
        )

class PerfilUsuarioSerializer(serializers.ModelSerializer):
    tipo_usuario = serializers.SerializerMethodField()
    status_aprovacao = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'tipo_usuario', 'status_aprovacao']

    def get_tipo_usuario(self, obj):
        if obj.is_superuser:
            return 'admin'
        try:
            if hasattr(obj, 'vendedor'):
                return 'vendedor'
        except Vendedor.DoesNotExist:
            pass
        return 'cliente'

    def get_status_aprovacao(self, obj):
        try:
            if hasattr(obj, 'vendedor'):
                return True
        except Vendedor.DoesNotExist:
            pass
        return False 