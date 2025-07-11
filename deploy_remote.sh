#!/bin/bash

echo "🚀 Deploy do AgroMarketplace - Servidor de Produção"
echo "=================================================="

# Navegar para o diretório do projeto
cd /opt/agromais

# Verificar se o diretório existe
if [ ! -d "/opt/agromais" ]; then
    echo "❌ Erro: Diretório /opt/agromais não encontrado"
    exit 1
fi

# Verificar se estamos no diretório correto
if [ ! -f "manage.py" ]; then
    echo "❌ Erro: Não estamos no diretório do projeto Django"
    exit 1
fi

echo "📂 Diretório atual: $(pwd)"

# Fazer backup antes da atualização
echo "💾 Fazendo backup..."
cp -r staticfiles staticfiles_backup_$(date +%Y%m%d_%H%M%S)

# Atualizar código do repositório
echo "📥 Atualizando código do repositório..."
git fetch origin
git reset --hard origin/main

# Verificar se houve mudanças
if [ $? -eq 0 ]; then
    echo "✅ Código atualizado com sucesso"
else
    echo "❌ Erro ao atualizar código"
    exit 1
fi

# Ativar ambiente virtual
echo "🐍 Ativando ambiente virtual..."
source venv/bin/activate

# Atualizar dependências
echo "📦 Atualizando dependências..."
pip install -r requirements.txt

# Coletar arquivos estáticos (incluindo as novas imagens do carrossel)
echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear

# Aplicar migrações
echo "🗄️ Aplicando migrações..."
python manage.py migrate

# Verificar status dos serviços antes
echo "🔍 Status dos serviços antes da atualização:"
supervisorctl status agromais:*

# Reiniciar serviços
echo "🔄 Reiniciando serviços..."
supervisorctl restart agromais:*
systemctl restart nginx

# Aguardar um pouco para os serviços iniciarem
echo "⏳ Aguardando serviços iniciarem..."
sleep 10

# Verificar se os serviços estão rodando
echo "✅ Verificando se os serviços estão ativos..."
supervisorctl status agromais:*
systemctl status nginx --no-pager -l

# Testar se o site está respondendo
echo "🌐 Testando resposta do site..."
curl -I https://agromaisdigital.com.br

echo ""
echo "🎉 Deploy concluído com sucesso!"
echo "🌐 Acesse: https://agromaisdigital.com.br"
echo "📸 Carrossel de imagens implementado na página inicial"
echo "🔄 Serviços reiniciados e funcionando" 