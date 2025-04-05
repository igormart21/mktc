from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VendaViewSet, HistoricoVendasView
from . import views

app_name = 'vendas'

router = DefaultRouter()
router.register('', VendaViewSet, basename='venda')

urlpatterns = [
    path('vendas_recebidas/', VendaViewSet.as_view({'get': 'vendas_recebidas'}), name='vendas-recebidas'),
    path('minhas_vendas/', VendaViewSet.as_view({'get': 'minhas_vendas'}), name='minhas-vendas'),
    path('historico/', HistoricoVendasView.as_view(), name='historico_vendas'),
    path('meus-pedidos/', views.meus_pedidos, name='meus_pedidos'),
    path('solicitar-compra/<int:produto_id>/', views.solicitar_compra, name='solicitar_compra'),
    path('cancelar-pedido/<int:pedido_id>/', views.cancelar_pedido, name='cancelar_pedido'),
    path('', include(router.urls)),
] 