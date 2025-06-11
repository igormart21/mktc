import os
import django

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.email_service import EmailService

# Novo destinatário para os testes
EMAIL_DESTINO = "vitor@agripro.com.br"

# Mock de vendedor aprovado para o teste
class UsuarioTeste:
    def __init__(self):
        self.nome = "Vitor"
        self.email = EMAIL_DESTINO

class VendedorAprovado:
    def __init__(self):
        self.id = 5678
        self.usuario = UsuarioTeste()
        self.status_aprovacao = 'APROVADO'
        self.nome_fantasia = 'AgroMais Teste'
        self.data_aprovacao = '2024-06-11'
        self.justificativa_recusa = ''

class VendedorReprovado:
    def __init__(self):
        self.id = 9101
        self.usuario = UsuarioTeste()
        self.status_aprovacao = 'RECUSADO'
        self.nome_fantasia = 'AgroMais Teste'
        self.data_aprovacao = '2024-06-11'
        self.justificativa_recusa = 'Documentação incompleta.'

# Teste de boas-vindas
try:
    usuario_teste = UsuarioTeste()
    EmailService.send_welcome_email(usuario_teste)
    print("E-mail de boas-vindas enviado com sucesso!")
except Exception as e:
    print(f"Erro ao enviar e-mail: {str(e)}")

tipo_item = type('Item', (), {})
tipo_pedido = type('Pedido', (), {})

item1 = tipo_item()
item1.produto = type('Produto', (), {'nome': 'Produto Teste'})()
item1.quantidade = 2
item1.preco_unitario = '49.90'

class ItensMock:
    def __init__(self, itens):
        self._itens = itens
    def all(self):
        return self._itens

pedido = tipo_pedido()
pedido.id = 1234
pedido.cliente = UsuarioTeste()
pedido.itens = ItensMock([item1])
pedido.valor_total = '99.80'

# Teste de confirmação de pedido
try:
    EmailService.send_order_confirmation(pedido)
    print("E-mail de confirmação de pedido enviado com sucesso!")
except Exception as e:
    print(f"Erro ao enviar e-mail: {str(e)}")

# Teste de aprovação de vendedor
try:
    vendedor = VendedorAprovado()
    senha_provisoria = 'Senha123@'
    EmailService.send_vendedor_aprovado(vendedor, senha_provisoria)
    print("E-mail de aprovação de vendedor enviado com sucesso!")
except Exception as e:
    print(f"Erro ao enviar e-mail: {str(e)}")

# Teste de reprovação de vendedor
try:
    vendedor = VendedorReprovado()
    EmailService.send_vendedor_reprovado(vendedor)
    print("E-mail de reprovação de vendedor enviado com sucesso!")
except Exception as e:
    print(f"Erro ao enviar e-mail: {str(e)}") 