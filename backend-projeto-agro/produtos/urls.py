from django.urls import path
from .views import (
    ListaProdutosPublicosAPIView,
    ListaProdutosAPIView,
    ProdutoListCreateAPIView,
    ProdutoRetrieveUpdateDestroyAPIView
)

urlpatterns = [
    path('publicos/', ListaProdutosPublicosAPIView.as_view(), name='produtos-publicos'),
    path('', ListaProdutosAPIView.as_view(), name='produtos'),
    path('criar/', ProdutoListCreateAPIView.as_view(), name='produto-criar'),
    path('<int:pk>/', ProdutoRetrieveUpdateDestroyAPIView.as_view(), name='produto-detalhe'),
] 