DROP DATABASE IF EXISTS petshop;
CREATE DATABASE petshop;
USE petshop;

-- CLIENTES
CREATE TABLE IF NOT EXISTS clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    cpf VARCHAR(20) NOT NULL,
    nascimento VARCHAR(15) NOT NULL,
    telefone VARCHAR(20) NOT NULL,
    senha VARCHAR(100) NOT NULL,
    profile_pic_url VARCHAR(255) DEFAULT '/assets/img/default-profile.png'
);

-- PETS
CREATE TABLE IF NOT EXISTS pets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT,
    nome VARCHAR(100),
    nascimento DATE,
    especie VARCHAR(50),
    raca VARCHAR(100),
    peso DECIMAL(5,2),
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
);

-- EVENTOS (AGENDA)
CREATE TABLE IF NOT EXISTS eventos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pet_id INT,
    data DATE,
    hora TIME,
    tipo VARCHAR(50),
    descricao VARCHAR(200),
    local VARCHAR(100),
    observacoes TEXT,
    FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE
);
-- ADMIN
CREATE TABLE IF NOT EXISTS admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha VARCHAR(100) NOT NULL,
    nome VARCHAR(100) NOT NULL DEFAULT 'Admin',
    profile_pic_url VARCHAR(255) DEFAULT '/assets/img/default-profile.png'
);
INSERT INTO admin (email, senha) VALUES 
-- A senha '123456' é armazenada como um hash SHA-256 para segurança.
('admin@gmail.com', '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92');
-- CARGOS
CREATE TABLE IF NOT EXISTS cargos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) UNIQUE NOT NULL
);
-- FUNCIONÁRIOS
CREATE TABLE IF NOT EXISTS funcionarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100),
    cargo VARCHAR(100),
    salario DECIMAL(10,2),
    telefone VARCHAR(20)
);

-- Dados de exemplo para funcionários
INSERT INTO funcionarios (nome, cargo, salario, telefone) VALUES 
('Isabela Silva dos Santos', 'Assistente administrativo', 1400.00, '41999999999'),
('Carlos Pereira', 'Veterinário', 3500.00, '41988888888'),
('Ana Souza', 'Banhista', 1800.00, '41977777777');