import os
import subprocess
from decouple import config

# Configurações do banco de dados
db_name = config('DB_NAME')
db_user = config('DB_USER')
db_password = config('DB_PASSWORD')
db_host = config('DB_HOST')

# Comandos SQL
commands = [
    f"DROP DATABASE IF EXISTS {db_name};",
    f"CREATE DATABASE {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;",
    f"GRANT ALL PRIVILEGES ON {db_name}.* TO '{db_user}'@'{db_host}';",
    "FLUSH PRIVILEGES;"
]

# Executar comandos
for cmd in commands:
    subprocess.run([
        'mysql',
        '-u', 'root',
        '-p',
        '-e', cmd
    ])

print("Banco de dados recriado com sucesso!") 