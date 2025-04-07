from django import forms
from .models import Pedido

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = [
            'quantidade',
            'nome_propriedade',
            'cnpj',
            'hectares',
            'cultivo_principal',
            'estado',
            'cidade',
            'endereco',
            'cep',
            'referencia',
            'observacoes'
        ]
        widgets = {
            'quantidade': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'nome_propriedade': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'cnpj': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'hectares': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1'
            }),
            'cultivo_principal': forms.Select(attrs={
                'class': 'form-control'
            }),
            'estado': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '2'
            }),
            'cidade': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'endereco': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'cep': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'referencia': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': '3'
            })
        } 