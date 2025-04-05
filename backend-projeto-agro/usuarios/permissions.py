from rest_framework import permissions
from vendedores.models import Vendedor

class IsSuperAdmin(permissions.BasePermission):
    """
    Permite acesso apenas a superadmins
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser

class IsVendedorAprovado(permissions.BasePermission):
    """
    Permite acesso apenas a vendedores aprovados
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        try:
            return request.user.vendedor.status_aprovacao == 'aprovado'
        except Vendedor.DoesNotExist:
            return False

class IsAuthenticatedUser(permissions.BasePermission):
    """
    Permite acesso apenas a usuários autenticados
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

class IsVendedorAprovadoOrSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and 
                (request.user.is_superuser or 
                 (request.user.vendedor and request.user.vendedor.status_aprovacao == 'aprovado'))) 