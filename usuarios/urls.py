from django.urls import path
from .views import PerfilUsuarioAPIView, LogoutAPIView

urlpatterns = [
    path('perfil/', PerfilUsuarioAPIView.as_view(), name='perfil-usuario'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
] 