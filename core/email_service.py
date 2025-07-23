from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

ADMIN_EMAILS = [
    'giovany@agromaisdigital.com.br',
    'vitor@agromaisdigital.com.br',
    'adricson@agromaisdigital.com.br',
    'administrativo.agroshowa@agromaisdigital.com.br',
]

class EmailService:
    @staticmethod
    def send_email(subject, template_name, context, to_email, from_email=None):
        """
        Envia um e-mail usando um template HTML.
        
        Args:
            subject (str): Assunto do e-mail
            template_name (str): Nome do template HTML
            context (dict): Contexto para o template
            to_email (str): E-mail do destinatário
            from_email (str, optional): E-mail do remetente
        """
        if from_email is None:
            from_email = settings.DEFAULT_FROM_EMAIL

        # Adiciona o contexto STATIC_URL
        context['STATIC_URL'] = settings.STATIC_URL

        # Renderiza o template HTML
        html_message = render_to_string(template_name, context)
        
        # Cria a versão em texto plano
        plain_message = strip_tags(html_message)

        # Lista de destinatários (incluindo o destinatário original)
        recipient_list = [to_email]
        
        # Envia o e-mail
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False,
        )

    @staticmethod
    def notify_admin_new_user(usuario):
        subject = 'Novo cadastro de usuário'
        nome = getattr(usuario, "nome", "")
        if nome:
            message = f'Novo usuário cadastrado: {usuario.email} ({nome})'
        else:
            message = f'Novo usuário cadastrado: {usuario.email}'
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, ADMIN_EMAILS)

    @staticmethod
    def notify_admin_user_approved(usuario):
        subject = 'Usuário aprovado'
        message = f'O usuário {usuario.email} foi aprovado.'
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, ADMIN_EMAILS)

    @staticmethod
    def notify_admin_product_approved(produto):
        subject = 'Produto aprovado'
        # Verifica se é uma solicitação de produto ou produto direto
        if hasattr(produto, 'nome_produto'):
            # É uma SolicitacaoProduto
            message = f'A solicitação de produto "{produto.nome_produto}" foi aprovada.'
        else:
            # É um Produto
            message = f'O produto {produto.nome} foi aprovado.'
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, ADMIN_EMAILS)

    @staticmethod
    def notify_admin_new_order(pedido):
        subject = 'Novo pedido recebido'
        # Verifica se o pedido tem comprador
        if pedido.comprador:
            message = f'Novo pedido #{pedido.id} recebido de {pedido.comprador.email}.'
        else:
            message = f'Novo pedido #{pedido.id} recebido (comprador não especificado).'
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, ADMIN_EMAILS)

    @classmethod
    def send_order_confirmation(cls, pedido):
        """Envia e-mail de confirmação de pedido."""
        context = {
            'pedido': pedido,
            'pedido_url': f"{settings.SITE_URL}/pedidos/{pedido.id}/"
        }
        
        cls.send_email(
            subject=f'Confirmação de Pedido #{pedido.id} - AgroMais',
            template_name='emails/confirmacao_pedido.html',
            context=context,
            to_email=pedido.cliente.email
        )

    @classmethod
    def send_password_reset(cls, usuario, reset_url):
        """Envia e-mail de recuperação de senha."""
        context = {
            'usuario': usuario,
            'reset_url': reset_url
        }
        
        cls.send_email(
            subject='Recuperação de Senha - AgroMais',
            template_name='emails/recuperacao_senha.html',
            context=context,
            to_email=usuario.email
        )

    @classmethod
    def send_welcome_email(cls, usuario):
        """Envia e-mail de boas-vindas."""
        context = {
            'usuario': usuario,
            'login_url': f"{settings.SITE_URL}/login/"
        }
        
        cls.send_email(
            subject='Bem-vindo ao AgroMais!',
            template_name='emails/boas_vindas.html',
            context=context,
            to_email=usuario.email
        )

    @classmethod
    def send_vendedor_reprovado(cls, vendedor):
        """Envia e-mail de reprovação do vendedor, incluindo o motivo da recusa."""
        context = {
            'vendedor': vendedor
        }
        
        cls.send_email(
            subject='Cadastro Reprovado - AgroMais',
            template_name='emails/reprovacao_vendedor.html',
            context=context,
            to_email=vendedor.usuario.email
        )

    @classmethod
    def send_vendedor_aprovado(cls, vendedor, senha_provisoria):
        """Envia e-mail de aprovação do vendedor, incluindo senha provisória."""
        context = {
            'vendedor': vendedor,
            'senha_provisoria': senha_provisoria
        }
        cls.send_email(
            subject='Cadastro Aprovado - AgroMais',
            template_name='emails/aprovacao_vendedor.html',
            context=context,
            to_email=vendedor.usuario.email
        ) 