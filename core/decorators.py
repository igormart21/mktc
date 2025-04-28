from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from vendedor.models import Vendedor

def superuser_required(function=None):
    actual_decorator = user_passes_test(lambda u: u.is_superuser)
    if function:
        return actual_decorator(function)
    return actual_decorator

def is_seller(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        try:
            vendedor = Vendedor.objects.get(usuario=request.user)
            return function(request, *args, **kwargs)
        except Vendedor.DoesNotExist:
            messages.error(request, 'Você precisa ser um vendedor para acessar esta página.')
            return redirect('core:home')
    return wrap 