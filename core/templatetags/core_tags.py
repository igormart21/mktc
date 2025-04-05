from django import template
from vendedor.models import Vendedor

register = template.Library()

@register.filter
def has_seller(user):
    return hasattr(user, 'seller')

@register.filter
def is_vendedor(user):
    if not user.is_authenticated:
        return False
    return hasattr(user, 'vendedor') 