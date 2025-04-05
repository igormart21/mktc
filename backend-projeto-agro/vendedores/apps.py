from django.apps import AppConfig


class VendedoresConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vendedores'

    def ready(self):
        import vendedores.signals  # Conecta os sinais quando o app é carregado
