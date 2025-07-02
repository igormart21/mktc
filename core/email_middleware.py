from django.core.mail import EmailMessage
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class EmailForwardingMiddleware:
    """
    Middleware para reencaminhar automaticamente todos os emails enviados
    para endereços adicionais configurados.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Lista de emails para reencaminhamento
        self.forward_emails = getattr(settings, 'FORWARD_EMAILS', [])
    
    def __call__(self, request):
        response = self.get_response(request)
        return response
    
    def process_email(self, email_message):
        """
        Processa um email antes do envio para adicionar destinatários de reencaminhamento.
        """
        if self.forward_emails and isinstance(email_message, EmailMessage):
            # Adiciona os emails de reencaminhamento à lista de destinatários
            for forward_email in self.forward_emails:
                if forward_email not in email_message.recipients():
                    email_message.recipients().append(forward_email)
            
            logger.info(f"Email reencaminhado para: {self.forward_emails}")
        
        return email_message 