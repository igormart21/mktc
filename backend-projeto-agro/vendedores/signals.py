from django.db.models.signals import post_save
from django.dispatch import receiver
from usuarios.models import Usuario
from .models import Vendedor

@receiver(post_save, sender=Usuario)
def criar_vendedor(sender, instance, created, **kwargs):
    """
    Cria automaticamente um vendedor quando um novo usuário é criado
    e não é um staff (admin)
    """
    if created and not instance.is_staff:
        Vendedor.objects.create(
            usuario=instance,
            status_aprovacao='PENDENTE'
        ) 