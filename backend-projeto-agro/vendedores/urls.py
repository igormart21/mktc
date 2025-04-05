from django.urls import path
from .views import (
    VendedorListCreateAPIView,
    VendedorRetrieveUpdateDestroyAPIView
)

urlpatterns = [
    path('', VendedorListCreateAPIView.as_view(), name='vendedor-list-create'),
    path('<int:pk>/', VendedorRetrieveUpdateDestroyAPIView.as_view(), name='vendedor-detail'),
] 