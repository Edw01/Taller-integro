"""
Configuración del panel de administración de Django para VoluntariadoMayor.

Este módulo registra y configura todos los modelos para su gestión
a través del panel de administración de Django.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Usuario, AdultoMayor, Solicitud, Postulacion, Mensaje


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    """
    Configuración del admin para el modelo Usuario personalizado.
    
    Extiende UserAdmin de Django para incluir los campos personalizados
    del modelo Usuario (rol, teléfono, dirección, etc.).
    """
    
    # Campos a mostrar en la lista de usuarios
    list_display = [
        'username',
        'email',
        'get_full_name',
        'rol_badge',
        'is_active',
        'is_staff',
        'fecha_registro',
    ]
    
    # Filtros laterales
    list_filter = [
        'rol',
        'is_active',
        'is_staff',
        'is_superuser',
        'fecha_registro',
    ]
    
    # Campos de búsqueda
    search_fields = [
        'username',
        'first_name',
        'last_name',
        'email',
        'telefono',
    ]
    
    # Ordenamiento por defecto
    ordering = ['-fecha_registro']
    
    # Configuración de fieldsets para el formulario de edición
    fieldsets = (
        ('Información de Autenticación', {
            'fields': ('username', 'password')
        }),
        ('Información Personal', {
            'fields': ('first_name', 'last_name', 'email', 'telefono', 'direccion')
        }),
        ('Rol y Estado', {
            'fields': ('rol', 'activo')
        }),
        ('Permisos', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Fechas Importantes', {
            'fields': ('last_login', 'date_joined', 'fecha_registro'),
            'classes': ('collapse',)
        }),
    )
    
    # Configuración para agregar nuevo usuario
    add_fieldsets = (
        ('Información de Autenticación', {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        ('Información Personal', {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'email', 'telefono', 'direccion'),
        }),
        ('Rol', {
            'classes': ('wide',),
            'fields': ('rol',),
        }),
    )
    
    # Campos de solo lectura
    readonly_fields = ['fecha_registro', 'last_login', 'date_joined']
    
    def rol_badge(self, obj):
        """
        Muestra el rol con un badge de color.
        
        Args:
            obj: Instancia de Usuario
            
        Returns:
            str: HTML con badge coloreado
        """
        colors = {
            'SOLICITANTE': '#007bff',  # Azul
            'VOLUNTARIO': '#28a745',   # Verde
        }
        color = colors.get(obj.rol, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_rol_display()
        )
    rol_badge.short_description = 'Rol'
    
    def get_full_name(self, obj):
        """Retorna el nombre completo del usuario."""
        return obj.get_full_name() or '(Sin nombre)'
    get_full_name.short_description = 'Nombre Completo'


@admin.register(AdultoMayor)
class AdultoMayorAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo AdultoMayor.
    
    Gestiona la información sensible de los beneficiarios del programa.
    """
    
    # Campos a mostrar en la lista
    list_display = [
        'rut',
        'nombre_completo',
        'edad_calculada',
        'telefono',
        'activo_badge',
        'fecha_registro',
    ]
    
    # Filtros laterales
    list_filter = [
        'activo',
        'fecha_registro',
    ]
    
    # Campos de búsqueda
    search_fields = [
        'rut',
        'nombres',
        'apellidos',
        'direccion',
        'telefono',
    ]
    
    # Ordenamiento por defecto
    ordering = ['apellidos', 'nombres']
    
    # Campos de solo lectura
    readonly_fields = ['fecha_registro', 'edad_calculada']
    
    # Organización del formulario
    fieldsets = (
        ('Información Personal', {
            'fields': ('rut', 'nombres', 'apellidos', 'fecha_nacimiento')
        }),
        ('Información de Contacto', {
            'fields': ('direccion', 'telefono', 'contacto_emergencia')
        }),
        ('Información Médica', {
            'fields': ('observaciones_medicas',),
            'classes': ('collapse',)
        }),
        ('Estado y Registro', {
            'fields': ('activo', 'fecha_registro', 'edad_calculada'),
        }),
    )
    
    def edad_calculada(self, obj):
        """
        Calcula y muestra la edad del adulto mayor.
        
        Args:
            obj: Instancia de AdultoMayor
            
        Returns:
            str: Edad en años
        """
        return f"{obj.edad} años"
    edad_calculada.short_description = 'Edad'
    
    def activo_badge(self, obj):
        """
        Muestra el estado activo con un ícono.
        
        Args:
            obj: Instancia de AdultoMayor
            
        Returns:
            str: HTML con ícono coloreado
        """
        if obj.activo:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Activo</span>'
            )
        return format_html(
            '<span style="color: red; font-weight: bold;">✗ Inactivo</span>'
        )
    activo_badge.short_description = 'Estado'


@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Solicitud.
    
    Gestiona las solicitudes de ayuda creadas por los Solicitantes.
    """
    
    # Campos a mostrar en la lista
    list_display = [
        'id',
        'titulo',
        'adulto_mayor_link',
        'creador_link',
        'estado_badge',
        'prioridad_badge',
        'fecha_creacion',
        'voluntario_asignado_link',
    ]
    
    # Filtros laterales
    list_filter = [
        'estado',
        'prioridad',
        'fecha_creacion',
        'fecha_limite',
    ]
    
    # Campos de búsqueda
    search_fields = [
        'titulo',
        'descripcion',
        'tipo_ayuda',
        'adulto_mayor__nombres',
        'adulto_mayor__apellidos',
        'creador__username',
        'creador__first_name',
        'creador__last_name',
    ]
    
    # Ordenamiento por defecto
    ordering = ['-fecha_creacion']
    
    # Campos de solo lectura
    readonly_fields = [
        'fecha_creacion',
        'fecha_actualizacion',
        'fecha_asignacion',
        'fecha_finalizacion',
        'postulaciones_count',
        'mensajes_count',
    ]
    
    # Organización del formulario
    fieldsets = (
        ('Información Básica', {
            'fields': ('titulo', 'descripcion', 'tipo_ayuda')
        }),
        ('Beneficiario y Creador', {
            'fields': ('adulto_mayor', 'creador')
        }),
        ('Estado y Prioridad', {
            'fields': ('estado', 'prioridad', 'fecha_limite')
        }),
        ('Asignación', {
            'fields': ('voluntario_asignado', 'fecha_asignacion'),
        }),
        ('Finalización', {
            'fields': ('fecha_finalizacion', 'comentarios_finalizacion'),
            'classes': ('collapse',)
        }),
        ('Estadísticas', {
            'fields': ('postulaciones_count', 'mensajes_count'),
            'classes': ('collapse',)
        }),
        ('Fechas del Sistema', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    # Acciones personalizadas
    actions = ['marcar_como_finalizada', 'marcar_como_pendiente']
    
    def estado_badge(self, obj):
        """
        Muestra el estado con un badge de color.
        
        Args:
            obj: Instancia de Solicitud
            
        Returns:
            str: HTML con badge coloreado
        """
        colors = {
            'PENDIENTE': '#ffc107',  # Amarillo
            'ASIGNADA': '#007bff',   # Azul
            'FINALIZADA': '#28a745', # Verde
        }
        color = colors.get(obj.estado, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    
    def prioridad_badge(self, obj):
        """
        Muestra la prioridad con un badge de color.
        
        Args:
            obj: Instancia de Solicitud
            
        Returns:
            str: HTML con badge coloreado
        """
        colors = {
            'BAJA': '#28a745',    # Verde
            'MEDIA': '#ffc107',   # Amarillo
            'ALTA': '#fd7e14',    # Naranja
            'URGENTE': '#dc3545', # Rojo
        }
        color = colors.get(obj.prioridad, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_prioridad_display()
        )
    prioridad_badge.short_description = 'Prioridad'
    
    def adulto_mayor_link(self, obj):
        """Crea un enlace al adulto mayor."""
        url = reverse('admin:adultomayor_adultomayor_change', args=[obj.adulto_mayor.id])
        return format_html('<a href="{}">{}</a>', url, obj.adulto_mayor.nombre_completo)
    adulto_mayor_link.short_description = 'Adulto Mayor'
    
    def creador_link(self, obj):
        """Crea un enlace al creador de la solicitud."""
        url = reverse('admin:adultomayor_usuario_change', args=[obj.creador.id])
        return format_html('<a href="{}">{}</a>', url, obj.creador.get_full_name())
    creador_link.short_description = 'Creador'
    
    def voluntario_asignado_link(self, obj):
        """Crea un enlace al voluntario asignado."""
        if obj.voluntario_asignado:
            url = reverse('admin:adultomayor_usuario_change', args=[obj.voluntario_asignado.id])
            return format_html('<a href="{}">{}</a>', url, obj.voluntario_asignado.get_full_name())
        return '-'
    voluntario_asignado_link.short_description = 'Voluntario Asignado'
    
    def postulaciones_count(self, obj):
        """Cuenta las postulaciones de la solicitud."""
        count = obj.postulaciones.count()
        return f"{count} postulación(es)"
    postulaciones_count.short_description = 'Postulaciones'
    
    def mensajes_count(self, obj):
        """Cuenta los mensajes de la solicitud."""
        count = obj.mensajes.count()
        return f"{count} mensaje(s)"
    mensajes_count.short_description = 'Mensajes'
    
    def marcar_como_finalizada(self, request, queryset):
        """Acción para marcar solicitudes como finalizadas."""
        updated = queryset.filter(estado='ASIGNADA').update(estado='FINALIZADA')
        self.message_user(request, f'{updated} solicitud(es) marcada(s) como finalizada(s).')
    marcar_como_finalizada.short_description = 'Marcar como Finalizada'
    
    def marcar_como_pendiente(self, request, queryset):
        """Acción para marcar solicitudes como pendientes."""
        updated = queryset.update(estado='PENDIENTE', voluntario_asignado=None)
        self.message_user(request, f'{updated} solicitud(es) marcada(s) como pendiente(s).')
    marcar_como_pendiente.short_description = 'Marcar como Pendiente'


@admin.register(Postulacion)
class PostulacionAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Postulacion.
    
    Gestiona las postulaciones de voluntarios a solicitudes.
    """
    
    # Campos a mostrar en la lista
    list_display = [
        'id',
        'voluntario_link',
        'solicitud_link',
        'estado_badge',
        'fecha_postulacion',
        'fecha_respuesta',
    ]
    
    # Filtros laterales
    list_filter = [
        'estado',
        'fecha_postulacion',
        'fecha_respuesta',
    ]
    
    # Campos de búsqueda
    search_fields = [
        'voluntario__username',
        'voluntario__first_name',
        'voluntario__last_name',
        'solicitud__titulo',
        'mensaje_postulacion',
    ]
    
    # Ordenamiento por defecto
    ordering = ['-fecha_postulacion']
    
    # Campos de solo lectura
    readonly_fields = ['fecha_postulacion', 'fecha_respuesta']
    
    # Organización del formulario
    fieldsets = (
        ('Información de la Postulación', {
            'fields': ('voluntario', 'solicitud', 'mensaje_postulacion')
        }),
        ('Estado', {
            'fields': ('estado', 'comentario_respuesta')
        }),
        ('Fechas', {
            'fields': ('fecha_postulacion', 'fecha_respuesta'),
        }),
    )
    
    def estado_badge(self, obj):
        """
        Muestra el estado con un badge de color.
        
        Args:
            obj: Instancia de Postulacion
            
        Returns:
            str: HTML con badge coloreado
        """
        colors = {
            'PENDIENTE': '#ffc107',  # Amarillo
            'ACEPTADA': '#28a745',   # Verde
            'RECHAZADA': '#dc3545',  # Rojo
        }
        color = colors.get(obj.estado, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    
    def voluntario_link(self, obj):
        """Crea un enlace al voluntario."""
        url = reverse('admin:adultomayor_usuario_change', args=[obj.voluntario.id])
        return format_html('<a href="{}">{}</a>', url, obj.voluntario.get_full_name())
    voluntario_link.short_description = 'Voluntario'
    
    def solicitud_link(self, obj):
        """Crea un enlace a la solicitud."""
        url = reverse('admin:adultomayor_solicitud_change', args=[obj.solicitud.id])
        return format_html('<a href="{}">{}</a>', url, obj.solicitud.titulo)
    solicitud_link.short_description = 'Solicitud'


@admin.register(Mensaje)
class MensajeAdmin(admin.ModelAdmin):
    """
    Configuración del admin para el modelo Mensaje.
    
    Gestiona los mensajes del chat entre usuarios.
    """
    
    # Campos a mostrar en la lista
    list_display = [
        'id',
        'remitente_link',
        'solicitud_link',
        'contenido_preview',
        'leido_badge',
        'fecha_envio',
    ]
    
    # Filtros laterales
    list_filter = [
        'leido',
        'fecha_envio',
    ]
    
    # Campos de búsqueda
    search_fields = [
        'remitente__username',
        'remitente__first_name',
        'remitente__last_name',
        'solicitud__titulo',
        'contenido',
    ]
    
    # Ordenamiento por defecto
    ordering = ['-fecha_envio']
    
    # Campos de solo lectura
    readonly_fields = ['fecha_envio', 'fecha_lectura']
    
    # Organización del formulario
    fieldsets = (
        ('Información del Mensaje', {
            'fields': ('solicitud', 'remitente', 'contenido')
        }),
        ('Estado de Lectura', {
            'fields': ('leido', 'fecha_lectura')
        }),
        ('Fechas', {
            'fields': ('fecha_envio',),
        }),
    )
    
    def contenido_preview(self, obj):
        """
        Muestra una vista previa del contenido del mensaje.
        
        Args:
            obj: Instancia de Mensaje
            
        Returns:
            str: Vista previa truncada del mensaje
        """
        max_length = 50
        if len(obj.contenido) > max_length:
            return f"{obj.contenido[:max_length]}..."
        return obj.contenido
    contenido_preview.short_description = 'Contenido'
    
    def leido_badge(self, obj):
        """
        Muestra el estado de lectura con un ícono.
        
        Args:
            obj: Instancia de Mensaje
            
        Returns:
            str: HTML con ícono coloreado
        """
        if obj.leido:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Leído</span>'
            )
        return format_html(
            '<span style="color: orange; font-weight: bold;">○ No leído</span>'
        )
    leido_badge.short_description = 'Estado'
    
    def remitente_link(self, obj):
        """Crea un enlace al remitente."""
        url = reverse('admin:adultomayor_usuario_change', args=[obj.remitente.id])
        return format_html('<a href="{}">{}</a>', url, obj.remitente.get_full_name())
    remitente_link.short_description = 'Remitente'
    
    def solicitud_link(self, obj):
        """Crea un enlace a la solicitud."""
        url = reverse('admin:adultomayor_solicitud_change', args=[obj.solicitud.id])
        return format_html('<a href="{}">{}</a>', url, obj.solicitud.titulo)
    solicitud_link.short_description = 'Solicitud'

