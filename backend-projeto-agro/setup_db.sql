-- Criar o banco de dados
CREATE DATABASE IF NOT EXISTS marketplace_agro CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Criar o usuário e conceder privilégios
CREATE USER IF NOT EXISTS 'agro_user'@'localhost' IDENTIFIED BY 'Agro12345';
GRANT ALL PRIVILEGES ON marketplace_agro.* TO 'agro_user'@'localhost';
FLUSH PRIVILEGES;

-- Selecionar o banco de dados
USE marketplace_agro; 