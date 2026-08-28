CREATE DATABASE IF NOT EXISTS chapala;
USE chapala;

-- 1. Tabla de Cortes
CREATE TABLE IF NOT EXISTS cortes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(65) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    imagen LONGBLOB
);

-- 2. Tabla de Usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    es_admin TINYINT(1) DEFAULT 0
);

-- 3. Tabla de Carrito
CREATE TABLE IF NOT EXISTS carrito (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_corte INT NOT NULL,
    cantidad DECIMAL(10,2) NOT NULL DEFAULT 1.00,
    fecha_agregado DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (id_corte) REFERENCES cortes(id) ON DELETE CASCADE
);

-- 4. Tabla para el Historial de Ventas
CREATE TABLE IF NOT EXISTS ventas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- 5. Tabla para los Detalles de cada Venta
CREATE TABLE IF NOT EXISTS detalle_ventas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_venta INT NOT NULL,
    id_corte INT NOT NULL,
    cantidad DECIMAL(10,2) NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_venta) REFERENCES ventas(id) ON DELETE CASCADE,
    FOREIGN KEY (id_corte) REFERENCES cortes(id) ON DELETE CASCADE
);

-- Asignación de permisos de administrador
UPDATE usuarios SET es_admin = 1 WHERE email = 'enzosalvatierra44@gmail.com';