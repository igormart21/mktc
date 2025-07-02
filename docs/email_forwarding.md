# Reencaminhamento de Emails Automatizados

Este documento explica como configurar o reencaminhamento automático de todos os emails automatizados do sistema AgroMais.

## 📧 Emails Automatizados do Sistema

O sistema AgroMais envia automaticamente os seguintes tipos de email:

1. **Confirmação de Pedido** - Quando um cliente faz um pedido
2. **Recuperação de Senha** - Quando um usuário solicita reset de senha
3. **Boas-vindas** - Quando um novo usuário se cadastra
4. **Aprovação de Vendedor** - Quando um vendedor é aprovado
5. **Reprovação de Vendedor** - Quando um vendedor é reprovado

## 🚀 Soluções Implementadas

### Solução 1: EmailService Modificado (Recomendada)

**Vantagens:**
- ✅ Simples de configurar
- ✅ Não afeta outros emails do sistema
- ✅ Fácil de manter
- ✅ Logs detalhados

**Como configurar:**

1. Edite o arquivo `config/settings.py`
2. Localize a seção de configuração de emails
3. Descomente e adicione os emails desejados:

```python
# Configuração de reencaminhamento de emails automatizados
FORWARD_EMAILS = [
    'giovany@agromaisdigital.com.br',
    'vitor@agromaisdigital.com.br',
    'adricson@agromaisdigital.com.br',
    'administrativo.agroshowa@agromaisdigital.com.br',
]
```

4. Reinicie o servidor Django

### Solução 2: Backend de Email Personalizado (Avançada)

**Vantagens:**
- ✅ Reencaminha TODOS os emails do sistema
- ✅ Mais controle sobre o processo
- ✅ Pode ser usado com qualquer tipo de email

**Como configurar:**

1. Edite o arquivo `config/settings.py`
2. Mude a configuração do EMAIL_BACKEND:

```python
EMAIL_BACKEND = 'core.email_backend.ForwardingEmailBackend'
```

3. Configure os emails de reencaminhamento:

```python
FORWARD_EMAILS = [
    'admin@agromaisdigital.com.br',
    'gerente@agromaisdigital.com.br',
]
```

### Solução 3: Middleware de Email (Alternativa)

**Vantagens:**
- ✅ Intercepta emails em tempo real
- ✅ Pode ser ativado/desativado facilmente

**Como configurar:**

1. Adicione o middleware ao `MIDDLEWARE` no `settings.py`:

```python
MIDDLEWARE = [
    # ... outros middlewares ...
    'core.email_middleware.EmailForwardingMiddleware',
]
```

## 🧪 Testando a Configuração

Execute o script de teste para verificar se o reencaminhamento está funcionando:

```bash
python test_email_forwarding.py
```

## 📋 Exemplo de Configuração Completa

```python
# config/settings.py

# Configurações de E-mail
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.hostinger.com'
EMAIL_PORT = 465
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_HOST_USER = 'contato@agromaisdigital.com.br'
EMAIL_HOST_PASSWORD = 'Agromias1@'
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER

# Configuração de reencaminhamento de emails automatizados
FORWARD_EMAILS = [
    'giovany@agromaisdigital.com.br',           # Giovany
    'vitor@agromaisdigital.com.br',             # Vitor
    'adricson@agromaisdigital.com.br',          # Adricson
    'administrativo.agroshowa@agromaisdigital.com.br',  # Administrativo AgroShowa
]
```

## 🔍 Monitoramento

Os logs de reencaminhamento são registrados automaticamente. Você pode verificar:

1. **Logs do Django** - Procure por mensagens como "Email reencaminhado para: [...]"
2. **Caixa de entrada** - Verifique se os emails estão chegando nos endereços configurados
3. **Logs do servidor** - Verifique os logs do servidor web

## ⚠️ Considerações Importantes

1. **Limite de destinatários** - Alguns provedores de email têm limites para número de destinatários
2. **Spam** - Muitos emails podem ser marcados como spam
3. **Custos** - Mais destinatários = mais uso de recursos
4. **Privacidade** - Todos os emails serão visíveis para os endereços configurados

## 🛠️ Solução de Problemas

### Email não está sendo reencaminhado

1. Verifique se `FORWARD_EMAILS` está configurado corretamente
2. Confirme se o servidor foi reiniciado
3. Verifique os logs do Django
4. Teste com o script `test_email_forwarding.py`

### Erro de autenticação SMTP

1. Verifique as credenciais SMTP no `settings.py`
2. Confirme se o servidor SMTP está funcionando
3. Teste a conexão SMTP manualmente

### Emails marcados como spam

1. Configure SPF, DKIM e DMARC no domínio
2. Use um provedor de email confiável
3. Monitore a reputação do IP de envio

## 📞 Suporte

Para dúvidas ou problemas, entre em contato com a equipe de desenvolvimento. 