from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def superuser_required(function=None):
    actual_decorator = user_passes_test(lambda u: u.is_superuser)
    if function:
        return actual_decorator(function)
    return actual_decorator

def is_seller(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if hasattr(request.user, 'vendedor'):
            return function(request, *args, **kwargs)
        else:
            messages.error(request, 'Você precisa ser um vendedor para acessar esta página.')
            return redirect('core:home')
    return wrap 