from django import template

register = template.Library()

@register.filter
def divide(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return None 

@register.filter
def format_cnpj(value):
    if not value:
        return '-'
    # Remove caracteres não numéricos
    cnpj = ''.join(filter(str.isdigit, str(value)))
    # Formata o CNPJ
    return f'{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}'

@register.filter
def format_cep(value):
    if not value:
        return '-'
    # Remove caracteres não numéricos
    cep = ''.join(filter(str.isdigit, str(value)))
    # Formata o CEP
    return f'{cep[:5]}-{cep[5:]}' 