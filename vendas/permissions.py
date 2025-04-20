from rest_framework import permissions
from vendedor.models import Vendedor

class IsVendedorAprovado(permissions.BasePermission):
    """
    Permite acesso apenas para vendedores aprovados.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        try:
            vendedor = Vendedor.objects.get(usuario=request.user)
            return vendedor.status_aprovacao == 'APROVADO'
        except Vendedor.DoesNotExist:
            return False

class IsComprador(permissions.BasePermission):
    """
    Permite acesso apenas para usuários que não são vendedores (apenas compradores).
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        try:
            vendedor = Vendedor.objects.get(usuario=request.user)
            return False
        except Vendedor.DoesNotExist:
            return True 