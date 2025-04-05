"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView
from usuarios.views import (
    teste_autenticacao,
    area_admin,
    area_vendedor,
    area_usuario,
    CustomTokenObtainPairView
)
from produtos.views import (
    ListaProdutosAPIView,
    ProdutoListCreateAPIView,
    ProdutoRetrieveUpdateDestroyAPIView,
    ListaProdutosPublicosAPIView
)
from vendas.views import (
    ListaVendasAPIView,
    VendaListCreateAPIView,
    VendaRetrieveUpdateDestroyAPIView
)
from vendedores.views import (
    VendedorListCreateAPIView,
    VendedorRetrieveUpdateDestroyAPIView
)
from django.views.generic import RedirectView
from .views import home

urlpatterns = [
    path('', RedirectView.as_view(url='/admin/', permanent=True), name='index'),
    path('admin/', admin.site.urls),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/teste-autenticacao/', teste_autenticacao, name='teste_autenticacao'),
    path('api/area-admin/', area_admin, name='area_admin'),
    path('api/area-vendedor/', area_vendedor, name='area_vendedor'),
    path('api/area-usuario/', area_usuario, name='area_usuario'),
    path('api/produtos/', include('produtos.urls')),
    path('api/vendas/', include('vendas.urls')),
    path('api/vendedores/', include('vendedores.urls')),
    path('api/auth/', include('autenticacao.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
