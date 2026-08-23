CREATE DATABASE IF NOT EXISTS chapala;
USE chapala;

CREATE TABLE IF NOT EXISTS cortes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(65) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    imagen LONGBLOB
);

CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

select * from usuarios;

select * from cortes;

ALTER TABLE usuarios ADD COLUMN es_admin TINYINT(1) DEFAULT 0;

UPDATE usuarios SET es_admin = 1 WHERE email = 'enzosalvatierra44@gmail.com';