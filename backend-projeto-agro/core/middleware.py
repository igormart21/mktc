from django.http import JsonResponse
import logging
import traceback

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        # Log do erro
        logger.error(f"Erro não tratado: {str(exception)}")
        logger.error(traceback.format_exc())

        # Resposta de erro
        return JsonResponse({
            'error': 'Ocorreu um erro interno no servidor',
            'message': str(exception)
        }, status=500) 