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
            'nome', 'categoria', 'preco', 'moeda', 'volume_disponivel', 'unidade_medida',
            'tipo', 'embalagem', 'fabricante', 'lote', 'validade', 'quantidade_minima',
            'peneira', 'variedade', 'imagem', 'descricao', 'permite_troca', 'ativo'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'categoria': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'preco': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'required': True}),
            'moeda': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'volume_disponivel': forms.NumberInput(attrs={'class': 'form-control', 'required': True}),
            'unidade_medida': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'tipo': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'embalagem': forms.Select(attrs={'class': 'form-select'}),
            'fabricante': forms.TextInput(attrs={'class': 'form-control'}),
            'lote': forms.TextInput(attrs={'class': 'form-control'}),
            'validade': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'quantidade_minima': forms.NumberInput(attrs={'class': 'form-control'}),
            'peneira': forms.TextInput(attrs={'class': 'form-control'}),
            'variedade': forms.TextInput(attrs={'class': 'form-control'}),
            'imagem': forms.FileInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'permite_troca': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input', 'checked': True})
        }
        labels = {
            'nome': 'Nome do Produto*',
            'categoria': 'Categoria*',
            'preco': 'Preço*',
            'moeda': 'Moeda*',
            'volume_disponivel': 'Volume Disponível*',
            'unidade_medida': 'Unidade de Medida*',
            'tipo': 'Tipo do Produto*',
            'embalagem': 'Embalagem',
            'fabricante': 'Fabricante',
            'lote': 'Lote',
            'validade': 'Data de Validade',
            'quantidade_minima': 'Quantidade Mínima',
            'peneira': 'Peneira da Semente',
            'variedade': 'Variedade da Semente',
            'imagem': 'Imagem do Produto',
            'descricao': 'Descrição do Produto',
            'permite_troca': 'Permitir Troca',
            'ativo': 'Produto Ativo'
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
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    sobrenome = forms.CharField(
        max_length=100, 
        label='Sobrenome', 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='E-mail', 
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    cpf = forms.CharField(
        max_length=11,
        label='CPF',
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    telefone = forms.CharField(
        max_length=20, 
        label='Telefone', 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    tipo_documento = forms.ChoiceField(
        choices=[('RG', 'RG'), ('CNH', 'CNH')],
        label='Tipo de Documento',
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    arquivo_documento = forms.FileField(
        label='Arquivo do Documento', 
        required=True,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    endereco = forms.CharField(
        max_length=255, 
        label='Endereço', 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    cidade = forms.CharField(
        max_length=100, 
        label='Cidade', 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    estado = forms.CharField(
        max_length=2, 
        label='Estado', 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    cep = forms.CharField(
        max_length=9, 
        label='CEP', 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    hectares_atendidos = forms.IntegerField(
        label='Hectares Atendidos',
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Usuario
        fields = [
            'nome', 'sobrenome', 'email', 'cpf', 'password1', 'password2',
            'telefone', 'tipo_documento', 'arquivo_documento',
            'endereco', 'cidade', 'estado', 'cep', 'hectares_atendidos'
        ]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email já está em uso.')
        return email

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if Usuario.objects.filter(cpf=cpf).exists():
            raise forms.ValidationError('Este CPF já está cadastrado.')
        return cpf

    def clean_estado(self):
        estado = self.cleaned_data.get('estado')
        return estado.upper() if estado else estado

class LoginForm(forms.Form):
    username = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Senha')

class SolicitacaoProdutoForm(forms.ModelForm):
    class Meta:
        model = SolicitacaoProduto
        fields = [
            'nome_produto', 
            'categoria_sugerida', 
            'descricao', 
            'quantidade', 
            'unidade_medida',
            'fabricante',
            'tipo_produto',
            'lote',
            'peneira',
            'variedade',
            'embalagem',
            'data_validade',
            'observacoes'
        ]
        labels = {
            'nome_produto': 'Nome do Produto',
            'categoria_sugerida': 'Categoria Sugerida',
            'descricao': 'Descrição',
            'quantidade': 'Volume',
            'unidade_medida': 'Unidade',
            'fabricante': 'Fabricante',
            'tipo_produto': 'Tipo de Produto',
            'lote': 'Lote',
            'peneira': 'Peneira',
            'variedade': 'Variedade',
            'embalagem': 'Embalagem',
            'data_validade': 'Data de Validade',
            'observacoes': 'Observações'
        }
        widgets = {
            'nome_produto': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Semente de Soja, Fertilizante NPK',
                'required': 'required'
            }),
            'categoria_sugerida': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Sementes, Fertilizantes, Defensivos',
                'required': 'required'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descreva as características específicas do produto que você precisa',
                'required': 'required'
            }),
            'quantidade': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0.01',
                'step': '0.01',
                'placeholder': 'Digite o volume',
                'required': 'required',
                'value': '1.00'  # Valor padrão
            }),
            'unidade_medida': forms.Select(attrs={
                'class': 'form-select',
                'required': 'required'
            }),
            'fabricante': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Não especificado'
            }),
            'tipo_produto': forms.Select(attrs={
                'class': 'form-select'
            }),
            'lote': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'peneira': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'variedade': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'embalagem': forms.Select(attrs={
                'class': 'form-select'
            }),
            'data_validade': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tornar campos obrigatórios
        self.fields['nome_produto'].required = True
        self.fields['categoria_sugerida'].required = True
        self.fields['quantidade'].required = True
        self.fields['unidade_medida'].required = True

class SellerProfileForm(forms.ModelForm):
    class Meta:
        model = Vendedor
        fields = [
            'nome_fantasia',
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