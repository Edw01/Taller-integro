from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from adultomayor.models import Profile, Solicitud

class Command(BaseCommand):
    help = 'Carga datos de prueba iniciales (Usuarios, Roles, Solicitudes)'

    # Mensaje de inicio (Es un echo basicamente)
    def handle(self, *args, **kwargs):
        self.stdout.write('Iniciando carga de datos de prueba...')

        # Crear Presidente
        if not User.objects.filter(username='presi').exists():
            u1 = User.objects.create_user('presi', 'presi@example.com', 'pass1234', first_name='Juan', last_name='Perez')
            Profile.objects.create(user=u1, rut='11111111-1', rol='PRESIDENTE')
            self.stdout.write(self.style.SUCCESS('Creado usuario: presi (PRESIDENTE)'))

        # Crear Voluntario 1
        if not User.objects.filter(username='vol1').exists():
            u2 = User.objects.create_user('vol1', 'vol1@example.com', 'pass1234', first_name='Ana', last_name='Gomez')
            Profile.objects.create(user=u2, rut='22222222-2', rol='VOLUNTARIO')
            self.stdout.write(self.style.SUCCESS('Creado usuario: vol1 (VOLUNTARIO)'))

        # Crear Voluntario 2
        if not User.objects.filter(username='vol2').exists():
            u3 = User.objects.create_user('vol2', 'vol2@example.com', 'pass1234', first_name='Pedro', last_name='Soto')
            Profile.objects.create(user=u3, rut='33333333-3', rol='VOLUNTARIO')
            self.stdout.write(self.style.SUCCESS('Creado usuario: vol2 (VOLUNTARIO)'))

        # Crear Adulto Mayor
        if not User.objects.filter(username='abuelo1').exists():
            u4 = User.objects.create_user('abuelo1', 'abuelo1@example.com', 'pass1234', first_name='Maria', last_name='Lagos')
            Profile.objects.create(user=u4, rut='44444444-4', rol='ADULTO_MAYOR')
            self.stdout.write(self.style.SUCCESS('Creado usuario: abuelo1 (ADULTO_MAYOR)'))

        # Crear Solicitud de Prueba
        admin_user = User.objects.get(username='presi')
        if not Solicitud.objects.filter(titulo='Reparacion de Techo').exists():
            s = Solicitud.objects.create(
                titulo='Reparacion de Techo',
                descripcion='Se necesita ayuda para reparar goteras antes del invierno en casa de Doña Maria.',
                cantidad_presidentes=1,
                cantidad_voluntarios=2,
                cantidad_beneficiarios=1,
                presidente=admin_user
            )
            # Asignar beneficiario automaticamente para probar relacion
            abuelo = User.objects.get(username='abuelo1')
            s.adultos_mayores.add(abuelo)
            self.stdout.write(self.style.SUCCESS('Creada solicitud de prueba: Reparacion de Techo'))

        self.stdout.write(self.style.SUCCESS('Datos de prueba cargados exitosamente! Contraseña para todos: pass1234'))
