from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ProdutoListCreateAPIView, ProdutoRetrieveUpdateDestroyAPIView

app_name = 'produtos'

router = DefaultRouter()

urlpatterns = [
    path('api/produtos/', ProdutoListCreateAPIView.as_view(), name='produto-list-create'),
    path('api/produtos/<int:pk>/', ProdutoRetrieveUpdateDestroyAPIView.as_view(), name='produto-detail'),
] 