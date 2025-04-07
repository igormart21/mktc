from rest_framework import permissions
from vendedor.models import Vendedor

class IsSuperAdmin(permissions.BasePermission):
    """
    Permite acesso apenas a superadmins
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser

class IsVendedorAprovado(permissions.BasePermission):
    """
    Permite acesso apenas a vendedores aprovados
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        try:
            vendedor = Vendedor.objects.get(usuario=request.user)
            return vendedor.data_aprovacao is not None
        except Vendedor.DoesNotExist:
            return False

class IsAuthenticatedUser(permissions.BasePermission):
    """
    Permite acesso apenas a usuários autenticados
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

class IsVendedorAprovadoOrSuperAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated and 
                (request.user.is_superuser or 
                 (hasattr(request.user, 'vendedor') and request.user.vendedor.data_aprovacao is not None)))

class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or obj == request.user 