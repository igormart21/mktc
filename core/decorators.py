from django.contrib.auth.decorators import user_passes_test

def superuser_required(function=None):
    actual_decorator = user_passes_test(lambda u: u.is_superuser)
    if function:
        return actual_decorator(function)
    return actual_decorator 