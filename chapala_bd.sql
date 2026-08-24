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
    password VARCHAR(255) NOT NULL
);

-- Consultas solicitadas
SELECT * FROM usuarios;
SELECT * FROM cortes;

-- Modificación de la tabla usuarios para agregar admin
ALTER TABLE usuarios ADD COLUMN es_admin TINYINT(1) DEFAULT 0;

-- Asignación de permisos de administrador
UPDATE usuarios SET es_admin = 1 WHERE email = 'enzosalvatierra44@gmail.com';

CREATE TABLE IF NOT EXISTS carrito (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_corte INT NOT NULL,
    cantidad INT NOT NULL DEFAULT 1, -- Aquí se guardan los kilos enteros
    fecha_agregado DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (id_corte) REFERENCES cortes(id) ON DELETE CASCADE
);

-- 4. Tabla para el Historial de Ventas (NUEVA)
CREATE TABLE IF NOT EXISTS ventas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- 5. Tabla para los Detalles de cada Venta (NUEVA)
CREATE TABLE IF NOT EXISTS detalle_ventas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_venta INT NOT NULL,
    id_corte INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_venta) REFERENCES ventas(id) ON DELETE CASCADE,
    FOREIGN KEY (id_corte) REFERENCES cortes(id) ON DELETE CASCADE
);
USE chapala;

-- Cambiamos el tipo de dato de 'cantidad' a DECIMAL en las tablas necesarias
ALTER TABLE carrito MODIFY COLUMN cantidad DECIMAL(10,2) NOT NULL DEFAULT 1.00;
ALTER TABLE detalle_ventas MODIFY COLUMN cantidad DECIMAL(10,2) NOT NULL;