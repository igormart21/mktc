from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    ProdutoListCreateAPIView,
    ProdutoRetrieveUpdateDestroyAPIView,
    ListaProdutosAPIView,
    toggle_product_status
)
from django.views.generic.base import RedirectView
from django.urls import reverse_lazy

app_name = 'produtos'

router = DefaultRouter()

urlpatterns = [
    path('produtos/', ProdutoListCreateAPIView.as_view(), name='produto-list-create'),
    path('produtos/<int:pk>/', ProdutoRetrieveUpdateDestroyAPIView.as_view(), name='produto-detail'),
    path('produtos/<int:pk>/toggle_status/', toggle_product_status, name='toggle_product_status'),
    path('lista/', ListaProdutosAPIView.as_view(), name='lista_produtos'),
    path('detalhe/<int:produto_id>/', 
         RedirectView.as_view(pattern_name='core:produto_detalhe'), 
         name='produto-detalhe-redirect'),
] 