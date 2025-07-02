import os
import django

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.email_service import EmailService

# Configurar emails de teste para reencaminhamento
# (Configurado no settings.py - usando os emails reais do sistema)
EmailService.FORWARD_EMAILS = [
    'giovany@agromaisdigital.com.br',
    'vitor@agromaisdigital.com.br',
    'adricson@agromaisdigital.com.br',
    'administrativo.agroshowa@agromaisdigital.com.br'
]

# Mock de usuário para teste
class UsuarioTeste:
    def __init__(self):
        self.nome = "João Silva"
        self.email = "joao@teste.com"

# Mock de vendedor para teste
class VendedorTeste:
    def __init__(self):
        self.usuario = UsuarioTeste()
        self.nome_fantasia = "Empresa Teste"
        self.justificativa_recusa = "Documentação incompleta"

print("=== Teste de Reencaminhamento de Emails ===")
print(f"Emails configurados para reencaminhamento: {EmailService.FORWARD_EMAILS}")
print()

# Teste 1: Email de boas-vindas
try:
    usuario = UsuarioTeste()
    EmailService.send_welcome_email(usuario)
    print("✅ Email de boas-vindas enviado com sucesso!")
    print(f"   Destinatário original: {usuario.email}")
    print(f"   Reencaminhado para: {EmailService.FORWARD_EMAILS}")
except Exception as e:
    print(f"❌ Erro ao enviar email de boas-vindas: {str(e)}")

print()

# Teste 2: Email de reprovação de vendedor
try:
    vendedor = VendedorTeste()
    EmailService.send_vendedor_reprovado(vendedor)
    print("✅ Email de reprovação de vendedor enviado com sucesso!")
    print(f"   Destinatário original: {vendedor.usuario.email}")
    print(f"   Reencaminhado para: {EmailService.FORWARD_EMAILS}")
except Exception as e:
    print(f"❌ Erro ao enviar email de reprovação: {str(e)}")

print()
print("=== Como Configurar ===")
print("1. Edite o arquivo config/settings.py")
print("2. Descomente e adicione os emails desejados na lista FORWARD_EMAILS:")
print("   FORWARD_EMAILS = [")
print("       'admin@agromaisdigital.com.br',")
print("       'gerente@agromaisdigital.com.br',")
print("       'suporte@agromaisdigital.com.br',")
print("   ]")
print()
print("3. Reinicie o servidor Django")
print("4. Todos os emails automatizados serão reencaminhados automaticamente!") 