from django.http import HttpResponse
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def test_view(request):
    logger.info("DEBUG: View temporária foi chamada!")
    print("DEBUG: View temporária foi chamada!")  # Debug print
    return HttpResponse(f"""
        <html>
            <head>
                <title>Teste - AgroMarketplace</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    h1 {{ color: #2c3e50; }}
                </style>
            </head>
            <body>
                <h1>Teste - AgroMarketplace</h1>
                <p>Se você está vendo esta mensagem, o servidor está funcionando!</p>
                <p>Data e hora: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </body>
        </html>
    """) 