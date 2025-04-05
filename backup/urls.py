from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.seller_registration, name='register'),
    path('perfil/', views.profile, name='profile'),
    path('vendedor/registro/', views.seller_registration, name='seller_registration'),
    path('vendedor/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('superadmin/dashboard/', views.superadmin_dashboard, name='superadmin_dashboard'),
    path('produtos/', views.product_list, name='products'),
    path('produtos/criar/', views.product_create, name='product_create'),
    path('produtos/detalhe/<int:pk>/', views.product_detail, name='product_detail'),
    path('produtos/excluir/<int:pk>/', views.product_delete, name='product_delete'),
    path('superadmin/vendedores/', views.listar_vendedores, name='listar_vendedores'),
    path('superadmin/superadmins/', views.listar_superadmins, name='listar_superadmins'),
    path('superadmin/vendedores/aprovar/<int:vendedor_id>/', views.aprovar_vendedor, name='aprovar_vendedor'),
    path('superadmin/vendedores/reprovar/<int:vendedor_id>/', views.reprovar_vendedor, name='reprovar_vendedor'),
    path('superadmin/vendedores/editar/<int:seller_id>/', views.seller_edit, name='seller_edit'),
    path('superadmin/vendedores/desativar/<int:seller_id>/', views.seller_disable, name='seller_disable'),
    path('superadmin/vendedores/ativar/<int:seller_id>/', views.seller_enable, name='seller_enable'),
    path('superadmin/vendedores/excluir/<int:seller_id>/', views.seller_delete, name='seller_delete'),
    path('superadmin/vendedores/cadastrar/', views.cadastrar_vendedor, name='cadastrar_vendedor'),
    path('superadmin/aplicacoes/revisar/<int:application_id>/', views.review_application, name='review_application'),
    
    # URLs de pedidos
    path('pedidos/criar/', views.order_create, name='order_create'),
    path('pedidos/editar/<int:order_id>/', views.order_edit, name='order_edit'),
    path('pedidos/detalhe/<int:order_id>/', views.order_detail, name='order_detail'),
    path('pedidos/aprovar/<int:order_id>/', views.order_approve, name='order_approve'),
    path('pedidos/cancelar/<int:order_id>/', views.order_cancel, name='order_cancel'),

    # URLs de produtos do superadmin
    path('superadmin/produtos/', views.superadmin_products, name='superadmin_products'),
    path('superadmin/produtos/criar/', views.superadmin_product_create, name='superadmin_product_create'),
    path('superadmin/produtos/editar/<int:pk>/', views.superadmin_product_update, name='superadmin_product_update'),
    path('superadmin/produtos/excluir/<int:pk>/', views.superadmin_product_delete, name='superadmin_product_delete'),

    # URLs de produtos do vendedor
    path('vendedor/produtos/', views.seller_products, name='seller_products'),
    path('vendedor/produtos/adicionar-ao-carrinho/<int:product_id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),

    # Superadmin - Pedidos
    path('superadmin/pedidos/', views.superadmin_orders, name='superadmin_orders'),
    path('superadmin/pedidos/<int:order_id>/', views.superadmin_order_detail, name='superadmin_order_detail'),
    path('superadmin/pedidos/<int:order_id>/excluir/', views.superadmin_order_delete, name='superadmin_order_delete'),

    # URLs de Categorias
    path('categorias/', views.category_list, name='category_list'),
    path('categorias/criar/', views.category_create, name='category_create'),
    path('categorias/<int:pk>/editar/', views.category_update, name='category_update'),
    path('categorias/<int:pk>/excluir/', views.category_delete, name='category_delete'),

    # URLs de gerenciamento de vendedores
    path('vendedores/', views.listar_vendedores, name='listar_vendedores'),
    path('vendedores/<int:seller_id>/', views.seller_detail, name='seller_detail'),
    path('vendedores/<int:seller_id>/editar/', views.seller_edit, name='seller_edit'),
    path('vendedores/<int:seller_id>/desativar/', views.seller_disable, name='seller_disable'),
    path('vendedores/<int:seller_id>/ativar/', views.seller_enable, name='seller_enable'),
    path('vendedores/<int:seller_id>/excluir/', views.seller_delete, name='seller_delete'),

    # URLs de autenticação
    path('alterar-senha/', auth_views.PasswordChangeView.as_view(template_name='core/change_password.html'), name='change_password'),
    path('alterar-senha/sucesso/', auth_views.PasswordChangeDoneView.as_view(template_name='core/change_password_done.html'), name='change_password_done'),

    # URLs do carrinho
    path('carrinho/', views.carrinho, name='carrinho'),
    path('carrinho/adicionar/<int:product_id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('carrinho/remover/<int:product_id>/', views.remover_do_carrinho, name='remover_do_carrinho'),
] 