from django.middleware.csrf import CsrfViewMiddleware
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.contrib.auth import logout

class CustomCsrfMiddleware(CsrfViewMiddleware):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        """
        Processa a requisição antes da view ser chamada.
        Permite que requisições de APIs específicas ignorem a verificação CSRF.
        """
        # Lista de URLs que não precisam de verificação CSRF
        csrf_exempt_urls = [
            '/api/',  # Exemplo: todas as URLs que começam com /api/
            '/superadmin/vendedores/cadastrar/',  # URL do formulário de vendedor
        ]
        
        # Verifica se a URL atual está na lista de exceções
        for url in csrf_exempt_urls:
            if request.path.startswith(url):
                return None
        
        # Se não estiver na lista de exceções, aplica a verificação CSRF normalmente
        return super().process_view(request, callback, callback_args, callback_kwargs)

class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            current_time = timezone.now()
            last_activity = request.session.get('last_activity')
            
            if last_activity:
                last_activity = timezone.datetime.fromisoformat(last_activity)
                if current_time - last_activity > timedelta(minutes=30):  # 30 minutos de timeout
                    logout(request)
                    request.session.flush()
            
            request.session['last_activity'] = current_time.isoformat()
        
        response = self.get_response(request)
        return response 