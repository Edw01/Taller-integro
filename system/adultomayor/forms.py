"""
Formularios de la aplicación VoluntariadoMayor.

Este módulo contiene los formularios basados en ModelForm para la creación
y edición de Solicitudes, Postulaciones y otros modelos del sistema.
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Solicitud, Postulacion, AdultoMayor, Usuario, Mensaje


class SolicitudForm(forms.ModelForm):
    """
    Formulario para crear y editar Solicitudes.
    
    Utilizado por los Solicitantes (Jefes de Junta de Vecinos) para
    registrar peticiones de ayuda para adultos mayores.
    """
    
    class Meta:
        model = Solicitud
        fields = [
            'adulto_mayor',
            'titulo',
            'descripcion',
            'tipo_ayuda',
            'prioridad',
            'fecha_limite',
        ]
        
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Ayuda con compras semanales',
                'maxlength': '200'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describa detalladamente la ayuda que necesita el adulto mayor',
                'rows': 5
            }),
            'tipo_ayuda': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Compras, Trámites, Compañía, Traslados',
                'maxlength': '100'
            }),
            'adulto_mayor': forms.Select(attrs={
                'class': 'form-control'
            }),
            'prioridad': forms.Select(attrs={
                'class': 'form-control'
            }),
            'fecha_limite': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
        
        labels = {
            'adulto_mayor': 'Adulto Mayor Beneficiario',
            'titulo': 'Título de la Solicitud',
            'descripcion': 'Descripción Detallada',
            'tipo_ayuda': 'Tipo de Ayuda Requerida',
            'prioridad': 'Nivel de Prioridad',
            'fecha_limite': 'Fecha Límite (opcional)',
        }
        
        help_texts = {
            'titulo': 'Resuma brevemente la ayuda que necesita',
            'descripcion': 'Incluya todos los detalles relevantes',
            'tipo_ayuda': 'Especifique el tipo de asistencia necesaria',
            'prioridad': 'Indique qué tan urgente es la solicitud',
            'fecha_limite': 'Fecha en la que se necesita la ayuda',
        }
    
    def __init__(self, *args, **kwargs):
        """
        Constructor del formulario.
        
        Puede recibir un parámetro 'usuario' para filtrar adultos mayores
        según el contexto del solicitante.
        """
        self.usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar solo adultos mayores activos
        self.fields['adulto_mayor'].queryset = AdultoMayor.objects.filter(
            activo=True
        )
    
    def clean_fecha_limite(self):
        """
        Valida que la fecha límite no sea en el pasado.
        
        Returns:
            date: La fecha límite validada
            
        Raises:
            ValidationError: Si la fecha es anterior a hoy
        """
        fecha_limite = self.cleaned_data.get('fecha_limite')
        
        if fecha_limite:
            hoy = timezone.now().date()
            if fecha_limite < hoy:
                raise ValidationError(
                    'La fecha límite no puede ser anterior a la fecha actual.'
                )
        
        return fecha_limite
    
    def clean(self):
        """
        Validación adicional del formulario completo.
        
        Returns:
            dict: Datos limpios validados
        """
        cleaned_data = super().clean()
        
        # Validar que el título no sea solo espacios
        titulo = cleaned_data.get('titulo')
        if titulo and not titulo.strip():
            raise ValidationError({
                'titulo': 'El título no puede estar vacío.'
            })
        
        # Validar que la descripción tenga contenido significativo
        descripcion = cleaned_data.get('descripcion')
        if descripcion and len(descripcion.strip()) < 20:
            raise ValidationError({
                'descripcion': 'La descripción debe tener al menos 20 caracteres.'
            })
        
        return cleaned_data


class PostulacionForm(forms.ModelForm):
    """
    Formulario para que los Voluntarios postulen a Solicitudes.
    
    Permite a los voluntarios enviar un mensaje explicando por qué
    desean ayudar en una solicitud específica.
    """
    
    class Meta:
        model = Postulacion
        fields = ['mensaje_postulacion']
        
        widgets = {
            'mensaje_postulacion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Explique por qué desea ayudar en esta solicitud y cómo puede contribuir',
                'rows': 4
            }),
        }
        
        labels = {
            'mensaje_postulacion': 'Mensaje de Postulación',
        }
        
        help_texts = {
            'mensaje_postulacion': 'Cuéntele al solicitante por qué está interesado en ayudar',
        }
    
    def clean_mensaje_postulacion(self):
        """
        Valida que el mensaje de postulación tenga contenido adecuado.
        
        Returns:
            str: El mensaje validado
            
        Raises:
            ValidationError: Si el mensaje es muy corto o vacío
        """
        mensaje = self.cleaned_data.get('mensaje_postulacion')
        
        if not mensaje or not mensaje.strip():
            raise ValidationError('Debe incluir un mensaje de postulación.')
        
        if len(mensaje.strip()) < 30:
            raise ValidationError(
                'El mensaje debe tener al menos 30 caracteres para ser significativo.'
            )
        
        return mensaje.strip()


class AdultoMayorForm(forms.ModelForm):
    """
    Formulario para registrar y editar información de Adultos Mayores.
    
    Utilizado por administradores y solicitantes autorizados para
    gestionar los datos de los beneficiarios.
    """
    
    class Meta:
        model = AdultoMayor
        fields = [
            'rut',
            'nombres',
            'apellidos',
            'fecha_nacimiento',
            'direccion',
            'telefono',
            'contacto_emergencia',
            'observaciones_medicas',
            'activo',
        ]
        
        widgets = {
            'rut': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12345678-9',
                'maxlength': '12'
            }),
            'nombres': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombres del adulto mayor'
            }),
            'apellidos': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellidos del adulto mayor'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Dirección completa de residencia'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+56912345678'
            }),
            'contacto_emergencia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre y teléfono del contacto de emergencia'
            }),
            'observaciones_medicas': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Información médica relevante (opcional)'
            }),
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        
        labels = {
            'rut': 'RUT',
            'nombres': 'Nombres',
            'apellidos': 'Apellidos',
            'fecha_nacimiento': 'Fecha de Nacimiento',
            'direccion': 'Dirección de Residencia',
            'telefono': 'Teléfono de Contacto',
            'contacto_emergencia': 'Contacto de Emergencia',
            'observaciones_medicas': 'Observaciones Médicas',
            'activo': 'Beneficiario Activo',
        }
    
    def clean_rut(self):
        """
        Valida el formato del RUT chileno.
        
        Returns:
            str: El RUT validado en formato correcto
            
        Raises:
            ValidationError: Si el RUT es inválido
        """
        rut = self.cleaned_data.get('rut')
        
        if rut:
            # Remover puntos y espacios
            rut = rut.replace('.', '').replace(' ', '').upper()
            
            # Validar formato básico
            if '-' not in rut:
                raise ValidationError('El RUT debe incluir el guión. Formato: 12345678-9')
            
            partes = rut.split('-')
            if len(partes) != 2:
                raise ValidationError('Formato de RUT inválido. Use: 12345678-9')
            
            numero, digito = partes
            
            # Validar que el número sea numérico
            if not numero.isdigit():
                raise ValidationError('La parte numérica del RUT debe contener solo dígitos.')
            
            # Validar que el dígito verificador sea válido
            if digito not in '0123456789K':
                raise ValidationError('El dígito verificador debe ser un número o K.')
        
        return rut
    
    def clean_fecha_nacimiento(self):
        """
        Valida que la fecha de nacimiento sea coherente para un adulto mayor.
        
        Returns:
            date: La fecha de nacimiento validada
            
        Raises:
            ValidationError: Si la fecha no es válida
        """
        fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        
        if fecha_nacimiento:
            hoy = timezone.now().date()
            
            # Validar que no sea una fecha futura
            if fecha_nacimiento > hoy:
                raise ValidationError('La fecha de nacimiento no puede ser futura.')
            
            # Calcular edad
            edad = hoy.year - fecha_nacimiento.year - (
                (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day)
            )
            
            # Validar que sea adulto mayor (típicamente 60+ años)
            if edad < 60:
                raise ValidationError(
                    f'La persona debe ser adulto mayor (60+ años). Edad calculada: {edad} años.'
                )
            
            # Validar que la edad sea razonable (no más de 120 años)
            if edad > 120:
                raise ValidationError(
                    f'La edad calculada ({edad} años) parece incorrecta. Verifique la fecha.'
                )
        
        return fecha_nacimiento


class MensajeForm(forms.ModelForm):
    """
    Formulario para enviar mensajes en el chat de una solicitud.
    
    Permite la comunicación entre Solicitantes y Voluntarios.
    """
    
    class Meta:
        model = Mensaje
        fields = ['contenido']
        
        widgets = {
            'contenido': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Escriba su mensaje aquí...',
                'rows': 3
            }),
        }
        
        labels = {
            'contenido': 'Mensaje',
        }
    
    def clean_contenido(self):
        """
        Valida que el mensaje no esté vacío.
        
        Returns:
            str: El contenido del mensaje validado
            
        Raises:
            ValidationError: Si el mensaje está vacío
        """
        contenido = self.cleaned_data.get('contenido')
        
        if not contenido or not contenido.strip():
            raise ValidationError('El mensaje no puede estar vacío.')
        
        return contenido.strip()


class FinalizarSolicitudForm(forms.Form):
    """
    Formulario para finalizar una Solicitud.
    
    Permite al solicitante o voluntario agregar comentarios finales
    al completar una solicitud.
    """
    
    comentarios_finalizacion = forms.CharField(
        label='Comentarios de Finalización',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Describa cómo se completó la solicitud, resultados, etc.',
            'rows': 4
        }),
        required=False,
        help_text='Agregue cualquier información relevante sobre la finalización de la solicitud'
    )
    
    def clean_comentarios_finalizacion(self):
        """
        Limpia y valida los comentarios de finalización.
        
        Returns:
            str: Los comentarios validados
        """
        comentarios = self.cleaned_data.get('comentarios_finalizacion', '')
        return comentarios.strip()


class RespuestaPostulacionForm(forms.Form):
    """
    Formulario para que el Solicitante responda a una Postulación.
    
    Permite aceptar o rechazar postulaciones con un comentario opcional.
    """
    
    ACCIONES = (
        ('ACEPTAR', 'Aceptar Postulación'),
        ('RECHAZAR', 'Rechazar Postulación'),
    )
    
    accion = forms.ChoiceField(
        label='Acción',
        choices=ACCIONES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        })
    )
    
    comentario_respuesta = forms.CharField(
        label='Comentario (opcional)',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Agregue un comentario para el voluntario',
            'rows': 3
        }),
        required=False,
        help_text='Explique al voluntario la razón de su decisión'
    )
    
    def clean_comentario_respuesta(self):
        """
        Limpia el comentario de respuesta.
        
        Returns:
            str: El comentario validado
        """
        comentario = self.cleaned_data.get('comentario_respuesta', '')
        return comentario.strip()
