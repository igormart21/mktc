from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import Product, Order, OrderItem, SellerRegistration, SolicitacaoProduto
from usuarios.models import Usuario
from django.utils.translation import gettext_lazy as _

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
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