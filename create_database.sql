-- Script para crear la base de datos VoluntariadoMayor
-- Ejecutar este script en PostgreSQL antes de correr las migraciones de Django

-- Eliminar la base de datos si existe (CUIDADO: esto borra todos los datos)
DROP DATABASE IF EXISTS voluntariadomayor_db;

-- Crear la base de datos con codificación UTF-8
CREATE DATABASE voluntariadomayor_db
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'Spanish_Chile.1252'
    LC_CTYPE = 'Spanish_Chile.1252'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- Mensaje de confirmación
\echo 'Base de datos voluntariadomayor_db creada exitosamente'
