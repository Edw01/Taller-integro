from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    ROLES = (
        ('PRESIDENTE', 'Presidente de Junta'),
        ('VOLUNTARIO', 'Voluntario'),
        ('ADULTO_MAYOR', 'Adulto Mayor'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rut = models.CharField(max_length=12, unique=True)
    rol = models.CharField(max_length=20, choices=ROLES)

    def __str__(self):
        return f"{self.user.username} - {self.rol}"

class Solicitud(models.Model):
    ESTADOS = (
        ('DISPONIBLE', 'Disponible'),
        ('ASIGNADA', 'Asignada'),
        ('FINALIZADA', 'Finalizada'),
    )
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    presidente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='solicitudes_creadas')
    voluntario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='solicitudes_voluntariado')
    adulto_mayor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='solicitudes_recibidas')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='DISPONIBLE')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo
