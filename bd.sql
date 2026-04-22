DROP DATABASE IF EXISTS petshop;
CREATE DATABASE petshop;
USE petshop;

-- PETS
CREATE TABLE pets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100),
    nascimento DATE,
    especie VARCHAR(10),
    raca VARCHAR(100)
);
INSERT INTO pets (id, nome, nascimento, especie, raca) VALUES
    ('1', 'Marina da Silva', '2015-09-26', 'Canis lupus familiaris','Labrador Retriever')
    ('2', 'Olivia Rodrigues', '2020-01-05','Canis lupus familiaris', 'Pastor Alemão') 
    ('3', 'Donatella Vieira', '2023-06-22', 'Canis lupus familiaris', 'Golden Retriever')

-- EVENTOS (AGENDA)
CREATE TABLE eventos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pet_id INT,
    data DATE,
    hora TIME,
    tipo VARCHAR(50),
    descricao VARCHAR(200),
    local VARCHAR(100),
    observacoes TEXT,
    FOREIGN KEY (pet_id) REFERENCES pets(id)
);
CREATE TABLE admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100),
    senha VARCHAR(100)
);

INSERT INTO admin (email, senha) VALUES 
('admin@gmail.com', '123456');

-- FUNCIONÁRIOS
CREATE TABLE funcionarios (
    nome VARCHAR(100),
    cargo VARCHAR(100) AUTO_INCREMENT PRIMARY KEY NOT NULL,
    salario DECIMAL(10,2),
    telefone VARCHAR(20)
);

