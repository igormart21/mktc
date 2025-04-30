#!/bin/bash

# Configurações
BACKUP_DIR="/opt/agromais/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="mktc"
DB_USER="root"
DB_PASS="root123"

# Criar diretório de backup se não existir
mkdir -p $BACKUP_DIR

# Fazer backup do banco de dados
mysqldump -u$DB_USER -p$DB_PASS $DB_NAME > $BACKUP_DIR/backup_$DATE.sql

# Compactar o backup
gzip $BACKUP_DIR/backup_$DATE.sql

# Manter apenas os últimos 7 backups
find $BACKUP_DIR -name "backup_*.sql.gz" -type f -mtime +7 -delete 