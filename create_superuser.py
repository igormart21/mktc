import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

if not User.objects.filter(email='giovany.tecagro@gmail.com').exists():
    User.objects.create_superuser(
        email='giovany.tecagro@gmail.com',
        password='agromais@'
    )
    print('Superusuário criado com sucesso!')
else:
    print('Superusuário já existe!') 