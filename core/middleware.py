from django.middleware.csrf import CsrfViewMiddleware

class CustomCsrfMiddleware(CsrfViewMiddleware):
    def process_view(self, request, callback, callback_args, callback_kwargs):
        """
        Processa a requisição antes da view ser chamada.
        Permite que requisições de APIs específicas ignorem a verificação CSRF.
        """
        # Lista de URLs que não precisam de verificação CSRF
        csrf_exempt_urls = [
            '/api/',  # Exemplo: todas as URLs que começam com /api/
        ]
        
        # Verifica se a URL atual está na lista de exceções
        for url in csrf_exempt_urls:
            if request.path.startswith(url):
                return None
        
        # Se não estiver na lista de exceções, aplica a verificação CSRF normalmente
        return super().process_view(request, callback, callback_args, callback_kwargs) 