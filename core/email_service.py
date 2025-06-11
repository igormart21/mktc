from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

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

        # Envia o e-mail
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[to_email],
            html_message=html_message,
            fail_silently=False,
        )

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