from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django import forms
from .models import Usuario

class UsuarioAdminForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = '__all__'
        widgets = {
            'uf_documento': forms.Select(attrs={'class': 'uf-documento-field'}),
        }

    class Media:
        js = ('js/cep.js', 'js/documento.js',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['uf_documento'].required = self.instance.tipo_documento == 'RG'

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    form = UsuarioAdminForm
    list_display = ('nome', 'email', 'cpf', 'telefone', 'tipo_documento', 'is_active', 'is_staff', 'is_superuser', 'aprovado')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'aprovado', 'tipo_documento')
    search_fields = ('nome', 'email', 'cpf', 'numero_documento')
    ordering = ('nome',)
    readonly_fields = ('date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informações Pessoais', {'fields': ('nome', 'cpf', 'telefone', 'cep', 'rua', 'numero', 'complemento', 'hectares_atendidos')}),
        ('Documentos', {'fields': ('tipo_documento', 'numero_documento', 'documento', 'uf_documento')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'aprovado', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nome', 'cpf', 'telefone', 'cep', 'rua', 'numero', 'complemento', 'hectares_atendidos', 
                      'tipo_documento', 'numero_documento', 'documento', 'uf_documento',
                      'password1', 'password2', 'is_active', 'is_staff', 'is_superuser', 'aprovado'),
        }),
    )

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'is_active' in form.base_fields:
            form.base_fields['is_active'].label = 'Ativo'
        if 'is_staff' in form.base_fields:
            form.base_fields['is_staff'].label = 'Acesso ao Painel'
        if 'is_superuser' in form.base_fields:
            form.base_fields['is_superuser'].label = 'Superusuário'
        if 'aprovado' in form.base_fields:
            form.base_fields['aprovado'].label = 'Aprovado'
        return form

    class Media:
        js = ('js/cep.js', 'js/documento.js',)
        css = {
            'all': ('css/admin.css',)
        }
