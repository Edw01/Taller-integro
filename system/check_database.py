#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para verificar y crear la base de datos PostgreSQL para VoluntariadoMayor
"""

import os
import sys
from pathlib import Path

# Agregar el directorio de Django al path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv(BASE_DIR / '.env', encoding='utf-8')

print("="*60)
print("  Verificación de Base de Datos - VoluntariadoMayor")
print("="*60)
print()

# Verificar variables de entorno
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST', 'localhost')
db_port = os.getenv('DB_PORT', '5432')

print(f"Configuración cargada desde .env:")
print(f"  DB_NAME: {db_name}")
print(f"  DB_USER: {db_user}")
print(f"  DB_HOST: {db_host}")
print(f"  DB_PORT: {db_port}")
print(f"  DB_PASSWORD: {'*' * len(db_password) if db_password else 'NO CONFIGURADA'}")
print()

# Intentar conectar a PostgreSQL
try:
    import psycopg2
    from psycopg2 import sql
    print("✓ psycopg2 está instalado")
    print()
    
    # Intentar conectar a la base de datos postgres (la predeterminada)
    print(f"Intentando conectar a PostgreSQL...")
    conn = psycopg2.connect(
        dbname='postgres',
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    print("✓ Conexión exitosa a PostgreSQL")
    print()
    
    # Verificar si la base de datos existe
    cursor.execute(
        "SELECT 1 FROM pg_database WHERE datname = %s",
        (db_name,)
    )
    exists = cursor.fetchone()
    
    if exists:
        print(f"✓ La base de datos '{db_name}' ya existe")
        print()
        
        # Verificar que podemos conectarnos a ella
        try:
            test_conn = psycopg2.connect(
                dbname=db_name,
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port
            )
            test_conn.close()
            print(f"✓ Conexión exitosa a la base de datos '{db_name}'")
            print()
            print("="*60)
            print("  TODO LISTO - Puedes ejecutar las migraciones")
            print("="*60)
            print()
            print("Ejecuta los siguientes comandos:")
            print("  python manage.py makemigrations")
            print("  python manage.py migrate")
            print("  python manage.py createsuperuser")
            print("  python manage.py runserver")
            
        except psycopg2.Error as e:
            print(f"✗ No se puede conectar a la base de datos '{db_name}'")
            print(f"  Error: {e}")
            sys.exit(1)
            
    else:
        print(f"⚠ La base de datos '{db_name}' NO existe")
        print()
        response = input(f"¿Deseas crear la base de datos '{db_name}'? (s/n): ")
        
        if response.lower() in ['s', 'si', 'sí', 'y', 'yes']:
            try:
                cursor.execute(
                    sql.SQL("CREATE DATABASE {} WITH ENCODING='UTF8'").format(
                        sql.Identifier(db_name)
                    )
                )
                print(f"✓ Base de datos '{db_name}' creada exitosamente")
                print()
                print("="*60)
                print("  TODO LISTO - Puedes ejecutar las migraciones")
                print("="*60)
                print()
                print("Ejecuta los siguientes comandos:")
                print("  python manage.py makemigrations")
                print("  python manage.py migrate")
                print("  python manage.py createsuperuser")
                print("  python manage.py runserver")
                
            except psycopg2.Error as e:
                print(f"✗ Error al crear la base de datos")
                print(f"  Error: {e}")
                sys.exit(1)
        else:
            print()
            print("Operación cancelada. Por favor crea la base de datos manualmente:")
            print(f"  CREATE DATABASE {db_name} WITH ENCODING='UTF8';")
            sys.exit(1)
    
    cursor.close()
    conn.close()
    
except ImportError:
    print("✗ psycopg2 no está instalado")
    print()
    print("Instala psycopg2 con:")
    print("  pip install psycopg2-binary")
    sys.exit(1)
    
except psycopg2.OperationalError as e:
    print("✗ Error de conexión a PostgreSQL")
    print()
    print(f"Error: {e}")
    print()
    print("Posibles causas:")
    print("  1. PostgreSQL no está corriendo")
    print("  2. Las credenciales en .env son incorrectas")
    print("  3. El host o puerto son incorrectos")
    print()
    print("Soluciones:")
    print("  1. Verifica que PostgreSQL esté corriendo")
    print("  2. Verifica las credenciales en system/.env")
    print(f"     DB_USER={db_user}")
    print(f"     DB_PASSWORD=***")
    print(f"     DB_HOST={db_host}")
    print(f"     DB_PORT={db_port}")
    sys.exit(1)
    
except Exception as e:
    print(f"✗ Error inesperado: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
