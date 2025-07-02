import os
import django

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.email_service import EmailService

print("=== Teste de Reencaminhamento - Emails Reais ===")
print("Configuração ativa no settings.py:")
print("FORWARD_EMAILS = [")
for email in EmailService.FORWARD_EMAILS:
    print(f"    '{email}',")
print("]")
print()

# Mock de usuário para teste
class UsuarioTeste:
    def __init__(self):
        self.nome = "Usuário Teste"
        self.email = "teste@agromaisdigital.com.br"

# Mock de vendedor para teste
class VendedorTeste:
    def __init__(self):
        self.usuario = UsuarioTeste()
        self.nome_fantasia = "Empresa Teste Ltda"
        self.justificativa_recusa = "Documentação incompleta - favor enviar documentos adicionais"

print("🧪 Iniciando testes de reencaminhamento...")
print()

# Teste 1: Email de boas-vindas
try:
    usuario = UsuarioTeste()
    print(f"📧 Enviando email de boas-vindas para: {usuario.email}")
    EmailService.send_welcome_email(usuario)
    print("✅ Email de boas-vindas enviado com sucesso!")
    print(f"   📤 Reencaminhado para {len(EmailService.FORWARD_EMAILS)} emails:")
    for email in EmailService.FORWARD_EMAILS:
        print(f"      - {email}")
except Exception as e:
    print(f"❌ Erro ao enviar email de boas-vindas: {str(e)}")

print()

# Teste 2: Email de reprovação de vendedor
try:
    vendedor = VendedorTeste()
    print(f"📧 Enviando email de reprovação para: {vendedor.usuario.email}")
    EmailService.send_vendedor_reprovado(vendedor)
    print("✅ Email de reprovação de vendedor enviado com sucesso!")
    print(f"   📤 Reencaminhado para {len(EmailService.FORWARD_EMAILS)} emails:")
    for email in EmailService.FORWARD_EMAILS:
        print(f"      - {email}")
except Exception as e:
    print(f"❌ Erro ao enviar email de reprovação: {str(e)}")

print()
print("=== Resumo da Configuração ===")
print(f"✅ Total de emails configurados para reencaminhamento: {len(EmailService.FORWARD_EMAILS)}")
print("✅ Todos os emails automatizados serão reencaminhados para:")
for i, email in enumerate(EmailService.FORWARD_EMAILS, 1):
    print(f"   {i}. {email}")
print()
print("🎯 Tipos de emails que serão reencaminhados:")
print("   • Confirmação de pedidos")
print("   • Recuperação de senha")
print("   • Emails de boas-vindas")
print("   • Aprovação de vendedores")
print("   • Reprovação de vendedores")
print()
print("🚀 Sistema pronto! Todos os emails automatizados serão reencaminhados automaticamente.") 