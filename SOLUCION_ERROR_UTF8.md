# 🔧 Solución al Error de UTF-8 en PostgreSQL

## ❌ Error Encontrado

```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xf3 in position 85: invalid continuation byte
```

## 🎯 Causa del Problema

1. El archivo `.env` no estaba correctamente configurado
2. La base de datos PostgreSQL no existe o tiene problemas de codificación
3. Puede haber caracteres especiales en la contraseña de PostgreSQL

## ✅ Solución Rápida

### Opción 1: Script Automático (Recomendado)

```powershell
# Desde la raíz del proyecto
.\setup.ps1
```

Este script te guiará paso a paso para:
- Crear la base de datos con codificación UTF-8
- Configurar el archivo .env
- Ejecutar las migraciones
- Crear el superusuario

---

### Opción 2: Manual

#### Paso 1: Configurar el archivo `.env`

Edita `system/.env` con tus credenciales de PostgreSQL:

```env
DB_NAME=voluntariadomayor_db
DB_USER=postgres
DB_PASSWORD=TU_CONTRASEÑA_AQUI
DB_HOST=localhost
DB_PORT=5432

SECRET_KEY=django-insecure-k2nj+5p-wfktvk+soi$pqdw65072r^+*kbb)zfrovcy(f!wq&+
DEBUG=True
```

**IMPORTANTE**: Si tu contraseña tiene caracteres especiales (ó, ñ, á, etc.), cámbiala temporalmente a una sin acentos.

#### Paso 2: Crear la base de datos en PostgreSQL

```powershell
# Conectar a PostgreSQL
psql -U postgres

# Dentro de psql, ejecutar:
DROP DATABASE IF EXISTS voluntariadomayor_db;

CREATE DATABASE voluntariadomayor_db
    WITH 
    ENCODING = 'UTF8'
    LC_COLLATE = 'Spanish_Chile.1252'
    LC_CTYPE = 'Spanish_Chile.1252';

# Verificar que se creó correctamente
\l

# Salir de psql
\q
```

#### Paso 3: Ejecutar las migraciones

```powershell
cd system
python manage.py makemigrations
python manage.py migrate
```

#### Paso 4: Crear superusuario

```powershell
python manage.py createsuperuser
```

#### Paso 5: Iniciar el servidor

```powershell
python manage.py runserver
```

---

## 🔍 Problemas Comunes

### Problema 1: "psql: error: connection to server failed"

**Solución**: PostgreSQL no está corriendo.

```powershell
# Verificar estado del servicio
Get-Service -Name postgresql*

# Iniciar el servicio
Start-Service postgresql-x64-16  # Ajusta el nombre según tu versión
```

### Problema 2: "FATAL: password authentication failed"

**Solución**: Contraseña incorrecta en el archivo `.env`

1. Verifica tu contraseña de PostgreSQL
2. Si no la recuerdas, restablécela:

```powershell
# Como administrador, edita el archivo pg_hba.conf
# Cambia 'md5' a 'trust' temporalmente
# Reinicia PostgreSQL
# Conecta sin contraseña y cambia la contraseña:

psql -U postgres
ALTER USER postgres WITH PASSWORD 'nueva_contraseña';
\q

# Revierte el cambio en pg_hba.conf
# Reinicia PostgreSQL
```

### Problema 3: "database does not exist"

**Solución**: La base de datos no se creó correctamente.

```powershell
# Crear manualmente
psql -U postgres -c "CREATE DATABASE voluntariadomayor_db WITH ENCODING='UTF8';"
```

### Problema 4: Error de codificación persiste

**Solución**: Usar una contraseña sin caracteres especiales.

1. Cambia tu contraseña de PostgreSQL a una simple (solo letras y números)
2. Actualiza el archivo `.env`
3. Intenta de nuevo

---

## 📝 Verificación Final

Antes de ejecutar `makemigrations`, verifica:

```powershell
# 1. PostgreSQL está corriendo
psql -U postgres -c "SELECT version();"

# 2. La base de datos existe
psql -U postgres -l | Select-String "voluntariadomayor_db"

# 3. El archivo .env está configurado
Get-Content system\.env

# 4. Python puede conectarse
cd system
python manage.py dbshell
# Si se conecta, escribe \q para salir
```

---

## 🚀 Después de Solucionar

Una vez que las migraciones funcionen correctamente:

```powershell
cd system

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Iniciar servidor
python manage.py runserver
```

Luego accede a:
- **Aplicación**: http://127.0.0.1:8000/
- **Admin**: http://127.0.0.1:8000/admin/

---

## 📞 Ayuda Adicional

Si el problema persiste:

1. Verifica que `psycopg2-binary` esté instalado:
   ```powershell
   pip install psycopg2-binary
   ```

2. Verifica la versión de Python (debe ser 3.8+):
   ```powershell
   python --version
   ```

3. Verifica que el archivo `.env` no tenga espacios extras:
   ```powershell
   Get-Content system\.env | Format-Hex
   ```

4. Si usas caracteres especiales en la contraseña, escápelos o usa una contraseña simple temporalmente.
