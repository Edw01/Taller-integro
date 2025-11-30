En este espacio nos centramos en el trabajo de taller integracion y la codificacion de nuestro proyecto que estamos llevando a cabo. Ademas nos centraremos en dejar la documentacion correspondientes y la actividad de cada integrante.

DB = POSTGRESQL

**Recuerde crear y utilizar el entorno virtual cada vez que avance en el proyecto, de no hacerlo, puede generar errores en el repositorio por falta de librerias, entre otros!**
Seguido de esto, ademas cada vez que agregue librerias, agreguelo al archivo ya hecho "requeriments.txt" mediante el comando: "pip freeze > requeriments.txt"
Nota: *Debe de encontrarse en la carpeta actual de requeriments.txt, de caso contrario, creara un nuevo archivo.*


## Guia del repositorio
1. Clonar el repositorio.
2. Crear entorno virtual: `python -m venv nombre-entorno`
3. Activar entorno mediante: `source directorio\activate`.
4. Instalar dependencias: `pip install -r requirements.txt`
5. Crear archivo `.env` dentro del directorio /system con tus credenciales para la base de datos. La estructura es por ejemplo: DB_NAME=miproyectodb (salto de linea) DB_USER=tuusuario (salto de linea) DB_PASSWORD=tucontra
6. Para correr migraciones: `python manage.py migrate`
7. Para correr el servidor: `python manage.py runserver`
