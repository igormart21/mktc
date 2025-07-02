from django.core.mail.backends.smtp import EmailBackend as SMTPBackend
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class ForwardingEmailBackend(SMTPBackend):
    """
    Backend de email personalizado que reencaminha automaticamente
    todos os emails para endereços configurados.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Lista de emails para reencaminhamento
        self.forward_emails = getattr(settings, 'FORWARD_EMAILS', [])
    
    def send_messages(self, email_messages):
        """
        Sobrescreve o método de envio para adicionar reencaminhamento.
        """
        # Processa cada mensagem para adicionar reencaminhamento
        for email_message in email_messages:
            if self.forward_emails:
                # Adiciona os emails de reencaminhamento
                for forward_email in self.forward_emails:
                    if forward_email not in email_message.recipients():
                        email_message.recipients().append(forward_email)
                
                logger.info(f"Email '{email_message.subject}' será reencaminhado para: {self.forward_emails}")
        
        # Chama o método original para enviar os emails
        return super().send_messages(email_messages) 