#!/bin/bash

echo "🚀 Iniciando atualização do AgroMarketplace..."

# Verificar se estamos no diretório correto
if [ ! -f "manage.py" ]; then
    echo "❌ Erro: Não estamos no diretório do projeto Django"
    exit 1
fi

# Atualizar código do repositório
echo "📥 Atualizando código do repositório..."
git pull origin main

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
python manage.py collectstatic --noinput

# Aplicar migrações
echo "🗄️ Aplicando migrações..."
python manage.py migrate

# Verificar status dos serviços
echo "🔍 Verificando status dos serviços..."
supervisorctl status agromais:*

# Reiniciar serviços
echo "🔄 Reiniciando serviços..."
supervisorctl restart agromais:*
systemctl restart nginx

# Verificar se os serviços estão rodando
echo "✅ Verificando se os serviços estão ativos..."
sleep 5
supervisorctl status agromais:*
systemctl status nginx --no-pager -l

echo "🎉 Atualização concluída com sucesso!"
echo "🌐 Acesse: https://agromaisdigital.com.br"
echo "📸 Carrossel de imagens implementado na página inicial" 