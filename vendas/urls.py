from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VendaViewSet, HistoricoVendasView

app_name = 'vendas'

router = DefaultRouter()
router.register('', VendaViewSet, basename='venda')

urlpatterns = [
    path('vendas_recebidas/', VendaViewSet.as_view({'get': 'vendas_recebidas'}), name='vendas-recebidas'),
    path('minhas_vendas/', VendaViewSet.as_view({'get': 'minhas_vendas'}), name='minhas-vendas'),
    path('historico/', HistoricoVendasView.as_view(), name='historico_vendas'),
    path('', include(router.urls)),
] 