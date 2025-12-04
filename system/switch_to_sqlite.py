# -*- coding: utf-8 -*-
"""
Configuración temporal de base de datos con SQLite
para evitar problemas de codificación con PostgreSQL
"""

import os
import sys
from pathlib import Path

# Configurar el entorno
BASE_DIR = Path(__file__).resolve().parent.parent

# Crear configuración temporal
sqlite_settings = f"""
# Usando SQLite temporalmente
DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }}
}}
"""

# Leer settings.py actual
settings_file = BASE_DIR / 'config' / 'settings.py'
with open(settings_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Comentar la configuración de PostgreSQL
if 'django.db.backends.postgresql' in content:
    print("Modificando settings.py para usar SQLite temporalmente...")
    
    # Guardar backup
    backup_file = BASE_DIR / 'config' / 'settings.py.backup'
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Backup creado en: {backup_file}")
    
    # Modificar
    lines = content.split('\n')
    new_lines = []
    in_databases_block = False
    brace_count = 0
    
    for line in lines:
        if "DATABASES = {" in line:
            in_databases_block = True
            new_lines.append("# DATABASES = {  # PostgreSQL comentado temporalmente")
            brace_count = 1
            continue
        
        if in_databases_block:
            if '{' in line:
                brace_count += line.count('{')
            if '}' in line:
                brace_count -= line.count('}')
            
            new_lines.append("# " + line)
            
            if brace_count == 0:
                in_databases_block = False
                # Agregar configuración SQLite
                new_lines.append("")
                new_lines.append("# Configuracion temporal con SQLite")
                new_lines.append("DATABASES = {")
                new_lines.append("    'default': {")
                new_lines.append("        'ENGINE': 'django.db.backends.sqlite3',")
                new_lines.append("        'NAME': BASE_DIR / 'db.sqlite3',")
                new_lines.append("    }")
                new_lines.append("}")
                continue
        
        new_lines.append(line)
    
    # Escribir nueva configuración
    with open(settings_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print("✓ settings.py modificado")
    print()
    print("=" * 60)
    print("  Ahora puedes ejecutar:")
    print("=" * 60)
    print("  python manage.py makemigrations")
    print("  python manage.py migrate")
    print("  python manage.py createsuperuser")
    print("  python manage.py runserver")
    print()
    print("NOTA: Esto es temporal. Para volver a PostgreSQL:")
    print("  1. Soluciona el problema de codificación UTF-8")
    print("  2. Restaura el backup: settings.py.backup")
    print()

else:
    print("La configuración de PostgreSQL ya está comentada o no existe.")
