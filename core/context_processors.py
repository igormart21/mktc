from .models import MensagemSuporte

def mensagens_pendentes(request):
    """
    Adiciona o número de mensagens de suporte pendentes ao contexto.
    """
    if request.user.is_authenticated and request.user.is_superuser:
        return {
            'mensagens_pendentes': MensagemSuporte.objects.filter(respondido=False).count()
        }
    return {'mensagens_pendentes': 0} 