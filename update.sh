#!/bin/bash

# Atualizar código do repositório
echo "Atualizando código do repositório..."
cd /opt/agromais
git pull origin main

# Ativar ambiente virtual
echo "Ativando ambiente virtual..."
source venv/bin/activate

# Atualizar dependências
echo "Atualizando dependências..."
pip install -r requirements.txt

# Coletar arquivos estáticos
echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Aplicar migrações
echo "Aplicando migrações..."
python manage.py migrate

# Reiniciar serviços
echo "Reiniciando serviços..."
supervisorctl restart agromais:*
systemctl restart nginx

echo "Atualização concluída!" 