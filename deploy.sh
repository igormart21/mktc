#!/bin/bash

# Atualizar sistema
echo "Atualizando sistema..."
apt update && apt upgrade -y

# Instalar dependências
echo "Instalando dependências..."
apt install -y python3-pip python3-venv nginx supervisor git mysql-server

# Configurar MySQL
echo "Configurando MySQL..."
mysql_secure_installation

# Criar diretório do projeto
echo "Criando diretório do projeto..."
mkdir -p /opt/agromais
cd /opt/agromais

# Clonar repositório
echo "Clonando repositório..."
git clone https://github.com/igormart21/mktc.git .

# Configurar ambiente virtual
echo "Configurando ambiente virtual..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependências Python
echo "Instalando dependências Python..."
pip install -r requirements.txt

# Configurar Nginx
echo "Configurando Nginx..."
cp nginx.conf /etc/nginx/sites-available/agromais
ln -s /etc/nginx/sites-available/agromais /etc/nginx/sites-enabled/
rm /etc/nginx/sites-enabled/default

# Configurar Supervisor
echo "Configurando Supervisor..."
cp supervisor.conf /etc/supervisor/conf.d/agromais.conf

# Configurar SSL
echo "Configurando SSL..."
apt install -y certbot python3-certbot-nginx
certbot --nginx -d agromaisdigital.com.br

# Reiniciar serviços
echo "Reiniciando serviços..."
systemctl restart nginx
supervisorctl reread
supervisorctl update
supervisorctl start agromais:*

echo "Deploy concluído!" 