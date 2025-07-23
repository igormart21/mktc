#!/bin/bash

# Script de Deploy para Produção - AgroMais
# Este script envia as atualizações para o servidor em produção

echo "🚀 Iniciando deploy para produção..."

# Configurações do servidor
SERVER_HOST="agromaisdigital.com.br"
SERVER_USER="root"
SERVER_PATH="/opt/agromais"
BACKUP_DIR="/opt/backups/$(date +%Y%m%d_%H%M%S)"

echo "📋 Configurações:"
echo "   Servidor: $SERVER_HOST"
echo "   Usuário: $SERVER_USER"
echo "   Caminho: $SERVER_PATH"
echo "   Backup: $BACKUP_DIR"

# 1. Criar backup do banco de dados
echo "💾 Criando backup do banco de dados..."
ssh $SERVER_USER@$SERVER_HOST "mkdir -p $BACKUP_DIR && mysqldump -u root -p agromais > $BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql"

# 2. Fazer backup dos arquivos atuais
echo "📁 Fazendo backup dos arquivos atuais..."
ssh $SERVER_USER@$SERVER_HOST "cp -r $SERVER_PATH $BACKUP_DIR/"

# 3. Enviar arquivos atualizados
echo "📤 Enviando arquivos atualizados..."
rsync -avz --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' --exclude='.env' \
    ./ $SERVER_USER@$SERVER_HOST:$SERVER_PATH/

# 4. Aplicar migrações
echo "🔄 Aplicando migrações..."
ssh $SERVER_USER@$SERVER_HOST "cd $SERVER_PATH && source venv/bin/activate && python manage.py migrate"

# 5. Coletar arquivos estáticos
echo "📦 Coletando arquivos estáticos..."
ssh $SERVER_USER@$SERVER_HOST "cd $SERVER_PATH && source venv/bin/activate && python manage.py collectstatic --noinput"

# 6. Reiniciar serviços
echo "🔄 Reiniciando serviços..."
ssh $SERVER_USER@$SERVER_HOST "systemctl restart gunicorn"
ssh $SERVER_USER@$SERVER_HOST "systemctl restart nginx"

# 7. Verificar status dos serviços
echo "✅ Verificando status dos serviços..."
ssh $SERVER_USER@$SERVER_HOST "systemctl status gunicorn --no-pager"
ssh $SERVER_USER@$SERVER_HOST "systemctl status nginx --no-pager"

echo "🎉 Deploy concluído com sucesso!"
echo "📊 Backup salvo em: $BACKUP_DIR"
echo "🌐 Site disponível em: https://$SERVER_HOST" 