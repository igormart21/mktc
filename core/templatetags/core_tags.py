from django import template

register = template.Library()

@register.filter
def has_seller(user):
    return hasattr(user, 'seller') 