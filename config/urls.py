"""
URL configuration for config project.

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
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls', namespace='core')),  # Inclui as URLs do core
    path('vendas/', include('vendas.urls')),  # Inclui as URLs do vendas
    path('vendedor/', include('vendedor.urls')),  # Inclui as URLs do vendedor
    path('produtos/', include('produtos.urls')),  # Inclui as URLs da API de produtos
    # URLs de autenticação
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Adiciona as URLs do debug toolbar apenas em desenvolvimento
if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]
    # Serve arquivos de mídia apenas em desenvolvimento
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

"""
Configuração do NGINX para servir arquivos de mídia em produção:

1. Adicione a seguinte configuração no seu arquivo de configuração do NGINX:

    location /media/ {
        alias /caminho/completo/para/seu/projeto/media/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }

2. Certifique-se de que:
   - O diretório media/ tem permissões corretas (geralmente 755)
   - O usuário do NGINX tem acesso de leitura ao diretório
   - O caminho no alias corresponde ao MEDIA_ROOT do seu projeto

3. Exemplo de configuração completa do NGINX:

    server {
        listen 80;
        server_name seu_dominio.com;

        location /static/ {
            alias /caminho/completo/para/seu/projeto/staticfiles/;
            expires 30d;
            add_header Cache-Control "public, no-transform";
        }

        location /media/ {
            alias /caminho/completo/para/seu/projeto/media/;
            expires 30d;
            add_header Cache-Control "public, no-transform";
        }

        location / {
            proxy_pass http://127.0.0.1:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
"""
