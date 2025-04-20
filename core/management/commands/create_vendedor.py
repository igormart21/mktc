from django.contrib.auth import get_user_model
from vendedor.models import Vendedor
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Cria um usuário e um vendedor associado a ele'

    def handle(self, *args, **options):
        # Cria o usuário
        Usuario = get_user_model()
        usuario = Usuario.objects.create_user(
            email='arley.silva@example.com',
            password='senha123',
            nome='arley',
            sobrenome='silva',
            is_staff=True
        )

        # Cria o vendedor associado ao usuário
        vendedor = Vendedor.objects.create(
            usuario=usuario,
            nome_fantasia='Arley Silva',
            status_aprovacao='APROVADO'
        )

        self.stdout.write(self.style.SUCCESS('Usuário e vendedor criados com sucesso!')) 