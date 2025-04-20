from django.contrib.auth.backends import ModelBackend
from usuarios.models import Usuario

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, email=None, password=None, **kwargs):
        if email is None:
            email = username
        try:
            user = Usuario.objects.get(email=email)
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except Usuario.DoesNotExist:
            return None 