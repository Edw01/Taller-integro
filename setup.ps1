# Script de configuración para VoluntariadoMayor
# Este script configura la base de datos PostgreSQL y ejecuta las migraciones de Django

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Configuración VoluntariadoMayor" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Paso 1: Verificar PostgreSQL
Write-Host "1. Verificando PostgreSQL..." -ForegroundColor Yellow
try {
    $pgVersion = psql --version
    Write-Host "   ✓ PostgreSQL encontrado: $pgVersion" -ForegroundColor Green
} catch {
    Write-Host "   ✗ PostgreSQL no encontrado. Por favor instálalo." -ForegroundColor Red
    exit 1
}

# Paso 2: Solicitar contraseña de PostgreSQL
Write-Host ""
Write-Host "2. Configuración de la base de datos" -ForegroundColor Yellow
$pgPassword = Read-Host "   Ingresa la contraseña de PostgreSQL (usuario 'postgres')" -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($pgPassword)
$pgPasswordPlain = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)

# Paso 3: Crear la base de datos
Write-Host ""
Write-Host "3. Creando base de datos..." -ForegroundColor Yellow

# Configurar variable de entorno para psql
$env:PGPASSWORD = $pgPasswordPlain

try {
    # Crear la base de datos usando el script SQL
    psql -U postgres -c "DROP DATABASE IF EXISTS voluntariadomayor_db;"
    psql -U postgres -c "CREATE DATABASE voluntariadomayor_db WITH ENCODING='UTF8' LC_COLLATE='Spanish_Chile.1252' LC_CTYPE='Spanish_Chile.1252';"
    Write-Host "   ✓ Base de datos 'voluntariadomayor_db' creada" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Error al crear la base de datos" -ForegroundColor Red
    Write-Host "   Intenta ejecutar manualmente: psql -U postgres" -ForegroundColor Yellow
    exit 1
}

# Limpiar la contraseña de la variable de entorno
Remove-Item Env:PGPASSWORD

# Paso 4: Actualizar archivo .env
Write-Host ""
Write-Host "4. Actualizando archivo .env..." -ForegroundColor Yellow

$envContent = @"
# Configuración de la Base de Datos PostgreSQL
DB_NAME=voluntariadomayor_db
DB_USER=postgres
DB_PASSWORD=$pgPasswordPlain
DB_HOST=localhost
DB_PORT=5432

# Configuración de Django
SECRET_KEY=django-insecure-k2nj+5p-wfktvk+soi-pqdw65072r-kbb-zfrovcy-f-wq
DEBUG=True
"@

Set-Content -Path "system\.env" -Value $envContent -Encoding UTF8
Write-Host "   ✓ Archivo .env actualizado" -ForegroundColor Green

# Paso 5: Ejecutar migraciones de Django
Write-Host ""
Write-Host "5. Ejecutando migraciones de Django..." -ForegroundColor Yellow
Set-Location system

try {
    python manage.py makemigrations
    Write-Host "   ✓ Migraciones creadas" -ForegroundColor Green
    
    python manage.py migrate
    Write-Host "   ✓ Migraciones aplicadas" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Error al ejecutar migraciones" -ForegroundColor Red
    exit 1
}

# Paso 6: Crear superusuario
Write-Host ""
Write-Host "6. ¿Deseas crear un superusuario ahora? (S/N)" -ForegroundColor Yellow
$createSuper = Read-Host "   "

if ($createSuper -eq "S" -or $createSuper -eq "s") {
    python manage.py createsuperuser
}

# Resumen final
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ✓ Configuración completada" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para iniciar el servidor:" -ForegroundColor Yellow
Write-Host "  cd system" -ForegroundColor White
Write-Host "  python manage.py runserver" -ForegroundColor White
Write-Host ""
Write-Host "Accede a la aplicación en:" -ForegroundColor Yellow
Write-Host "  http://127.0.0.1:8000/" -ForegroundColor White
Write-Host "  http://127.0.0.1:8000/admin/" -ForegroundColor White
Write-Host ""
