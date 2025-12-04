"""
Modelos de la aplicación VoluntariadoMayor.

Este módulo contiene los modelos de datos para gestionar el sistema de voluntariado
que conecta juntas de vecinos con estudiantes voluntarios para ayudar a adultos mayores.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, RegexValidator
from django.utils import timezone


class Usuario(AbstractUser):
    """
    Modelo de Usuario personalizado que extiende AbstractUser.
    
    Diferencia entre dos tipos de usuarios: Solicitante (Jefe Junta Vecinos)
    y Voluntario (Pastoral Universitaria).
    """
    
    ROLES = (
        ('SOLICITANTE', 'Solicitante - Jefe Junta Vecinos'),
        ('VOLUNTARIO', 'Voluntario - Pastoral Universitaria'),
    )
    
    rol = models.CharField(
        max_length=15,
        choices=ROLES,
        verbose_name='Rol del Usuario',
        help_text='Define si el usuario es Solicitante o Voluntario'
    )
    
    telefono = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message='Ingrese un número de teléfono válido.'
            )
        ],
        blank=True,
        null=True,
        verbose_name='Teléfono de Contacto'
    )
    
    direccion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Dirección'
    )
    
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Registro'
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name='Usuario Activo',
        help_text='Indica si el usuario está activo en el sistema'
    )
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-fecha_registro']
    
    def __str__(self):
        """Retorna una representación en string del usuario."""
        return f"{self.get_full_name()} ({self.get_rol_display()})"
    
    def es_solicitante(self):
        """Verifica si el usuario es un Solicitante."""
        return self.rol == 'SOLICITANTE'
    
    def es_voluntario(self):
        """Verifica si el usuario es un Voluntario."""
        return self.rol == 'VOLUNTARIO'


class AdultoMayor(models.Model):
    """
    Modelo para almacenar información protegida de los Adultos Mayores beneficiarios.
    
    Contiene datos sensibles que deben ser tratados con confidencialidad.
    """
    
    rut = models.CharField(
        max_length=12,
        unique=True,
        validators=[
            MinLengthValidator(9, 'El RUT debe tener al menos 9 caracteres'),
            RegexValidator(
                regex=r'^\d{7,8}-[\dkK]$',
                message='Formato de RUT inválido. Ejemplo: 12345678-9'
            )
        ],
        verbose_name='RUT',
        help_text='Formato: 12345678-9'
    )
    
    nombres = models.CharField(
        max_length=100,
        verbose_name='Nombres'
    )
    
    apellidos = models.CharField(
        max_length=100,
        verbose_name='Apellidos'
    )
    
    fecha_nacimiento = models.DateField(
        verbose_name='Fecha de Nacimiento'
    )
    
    direccion = models.TextField(
        verbose_name='Dirección de Residencia'
    )
    
    telefono = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message='Ingrese un número de teléfono válido.'
            )
        ],
        blank=True,
        null=True,
        verbose_name='Teléfono de Contacto'
    )
    
    contacto_emergencia = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Contacto de Emergencia',
        help_text='Nombre y teléfono del contacto de emergencia'
    )
    
    observaciones_medicas = models.TextField(
        blank=True,
        null=True,
        verbose_name='Observaciones Médicas',
        help_text='Información médica relevante para los voluntarios'
    )
    
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Registro'
    )
    
    activo = models.BooleanField(
        default=True,
        verbose_name='Beneficiario Activo',
        help_text='Indica si el adulto mayor está activo en el sistema'
    )
    
    class Meta:
        verbose_name = 'Adulto Mayor'
        verbose_name_plural = 'Adultos Mayores'
        ordering = ['apellidos', 'nombres']
    
    def __str__(self):
        """Retorna una representación en string del adulto mayor."""
        return f"{self.nombres} {self.apellidos} - RUT: {self.rut}"
    
    @property
    def nombre_completo(self):
        """Retorna el nombre completo del adulto mayor."""
        return f"{self.nombres} {self.apellidos}"
    
    @property
    def edad(self):
        """Calcula y retorna la edad del adulto mayor."""
        today = timezone.now().date()
        return today.year - self.fecha_nacimiento.year - (
            (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
        )


class Solicitud(models.Model):
    """
    Modelo para las Solicitudes de ayuda creadas por los Solicitantes.
    
    Representa una petición de ayuda para un adulto mayor específico.
    """
    
    ESTADOS = (
        ('PENDIENTE', 'Pendiente'),
        ('ASIGNADA', 'Asignada'),
        ('FINALIZADA', 'Finalizada'),
    )
    
    PRIORIDADES = (
        ('BAJA', 'Baja'),
        ('MEDIA', 'Media'),
        ('ALTA', 'Alta'),
        ('URGENTE', 'Urgente'),
    )
    
    creador = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='solicitudes_creadas',
        limit_choices_to={'rol': 'SOLICITANTE'},
        verbose_name='Creador de la Solicitud',
        help_text='Usuario Solicitante que crea la solicitud'
    )
    
    adulto_mayor = models.ForeignKey(
        AdultoMayor,
        on_delete=models.CASCADE,
        related_name='solicitudes',
        verbose_name='Adulto Mayor Beneficiario'
    )
    
    titulo = models.CharField(
        max_length=200,
        verbose_name='Título de la Solicitud'
    )
    
    descripcion = models.TextField(
        verbose_name='Descripción Detallada',
        help_text='Describa la ayuda que necesita el adulto mayor'
    )
    
    tipo_ayuda = models.CharField(
        max_length=100,
        verbose_name='Tipo de Ayuda',
        help_text='Ej: Compras, Trámites, Compañía, Traslados, etc.'
    )
    
    estado = models.CharField(
        max_length=15,
        choices=ESTADOS,
        default='PENDIENTE',
        verbose_name='Estado de la Solicitud'
    )
    
    prioridad = models.CharField(
        max_length=10,
        choices=PRIORIDADES,
        default='MEDIA',
        verbose_name='Prioridad'
    )
    
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    
    fecha_actualizacion = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Última Actualización'
    )
    
    fecha_limite = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha Límite',
        help_text='Fecha en la que se necesita la ayuda'
    )
    
    voluntario_asignado = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='solicitudes_asignadas',
        limit_choices_to={'rol': 'VOLUNTARIO'},
        blank=True,
        null=True,
        verbose_name='Voluntario Asignado'
    )
    
    fecha_asignacion = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Asignación'
    )
    
    fecha_finalizacion = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Finalización'
    )
    
    comentarios_finalizacion = models.TextField(
        blank=True,
        null=True,
        verbose_name='Comentarios de Finalización',
        help_text='Comentarios al finalizar la solicitud'
    )
    
    class Meta:
        verbose_name = 'Solicitud'
        verbose_name_plural = 'Solicitudes'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        """Retorna una representación en string de la solicitud."""
        return f"{self.titulo} - {self.get_estado_display()} ({self.adulto_mayor.nombre_completo})"
    
    def asignar_voluntario(self, voluntario):
        """
        Asigna un voluntario a la solicitud.
        
        Args:
            voluntario: Usuario con rol VOLUNTARIO a asignar
        """
        self.voluntario_asignado = voluntario
        self.estado = 'ASIGNADA'
        self.fecha_asignacion = timezone.now()
        self.save()
    
    def finalizar(self, comentarios=''):
        """
        Marca la solicitud como finalizada.
        
        Args:
            comentarios: Comentarios opcionales sobre la finalización
        """
        self.estado = 'FINALIZADA'
        self.fecha_finalizacion = timezone.now()
        self.comentarios_finalizacion = comentarios
        self.save()
    
    def esta_pendiente(self):
        """Verifica si la solicitud está pendiente."""
        return self.estado == 'PENDIENTE'
    
    def esta_asignada(self):
        """Verifica si la solicitud está asignada."""
        return self.estado == 'ASIGNADA'
    
    def esta_finalizada(self):
        """Verifica si la solicitud está finalizada."""
        return self.estado == 'FINALIZADA'


class Postulacion(models.Model):
    """
    Modelo para las Postulaciones de Voluntarios a Solicitudes.
    
    Relaciona un Voluntario con una Solicitud a la que desea postular.
    """
    
    ESTADOS_POSTULACION = (
        ('PENDIENTE', 'Pendiente'),
        ('ACEPTADA', 'Aceptada'),
        ('RECHAZADA', 'Rechazada'),
    )
    
    voluntario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='postulaciones',
        limit_choices_to={'rol': 'VOLUNTARIO'},
        verbose_name='Voluntario'
    )
    
    solicitud = models.ForeignKey(
        Solicitud,
        on_delete=models.CASCADE,
        related_name='postulaciones',
        verbose_name='Solicitud'
    )
    
    mensaje_postulacion = models.TextField(
        verbose_name='Mensaje de Postulación',
        help_text='Mensaje del voluntario explicando por qué desea ayudar'
    )
    
    estado = models.CharField(
        max_length=15,
        choices=ESTADOS_POSTULACION,
        default='PENDIENTE',
        verbose_name='Estado de la Postulación'
    )
    
    fecha_postulacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Postulación'
    )
    
    fecha_respuesta = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Respuesta'
    )
    
    comentario_respuesta = models.TextField(
        blank=True,
        null=True,
        verbose_name='Comentario de Respuesta',
        help_text='Comentario del solicitante al aceptar o rechazar'
    )
    
    class Meta:
        verbose_name = 'Postulación'
        verbose_name_plural = 'Postulaciones'
        ordering = ['-fecha_postulacion']
        unique_together = ['voluntario', 'solicitud']
    
    def __str__(self):
        """Retorna una representación en string de la postulación."""
        return f"Postulación de {self.voluntario.get_full_name()} a '{self.solicitud.titulo}' - {self.get_estado_display()}"
    
    def aceptar(self, comentario=''):
        """
        Acepta la postulación y asigna el voluntario a la solicitud.
        
        Args:
            comentario: Comentario opcional del solicitante
        """
        self.estado = 'ACEPTADA'
        self.fecha_respuesta = timezone.now()
        self.comentario_respuesta = comentario
        self.save()
        
        # Asignar el voluntario a la solicitud
        self.solicitud.asignar_voluntario(self.voluntario)
        
        # Rechazar las demás postulaciones pendientes
        Postulacion.objects.filter(
            solicitud=self.solicitud,
            estado='PENDIENTE'
        ).exclude(id=self.id).update(
            estado='RECHAZADA',
            fecha_respuesta=timezone.now(),
            comentario_respuesta='Postulación rechazada automáticamente: otro voluntario fue seleccionado'
        )
    
    def rechazar(self, comentario=''):
        """
        Rechaza la postulación.
        
        Args:
            comentario: Comentario opcional del solicitante
        """
        self.estado = 'RECHAZADA'
        self.fecha_respuesta = timezone.now()
        self.comentario_respuesta = comentario
        self.save()
    
    def esta_pendiente(self):
        """Verifica si la postulación está pendiente."""
        return self.estado == 'PENDIENTE'
    
    def esta_aceptada(self):
        """Verifica si la postulación fue aceptada."""
        return self.estado == 'ACEPTADA'
    
    def esta_rechazada(self):
        """Verifica si la postulación fue rechazada."""
        return self.estado == 'RECHAZADA'


class Mensaje(models.Model):
    """
    Modelo para los Mensajes del chat entre usuarios.
    
    Permite la comunicación entre Solicitantes y Voluntarios en el contexto
    de una Solicitud específica.
    """
    
    solicitud = models.ForeignKey(
        Solicitud,
        on_delete=models.CASCADE,
        related_name='mensajes',
        verbose_name='Solicitud Relacionada'
    )
    
    remitente = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='mensajes_enviados',
        verbose_name='Remitente'
    )
    
    contenido = models.TextField(
        verbose_name='Contenido del Mensaje'
    )
    
    fecha_envio = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Envío'
    )
    
    leido = models.BooleanField(
        default=False,
        verbose_name='Mensaje Leído',
        help_text='Indica si el mensaje ha sido leído por el destinatario'
    )
    
    fecha_lectura = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Lectura'
    )
    
    class Meta:
        verbose_name = 'Mensaje'
        verbose_name_plural = 'Mensajes'
        ordering = ['fecha_envio']
    
    def __str__(self):
        """Retorna una representación en string del mensaje."""
        preview = self.contenido[:50] + '...' if len(self.contenido) > 50 else self.contenido
        return f"Mensaje de {self.remitente.get_full_name()} en '{self.solicitud.titulo}': {preview}"
    
    def marcar_como_leido(self):
        """Marca el mensaje como leído."""
        if not self.leido:
            self.leido = True
            self.fecha_lectura = timezone.now()
            self.save()
