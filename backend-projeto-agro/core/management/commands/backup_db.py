from django.core.management.base import BaseCommand
from django.conf import settings
import os
import datetime
import subprocess
from pathlib import Path

class Command(BaseCommand):
    help = 'Faz backup do banco de dados'

    def handle(self, *args, **options):
        # Criar diretório de backup se não existir
        backup_dir = Path('backups')
        backup_dir.mkdir(exist_ok=True)

        # Nome do arquivo de backup com timestamp
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = backup_dir / f'backup_{timestamp}.sql'

        # Comando para backup do MySQL
        cmd = [
            'mysqldump',
            f'--user={settings.DATABASES["default"]["USER"]}',
            f'--password={settings.DATABASES["default"]["PASSWORD"]}',
            f'--host={settings.DATABASES["default"]["HOST"]}',
            settings.DATABASES["default"]["NAME"],
            f'--result-file={backup_file}'
        ]

        try:
            subprocess.run(cmd, check=True)
            self.stdout.write(self.style.SUCCESS(f'Backup criado com sucesso: {backup_file}'))
        except subprocess.CalledProcessError as e:
            self.stdout.write(self.style.ERROR(f'Erro ao criar backup: {str(e)}')) 