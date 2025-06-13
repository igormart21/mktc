from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import SellerRegistration, SolicitacaoProduto, Pedido, ItemPedido
from usuarios.models import Usuario
from vendedor.models import Vendedor
from produtos.models import Produto
from django.utils.translation import gettext_lazy as _
from django.conf import settings

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
            'peneira', 'variedade', 'tipo_da_semente', 'tratamento_da_semente', 'imagem', 'descricao', 'ativo'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'categoria': forms.Select(attrs={'class': 'form-select', 'required': True}),
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
            'tipo_da_semente': forms.Select(attrs={'class': 'form-select'}),
            'tratamento_da_semente': forms.TextInput(attrs={'class': 'form-control'}),
            'imagem': forms.FileInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
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
            'tipo_da_semente': 'Tipo da Semente',
            'tratamento_da_semente': 'Tratamento da Semente',
            'imagem': 'Imagem do Produto',
            'descricao': 'Descrição do Produto',
            'ativo': 'Produto Ativo'
        }

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = [
            'nome_propriedade',
            'cnpj',
            'hectares',
            'cultivo_principal',
            'estado',
            'cidade',
            'endereco',
            'cep',
            'referencia',
            'observacoes',
            'status',
            'tipo_venda',
            'documento_ir',
            'inscricao_estadual',
            'documento_matricula',
            'is_arrendatario',
            'documento_arrendamento',
            'total',
        ]

class SellerRegistrationForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['email', 'nome', 'sobrenome', 'cpf', 'telefone', 'cep', 'tipo_documento', 'numero_documento']
    
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
        max_length=14,
        label='CPF',
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '000.000.000-00',
            'data-mask': '000.000.000-00'
        })
    )
    telefone = forms.CharField(
        max_length=20, 
        label='Telefone', 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    endereco = forms.CharField(
        max_length=255, 
        label='Endereço', 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    numero = forms.CharField(
        max_length=10,
        label='Número',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    bairro = forms.CharField(
        max_length=100, 
        label='Bairro', 
        required=False,
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
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '00000-000',
            'pattern': '[0-9]{5}-[0-9]{3}',
            'title': 'Digite o CEP no formato 00000-000'
        })
    )
    tipo_documento = forms.ChoiceField(
        choices=Usuario.TIPO_DOCUMENTO_CHOICES,
        label='Tipo de Documento',
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    numero_documento = forms.CharField(
        max_length=20,
        label='Número do Documento',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    frente_documento = forms.FileField(
        label='Frente do Documento',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    verso_documento = forms.FileField(
        label='Verso do Documento',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    hectares_atendidos = forms.IntegerField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Quantidade de hectares atendidos'
        })
    )
    culturas_atendidas = forms.MultipleChoiceField(
        choices=Vendedor.CULTURAS_CHOICES,
        label='Culturas Atendidas',
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'})
    )
    
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if not validar_cpf(cpf):
            raise ValidationError('CPF inválido')
        return cpf
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_documento = cleaned_data.get('tipo_documento')
        frente_documento = cleaned_data.get('frente_documento')
        verso_documento = cleaned_data.get('verso_documento')
        
        if tipo_documento == 'RG':
            if not frente_documento:
                self.add_error('frente_documento', 'A frente do RG é obrigatória.')
            if not verso_documento:
                self.add_error('verso_documento', 'O verso do RG é obrigatório.')
        elif tipo_documento == 'CNH':
            if not frente_documento:
                self.add_error('frente_documento', 'A frente da CNH é obrigatória.')
            if not verso_documento:
                self.add_error('verso_documento', 'O verso da CNH é obrigatório.')
            
        return cleaned_data

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
            'nome_produto': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria_sugerida': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'unidade_medida': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: kg, l, un, cx, etc.'}),
            'fabricante': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_produto': forms.Select(attrs={'class': 'form-select'}),
            'lote': forms.TextInput(attrs={'class': 'form-control'}),
            'peneira': forms.TextInput(attrs={'class': 'form-control'}),
            'variedade': forms.TextInput(attrs={'class': 'form-control'}),
            'embalagem': forms.Select(attrs={'class': 'form-select'}),
            'data_validade': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
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
            'numero',
            'bairro',
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

class VendaPrazoForm(forms.Form):
    documento_ir = forms.FileField(
        label='Imposto de Renda do Produtor',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    inscricao_estadual = forms.FileField(
        label='Inscrição Estadual',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    documento_matricula = forms.FileField(
        label='Matrícula',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    is_arrendatario = forms.BooleanField(
        label='Você é arrendatário?',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    documento_arrendamento = forms.FileField(
        label='Documento de Arrendamento',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        is_arrendatario = cleaned_data.get('is_arrendatario')
        documento_arrendamento = cleaned_data.get('documento_arrendamento')
        inscricao_estadual = cleaned_data.get('inscricao_estadual')
        documento_matricula = cleaned_data.get('documento_matricula')

        if is_arrendatario and not documento_arrendamento:
            self.add_error('documento_arrendamento', 'Este campo é obrigatório para arrendatários.')

        if not inscricao_estadual:
            self.add_error('inscricao_estadual', 'Este campo é obrigatório para vendas a prazo.')

        if not documento_matricula:
            self.add_error('documento_matricula', 'Este campo é obrigatório para vendas a prazo.')

        return cleaned_data 