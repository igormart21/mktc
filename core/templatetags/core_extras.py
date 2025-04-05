from django import template

register = template.Library()

@register.filter
def starts_with(value, arg):
    return value.startswith(arg) 