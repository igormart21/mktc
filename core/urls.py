from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.seller_registration, name='register'),
    path('perfil/', views.seller_profile, name='profile'),
    path('vendedor/registro/', views.seller_registration, name='seller_registration'),
    path('vendedor/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('vendedor/perfil/', views.seller_profile, name='seller_profile'),
    path('vendedor/solicitar-produto/', views.request_product, name='request_product'),
    path('superadmin/dashboard/', views.superadmin_dashboard, name='superadmin_dashboard'),
    path('produtos/', views.catalogo, name='products'),
    path('produtos/criar/', views.product_create, name='product_create'),
    path('produtos/detalhe/<int:pk>/', views.product_detail, name='product_detail'),
    path('produtos/excluir/<int:pk>/', views.product_delete, name='product_delete'),
    path('superadmin/vendedores/', views.listar_vendedores, name='listar_vendedores'),
    path('vendedores/', views.listar_vendedores, name='listar_vendedores'),
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
    path('pedidos/', views.pedidos, name='pedidos'),
    path('pedido/<int:pedido_id>/', views.pedido_detail, name='pedido_detail'),
    path('pedido/<int:pedido_id>/editar/', views.pedido_edit, name='pedido_edit'),
    path('pedido/<int:pedido_id>/aprovar/', views.aprovar_pedido, name='aprovar_pedido'),
    path('pedido/<int:pedido_id>/cancelar/', views.pedido_cancel, name='pedido_cancel'),
    path('pedido/<int:pedido_id>/reprovar/', views.reprovar_pedido, name='reprovar_pedido'),

    # URLs de produtos do superadmin
    path('superadmin/produtos/', views.superadmin_products, name='superadmin_products'),
    path('superadmin/produtos/criar/', views.superadmin_product_create, name='superadmin_product_create'),
    path('superadmin/produtos/editar/<int:pk>/', views.superadmin_product_update, name='superadmin_product_update'),
    path('superadmin/produtos/excluir/<int:pk>/', views.superadmin_product_delete, name='superadmin_product_delete'),

    # URLs de produtos do vendedor
    path('vendedor/produtos/', views.seller_products, name='seller_products'),
    path('vendedor/produtos/adicionar-ao-carrinho/<int:product_id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),

    # Superadmin - Pedidos
    path('superadmin/pedidos/', views.superadmin_pedidos, name='superadmin_pedidos'),
    path('superadmin/pedidos/<int:order_id>/', views.superadmin_order_detail, name='superadmin_order_detail'),
    path('superadmin/pedidos/<int:order_id>/excluir/', views.superadmin_order_delete, name='superadmin_order_delete'),

    # URLs de gerenciamento de vendedores
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
    path('adicionar-ao-carrinho/<int:product_id>/', views.adicionar_ao_carrinho, name='adicionar_ao_carrinho'),
    path('remover-do-carrinho/<int:product_id>/', views.remover_do_carrinho, name='remover_do_carrinho'),
    path('carrinho/checkout/', views.checkout, name='checkout'),

    path('consult-ia/', views.consult_ia, name="consult_ia"),
    path('consultar/', views.consult_ia_page, name="consult_ia_page"),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('suporte/', views.suporte, name='suporte'),
    path('superadmin/suporte/', views.superadmin_suporte, name='superadmin_suporte'),
    path('superadmin/solicitacoes/', views.superadmin_solicitacoes, name='superadmin_solicitacoes'),
    path('superadmin/solicitacoes/<int:pk>/', views.superadmin_detalhes_solicitacao, name='superadmin_detalhes_solicitacao'),
    path('solicitar-produto/', views.solicitar_produto, name='solicitar_produto'),
    path('minhas-solicitacoes/', views.minhas_solicitacoes, name='minhas_solicitacoes'),
    path('detalhes-solicitacao/<int:pk>/', views.detalhes_solicitacao, name='detalhes_solicitacao'),
    path('produtos/detalhe/<int:produto_id>/', views.produto_detalhe, name='produto_detalhe'),
    path('superadmin/perfil/', views.admin_profile, name='admin_profile'),
    path('superadmin/vendas/pendentes/', views.listar_vendas_pendentes, name='listar_vendas_pendentes'),
    path('superadmin/vendas/<int:venda_id>/aprovar/', views.aprovar_venda, name='aprovar_venda'),
    path('superadmin/vendas/<int:venda_id>/rejeitar/', views.rejeitar_venda, name='rejeitar_venda'),
    path('superadmin/compras-vendedores/', views.superadmin_compras_vendedores, name='superadmin_compras_vendedores'),
    path('vendedores/aprovar/<int:vendedor_id>/', views.aprovar_vendedor, name='aprovar_vendedor'),
    path('vendedores/reprovar/<int:vendedor_id>/', views.reprovar_vendedor, name='reprovar_vendedor'),
    path('historico-pedidos/', views.historico_pedidos_vendedor, name='historico_pedidos'),
    path('vendedores/<int:vendedor_id>/historico-pedidos/', views.historico_pedidos_vendedor_admin, name='historico_pedidos_admin'),
    path('suporte/encerrar/<int:mensagem_id>/', views.encerrar_caso, name='encerrar_caso'),
] 