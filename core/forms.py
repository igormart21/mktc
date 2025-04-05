from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import Product, Order, OrderItem, SellerRegistration, SolicitacaoProduto
from usuarios.models import Usuario
from django.utils.translation import gettext_lazy as _

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'description', 'product_type', 'sieve', 'variety', 'lot',
            'available_volume', 'unit', 'packaging', 'currency', 'price',
            'manufacturer', 'minimum_quantity', 'expiration_date', 'allow_exchange',
            'image', 'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'expiration_date': forms.DateInput(attrs={'type': 'date'}),
            'available_volume': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
            'price': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
            'minimum_quantity': forms.NumberInput(attrs={'min': '0', 'step': '0.01'}),
        }
        labels = {
            'name': 'Nome do Produto',
            'description': 'Descrição',
            'product_type': 'Tipo de Produto',
            'sieve': 'Peneira',
            'variety': 'Variedade',
            'lot': 'Lote',
            'available_volume': 'Volume Disponível',
            'unit': 'Unidade',
            'packaging': 'Embalagem',
            'currency': 'Moeda',
            'price': 'Preço',
            'manufacturer': 'Fabricante',
            'minimum_quantity': 'Quantidade Mínima',
            'expiration_date': 'Data de Validade',
            'allow_exchange': 'Permite Troca',
            'image': 'Imagem',
            'is_active': 'Ativo'
        }

    def clean_available_volume(self):
        available_volume = self.cleaned_data.get('available_volume')
        if available_volume is None:
            raise forms.ValidationError('O volume disponível é obrigatório.')
        return available_volume

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is None:
            raise forms.ValidationError('O preço é obrigatório.')
        return price

    def clean_unit(self):
        unit = self.cleaned_data.get('unit')
        if not unit:
            raise forms.ValidationError('A unidade é obrigatória.')
        return unit

    def clean_product_type(self):
        product_type = self.cleaned_data.get('product_type')
        if not product_type:
            raise forms.ValidationError('O tipo de produto é obrigatório.')
        return product_type

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
    class Meta:
        model = Usuario
        fields = ['email', 'password1', 'password2', 'nome', 'cpf', 'telefone', 'cep', 'rua', 'numero']
        labels = {
            'email': _('Email'),
            'password1': _('Senha'),
            'password2': _('Confirmar Senha'),
            'nome': _('Nome Completo'),
            'cpf': _('CPF'),
            'telefone': _('Telefone'),
            'cep': _('CEP'),
            'rua': _('Endereço'),
            'numero': _('Número'),
        }

    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if Usuario.objects.filter(cpf=cpf).exists():
            raise ValidationError(_('Este CPF já está cadastrado.'))
        return cpf

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise ValidationError(_('Este email já está cadastrado.'))
        return email

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