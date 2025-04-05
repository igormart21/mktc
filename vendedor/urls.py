from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'vendedor'

router = DefaultRouter()
router.register(r'vendedores', views.VendedorViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 