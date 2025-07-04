from django.contrib import admin
from django import forms
from .models import Vendedor
from usuarios.models import Usuario
from core.email_service import EmailService

class VendedorAdminForm(forms.ModelForm):
    culturas_atendidas = forms.MultipleChoiceField(
        choices=Vendedor.CULTURAS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Culturas Atendidas'
    )
    senha = forms.CharField(
        label='Senha do Usuário',
        widget=forms.PasswordInput,
        required=False,
        help_text='Defina a senha do usuário. Só será usada na criação de um novo vendedor.'
    )
    nome_fantasia = forms.CharField(
        label='Nome do Vendedor',
        required=False
    )
    hectares_atendidos = forms.IntegerField(
        label='Quantidade de Hectares atendidos',
        required=False
    )

    class Meta:
        model = Vendedor
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Preenche o campo com os valores atuais (se houver)
        if self.instance and self.instance.culturas_atendidas:
            self.initial['culturas_atendidas'] = self.instance.culturas_atendidas
        # Só mostra o campo senha se for criação
        if self.instance and self.instance.pk:
            self.fields['senha'].widget = forms.HiddenInput()

    def clean_culturas_atendidas(self):
        # Garante que sempre retorna uma lista
        return self.cleaned_data.get('culturas_atendidas', [])

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Salva como lista no JSONField
        instance.culturas_atendidas = self.cleaned_data['culturas_atendidas']
        # Se for criação, cria o usuário e define a senha
        usuario = instance.usuario
        if not instance.pk:
            senha = self.cleaned_data.get('senha')
            if senha:
                usuario.set_password(senha)
                usuario.save()
        # Sincroniza dados do vendedor para o usuário
        usuario.telefone = instance.telefone
        usuario.endereco = instance.endereco
        usuario.cidade = instance.cidade
        usuario.estado = instance.estado
        usuario.cep = instance.cep
        usuario.save()
        if commit:
            instance.save()
        return instance

@admin.register(Vendedor)
class VendedorAdmin(admin.ModelAdmin):
    form = VendedorAdminForm
    list_display = ['usuario', 'nome_fantasia', 'telefone', 'cidade', 'estado', 'culturas_descricao']
    search_fields = ['usuario__username', 'nome_fantasia', 'telefone']
    list_filter = ['estado', 'cidade']
    readonly_fields = ('data_criacao', 'updated_at')
    fieldsets = (
        ('Informações do Usuário', {
            'fields': ('usuario', 'senha')
        }),
        ('Informações do Vendedor', {
            'fields': (
                'nome_fantasia',
            )
        }),
        ('Informações de Contato', {
            'fields': (
                'telefone',
                'endereco',
                'cidade',
                'estado',
                'cep'
            )
        }),
        ('Culturas Atendidas', {
            'fields': ('culturas_atendidas',)
        }),
        ('Documentos', {
            'fields': (
                'rg',
                'rg_verso',
                'cnh',
                'cnh_verso',
                'hectares_atendidos'
            )
        }),
        ('Informações de Sistema', {
            'fields': ('data_criacao', 'updated_at'),
            'classes': ('collapse',)
        })
    )

    def culturas_descricao(self, obj):
        if not obj.culturas_atendidas:
            return ""
        # Dicionário para traduzir as chaves em descrições
        descricoes = dict(obj.CULTURAS_CHOICES)
        return ', '.join([descricoes.get(c, c) for c in obj.culturas_atendidas])
    culturas_descricao.short_description = 'Culturas Atendidas'

    def get_nome_usuario(self, obj):
        return obj.usuario.nome if obj.usuario.nome else obj.usuario.email
    get_nome_usuario.short_description = 'Nome do Usuário'
    get_nome_usuario.admin_order_field = 'usuario__nome'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if not change:  # Se for criação
            EmailService.send_welcome_email(obj.usuario)
        elif obj.status_aprovacao == 'APROVADO':
            EmailService.send_order_confirmation(obj)
        elif obj.status_aprovacao == 'RECUSADO':
            EmailService.send_vendedor_reprovado(obj)
