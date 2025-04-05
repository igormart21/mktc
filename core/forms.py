from django import forms
from django.contrib.auth.forms import UserCreationForm
from usuarios.models import Usuario
from .models import Product, Category, Order, OrderItem, SellerRegistration, SolicitacaoProduto
from vendedor.models import Vendedor
import re

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name',
            'category',
            'product_type',
            'sieve',
            'variety',
            'lot',
            'available_volume',
            'unit',
            'packaging',
            'currency',
            'price',
            'manufacturer',
            'minimum_quantity',
            'expiration_date',
            'allow_exchange',
            'description',
            'image',
            'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'product_type': forms.Select(attrs={'class': 'form-select'}),
            'sieve': forms.TextInput(attrs={'class': 'form-control'}),
            'variety': forms.TextInput(attrs={'class': 'form-control'}),
            'lot': forms.TextInput(attrs={'class': 'form-control'}),
            'available_volume': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'packaging': forms.Select(attrs={'class': 'form-select'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
            'minimum_quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
            'expiration_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'allow_exchange': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
        labels = {
            'name': 'Nome do Produto',
            'category': 'Categoria do Produto',
            'product_type': 'Tipo do Produto',
            'sieve': 'Peneira da Semente',
            'variety': 'Variedade da Semente',
            'lot': 'Lote',
            'available_volume': 'Volume Disponível',
            'unit': 'Unidade de Medida',
            'packaging': 'Embalagem',
            'currency': 'Moeda',
            'price': 'Preço',
            'manufacturer': 'Fabricante',
            'minimum_quantity': 'Quantidade Mínima',
            'expiration_date': 'Data de Validade',
            'allow_exchange': 'Permitir Troca',
            'description': 'Descrição do Produto',
            'image': 'Imagem do Produto',
            'is_active': 'Produto Ativo'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['packaging'].choices = [('', 'Selecione uma embalagem')] + list(Product.PACKAGING_CHOICES)

    def clean(self):
        cleaned_data = super().clean()
        available_volume = cleaned_data.get('available_volume')
        minimum_quantity = cleaned_data.get('minimum_quantity')

        if available_volume is not None and available_volume < 0:
            self.add_error('available_volume', 'O volume disponível não pode ser negativo.')

        if minimum_quantity is not None and minimum_quantity < 0:
            self.add_error('minimum_quantity', 'A quantidade mínima não pode ser negativa.')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if commit:
            instance.save()
            self.save_m2m()
        
        return instance

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select'
            })
        }
        labels = {
            'status': 'Status do Pedido'
        }

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']
        widgets = {
            'product': forms.Select(attrs={
                'class': 'form-select',
                'onchange': 'updatePrice(this)'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'onchange': 'updateSubtotal(this)'
            })
        }
        labels = {
            'product': 'Produto',
            'quantity': 'Quantidade'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = Product.objects.filter(is_active=True)

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if not quantity or quantity <= 0:
            raise forms.ValidationError('A quantidade deve ser maior que zero.')
        return quantity

    def clean(self):
        cleaned_data = super().clean()
        product = cleaned_data.get('product')
        quantity = cleaned_data.get('quantity')

        if product and quantity:
            if quantity > product.available_volume:
                raise forms.ValidationError(
                    f'Quantidade insuficiente em estoque. Disponível: {product.available_volume} {product.get_unit_display()}'
                )
        
        return cleaned_data

OrderItemFormSet = forms.inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)

class SellerRegistrationForm(UserCreationForm):
    razao_social = forms.CharField(max_length=200, label='Razão Social')
    nome_fantasia = forms.CharField(max_length=200, label='Nome Fantasia', required=False)
    cnpj = forms.CharField(max_length=14, label='CNPJ', required=False)
    inscricao_estadual = forms.CharField(max_length=20, label='Inscrição Estadual', required=False)
    telefone = forms.CharField(max_length=20, label='Telefone')
    endereco = forms.CharField(max_length=200, label='Endereço')
    cidade = forms.CharField(max_length=100, label='Cidade')
    estado = forms.CharField(max_length=2, label='Estado')
    cep = forms.CharField(max_length=8, label='CEP')
    hectares_atendidos = forms.DecimalField(max_digits=10, decimal_places=2, label='Hectares Atendidos', required=False)

    class Meta:
        model = Usuario
        fields = ('email', 'nome', 'cpf', 'telefone', 'cep', 'rua', 'numero', 'hectares_atendidos', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    username = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite seu e-mail',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua senha'
        })
    )

class SolicitacaoProdutoForm(forms.ModelForm):
    class Meta:
        model = SolicitacaoProduto
        fields = ['nome_produto', 'categoria_sugerida', 'descricao', 'volume', 'unidade', 'fabricante']
        widgets = {
            'nome_produto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do produto'}),
            'categoria_sugerida': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Categoria sugerida'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descreva o produto'}),
            'volume': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Volume (opcional)'}),
            'unidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Unidade (opcional)'}),
            'fabricante': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Fabricante (opcional)'}),
        } 