from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import Product, Order, OrderItem, SellerRegistration, SolicitacaoProduto
from usuarios.models import Usuario
from vendedor.models import Vendedor
from produtos.models import Produto
from django.utils.translation import gettext_lazy as _

def validar_cpf(cpf):
    # Remove caracteres não numéricos
    cpf = ''.join(filter(str.isdigit, cpf))
    
    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        return False
    
    # Calcula o primeiro dígito verificador
    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)
    resto = 11 - (soma % 11)
    if resto > 9:
        resto = 0
    if resto != int(cpf[9]):
        return False
    
    # Calcula o segundo dígito verificador
    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)
    resto = 11 - (soma % 11)
    if resto > 9:
        resto = 0
    if resto != int(cpf[10]):
        return False
    
    return True

class ProductForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = [
            'nome', 'descricao', 'preco', 'volume_disponivel', 'unidade_medida',
            'categoria', 'tipo', 'fabricante', 'lote',
            'validade', 'quantidade_minima', 'embalagem',
            'peneira', 'variedade', 'moeda', 'permite_troca'
        ]
        widgets = {
            'descricao': forms.Textarea(attrs={'rows': 4}),
            'validade': forms.DateInput(attrs={'type': 'date'}),
        }

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status', 'notes']

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']

OrderItemFormSet = forms.inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    extra=1,
    can_delete=True
)

class SellerRegistrationForm(UserCreationForm):
    nome = forms.CharField(
        max_length=100, 
        label='Nome', 
        required=False
    )
    sobrenome = forms.CharField(
        max_length=100, 
        label='Sobrenome', 
        required=False
    )
    email = forms.EmailField(
        label='E-mail', 
        required=False
    )
    cpf = forms.CharField(
        max_length=11,
        label='CPF',
        required=False
    )
    telefone = forms.CharField(
        max_length=20, 
        label='Telefone', 
        required=False
    )
    tipo_documento = forms.ChoiceField(
        choices=[('RG', 'RG'), ('CNH', 'CNH')],
        label='Tipo de Documento',
        required=False
    )
    numero_documento = forms.CharField(
        max_length=20, 
        label='Número do Documento', 
        required=False
    )
    arquivo_documento = forms.FileField(
        label='Arquivo do Documento', 
        required=False
    )
    cep = forms.CharField(
        max_length=9, 
        label='CEP', 
        required=False
    )
    endereco = forms.CharField(
        max_length=255, 
        label='Endereço', 
        required=False
    )
    cidade = forms.CharField(
        max_length=100, 
        label='Cidade', 
        required=False
    )
    estado = forms.CharField(
        max_length=2, 
        label='Estado', 
        required=False
    )
    hectares_atendidos = forms.IntegerField(
        label='Hectares Atendidos',
        required=False
    )

    class Meta:
        model = Usuario
        fields = [
            'nome', 'sobrenome', 'email', 'cpf', 'password1', 'password2',
            'telefone', 'tipo_documento', 'numero_documento', 'arquivo_documento',
            'cep', 'endereco', 'cidade', 'estado', 'hectares_atendidos'
        ]

    def clean_email(self):
        return self.cleaned_data.get('email')

    def clean_cpf(self):
        return self.cleaned_data.get('cpf')

    def clean_estado(self):
        estado = self.cleaned_data.get('estado')
        return estado.upper() if estado else estado

class LoginForm(forms.Form):
    username = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Senha')

class SolicitacaoProdutoForm(forms.ModelForm):
    class Meta:
        model = SolicitacaoProduto
        fields = ['nome_produto', 'descricao', 'categoria_sugerida', 'quantidade', 'unidade_medida']
        labels = {
            'nome_produto': _('Nome do Produto'),
            'descricao': _('Descrição'),
            'categoria_sugerida': _('Categoria Sugerida'),
            'quantidade': _('Quantidade'),
            'unidade_medida': _('Unidade de Medida'),
        }

class SellerProfileForm(forms.ModelForm):
    class Meta:
        model = Vendedor
        fields = [
            'nome_fantasia',
            'inscricao_estadual',
            'telefone',
            'endereco',
            'cidade',
            'estado',
            'cep',
            'hectares_atendidos',
            'rg',
            'cnh'
        ]
        widgets = {
            'telefone': forms.TextInput(attrs={'placeholder': '(00) 00000-0000'}),
            'cep': forms.TextInput(attrs={'placeholder': '00000-000'}),
        }

class AdminProfileForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'telefone', 'cep', 'rua', 'numero', 'complemento']
        widgets = {
            'telefone': forms.TextInput(attrs={'placeholder': '(00) 00000-0000'}),
            'cep': forms.TextInput(attrs={'placeholder': '00000-000'}),
        } 