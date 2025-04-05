-- Recriar o banco de dados
DROP DATABASE IF EXISTS marketplace_agro;
CREATE DATABASE marketplace_agro CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Recriar o usuário e conceder privilégios
DROP USER IF EXISTS 'agro_user'@'localhost';
CREATE USER 'agro_user'@'localhost' IDENTIFIED BY 'Agro12345';
GRANT ALL PRIVILEGES ON marketplace_agro.* TO 'agro_user'@'localhost';
FLUSH PRIVILEGES;

-- Selecionar o banco de dados
USE marketplace_agro; 