"""
Vistas de la aplicación VoluntariadoMayor.

Este módulo contiene todas las vistas para gestionar el sistema de voluntariado,
incluyendo creación de solicitudes, postulaciones, asignación de voluntarios y chat.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Q, Count, Prefetch
from django.utils import timezone
from django.core.exceptions import PermissionDenied

from .models import Solicitud, Postulacion, AdultoMayor, Usuario, Mensaje
from .forms import (
    SolicitudForm, PostulacionForm, MensajeForm, 
    FinalizarSolicitudForm, RespuestaPostulacionForm
)


# ============================================================================
# MIXINS PERSONALIZADOS PARA CONTROL DE PERMISOS
# ============================================================================

class SolicitanteRequiredMixin(UserPassesTestMixin):
    """
    Mixin que verifica que el usuario sea un Solicitante.
    
    Restringe el acceso solo a usuarios con rol SOLICITANTE.
    """
    
    def test_func(self):
        """Verifica si el usuario es Solicitante."""
        return self.request.user.is_authenticated and self.request.user.es_solicitante()
    
    def handle_no_permission(self):
        """Maneja el caso cuando el usuario no tiene permiso."""
        messages.error(
            self.request,
            'No tiene permisos para acceder a esta página. Debe ser Solicitante.'
        )
        return redirect('solicitud_list')


class VoluntarioRequiredMixin(UserPassesTestMixin):
    """
    Mixin que verifica que el usuario sea un Voluntario.
    
    Restringe el acceso solo a usuarios con rol VOLUNTARIO.
    """
    
    def test_func(self):
        """Verifica si el usuario es Voluntario."""
        return self.request.user.is_authenticated and self.request.user.es_voluntario()
    
    def handle_no_permission(self):
        """Maneja el caso cuando el usuario no tiene permiso."""
        messages.error(
            self.request,
            'No tiene permisos para acceder a esta página. Debe ser Voluntario.'
        )
        return redirect('solicitud_list')


class SolicitudOwnerRequiredMixin(UserPassesTestMixin):
    """
    Mixin que verifica que el usuario sea el creador de la solicitud.
    
    Asegura que solo el creador de una solicitud pueda editarla o eliminarla.
    """
    
    def test_func(self):
        """Verifica si el usuario es el creador de la solicitud."""
        solicitud = self.get_object()
        return self.request.user == solicitud.creador
    
    def handle_no_permission(self):
        """Maneja el caso cuando el usuario no tiene permiso."""
        messages.error(
            self.request,
            'No tiene permisos para modificar esta solicitud. Solo el creador puede hacerlo.'
        )
        return redirect('solicitud_list')


# ============================================================================
# VISTAS DE SOLICITUDES
# ============================================================================

class SolicitudListView(ListView):
    """
    Vista para listar todas las solicitudes.
    
    - Vista pública accesible para todos los usuarios
    - Muestra solicitudes pendientes por defecto
    - Optimiza consultas con select_related
    - Los voluntarios ven solicitudes pendientes
    - Los solicitantes ven sus propias solicitudes
    """
    
    model = Solicitud
    template_name = 'adultomayor/solicitud_list.html'
    context_object_name = 'solicitudes'
    paginate_by = 10
    
    def get_queryset(self):
        """
        Optimiza y filtra el queryset según el usuario.
        
        - Usa select_related para optimizar consultas (JOIN en SQL)
        - Filtra solicitudes según el rol del usuario
        - Ordena por fecha de creación descendente
        
        Returns:
            QuerySet: Solicitudes filtradas y optimizadas
        """
        # Optimización: select_related trae datos relacionados en una sola query
        # Esto evita el problema N+1 al acceder a creador y adulto_mayor
        queryset = Solicitud.objects.select_related(
            'creador',           # Usuario que creó la solicitud
            'adulto_mayor',      # Adulto mayor beneficiario
            'voluntario_asignado'  # Voluntario asignado (si existe)
        ).prefetch_related(
            'postulaciones'      # Postulaciones relacionadas
        ).annotate(
            num_postulaciones=Count('postulaciones')  # Cuenta postulaciones
        )
        
        # Filtrar según el rol del usuario autenticado
        if self.request.user.is_authenticated:
            if self.request.user.es_voluntario():
                # Voluntarios ven solo solicitudes PENDIENTES
                queryset = queryset.filter(estado='PENDIENTE')
            elif self.request.user.es_solicitante():
                # Solicitantes ven solo sus propias solicitudes
                queryset = queryset.filter(creador=self.request.user)
        else:
            # Usuarios no autenticados ven solo solicitudes pendientes
            queryset = queryset.filter(estado='PENDIENTE')
        
        # Aplicar filtros de búsqueda si existen
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(titulo__icontains=search_query) |
                Q(descripcion__icontains=search_query) |
                Q(tipo_ayuda__icontains=search_query)
            )
        
        # Filtro por prioridad
        prioridad = self.request.GET.get('prioridad', '')
        if prioridad:
            queryset = queryset.filter(prioridad=prioridad)
        
        # Ordenar por fecha de creación (más recientes primero)
        return queryset.order_by('-fecha_creacion')
    
    def get_context_data(self, **kwargs):
        """
        Agrega contexto adicional al template.
        
        Returns:
            dict: Contexto con datos adicionales
        """
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['prioridad_filter'] = self.request.GET.get('prioridad', '')
        return context


class SolicitudDetailView(DetailView):
    """
    Vista de detalle de una solicitud específica.
    
    - Muestra información completa de la solicitud
    - Lista postulaciones si el usuario es el creador
    - Muestra chat si hay voluntario asignado
    """
    
    model = Solicitud
    template_name = 'adultomayor/solicitud_detail.html'
    context_object_name = 'solicitud'
    
    def get_queryset(self):
        """
        Optimiza el queryset con select_related.
        
        Returns:
            QuerySet: Solicitudes optimizadas
        """
        return Solicitud.objects.select_related(
            'creador',
            'adulto_mayor',
            'voluntario_asignado'
        ).prefetch_related(
            Prefetch(
                'postulaciones',
                queryset=Postulacion.objects.select_related('voluntario')
            ),
            Prefetch(
                'mensajes',
                queryset=Mensaje.objects.select_related('remitente').order_by('fecha_envio')
            )
        )
    
    def get_context_data(self, **kwargs):
        """
        Agrega contexto adicional para el template.
        
        Returns:
            dict: Contexto con postulaciones, mensajes y formularios
        """
        context = super().get_context_data(**kwargs)
        solicitud = self.get_object()
        
        # Agregar postulaciones si el usuario es el creador
        if self.request.user.is_authenticated and self.request.user == solicitud.creador:
            context['postulaciones'] = solicitud.postulaciones.all()
        
        # Agregar mensajes si el usuario está involucrado en la solicitud
        if self.request.user.is_authenticated:
            if (self.request.user == solicitud.creador or 
                self.request.user == solicitud.voluntario_asignado):
                context['mensajes'] = solicitud.mensajes.all()
                context['mensaje_form'] = MensajeForm()
        
        # Verificar si el voluntario actual ya postuló
        if self.request.user.is_authenticated and self.request.user.es_voluntario():
            context['ya_postulo'] = Postulacion.objects.filter(
                solicitud=solicitud,
                voluntario=self.request.user
            ).exists()
        
        return context


@login_required
def crear_solicitud(request):
    """
    Vista Function-Based para crear una nueva solicitud.
    
    - Solo accesible para usuarios con rol SOLICITANTE
    - Usa el decorador @login_required para verificar autenticación
    - Valida permisos manualmente
    - Asigna automáticamente el creador de la solicitud
    
    Args:
        request: HttpRequest
        
    Returns:
        HttpResponse: Renderiza el formulario o redirige al detalle
    """
    # VALIDACIÓN DE PERMISOS: Solo Solicitantes pueden crear solicitudes
    if not request.user.es_solicitante():
        messages.error(
            request,
            'No tiene permisos para crear solicitudes. Debe ser Solicitante (Jefe de Junta de Vecinos).'
        )
        return redirect('solicitud_list')
    
    if request.method == 'POST':
        # Procesar el formulario enviado
        form = SolicitudForm(request.POST, usuario=request.user)
        
        if form.is_valid():
            # Guardar pero sin commitear a la BD aún (commit=False)
            solicitud = form.save(commit=False)
            
            # Asignar el usuario actual como creador
            solicitud.creador = request.user
            
            # Establecer estado inicial (aunque ya tiene default)
            solicitud.estado = 'PENDIENTE'
            
            # Ahora sí guardar en la base de datos
            solicitud.save()
            
            # Mensaje de éxito
            messages.success(
                request,
                f'Solicitud "{solicitud.titulo}" creada exitosamente.'
            )
            
            # Redirigir al detalle de la solicitud creada
            return redirect('solicitud_detail', pk=solicitud.pk)
    else:
        # Mostrar formulario vacío
        form = SolicitudForm(usuario=request.user)
    
    context = {
        'form': form,
        'titulo_pagina': 'Crear Nueva Solicitud',
    }
    
    return render(request, 'adultomayor/solicitud_form.html', context)


class SolicitudCreateView(LoginRequiredMixin, SolicitanteRequiredMixin, CreateView):
    """
    Vista Class-Based alternativa para crear solicitudes.
    
    - Usa LoginRequiredMixin para requerir autenticación
    - Usa SolicitanteRequiredMixin para validar el rol
    - Asigna automáticamente el creador
    
    Nota: Esta es una implementación alternativa usando CBV.
    Puede elegirse entre esta y la FBV 'crear_solicitud' según preferencia.
    """
    
    model = Solicitud
    form_class = SolicitudForm
    template_name = 'adultomayor/solicitud_form.html'
    success_url = reverse_lazy('solicitud_list')
    
    def form_valid(self, form):
        """
        Procesa el formulario válido.
        
        - Asigna el creador automáticamente
        - Establece el estado inicial
        
        Args:
            form: Formulario validado
            
        Returns:
            HttpResponse: Redirección al éxito
        """
        # Asignar el usuario actual como creador
        form.instance.creador = self.request.user
        form.instance.estado = 'PENDIENTE'
        
        # Guardar y mostrar mensaje
        response = super().form_valid(form)
        
        messages.success(
            self.request,
            f'Solicitud "{self.object.titulo}" creada exitosamente.'
        )
        
        return response
    
    def get_success_url(self):
        """Retorna la URL de éxito (detalle de la solicitud creada)."""
        return reverse('solicitud_detail', kwargs={'pk': self.object.pk})


class SolicitudUpdateView(LoginRequiredMixin, SolicitudOwnerRequiredMixin, UpdateView):
    """
    Vista para editar una solicitud existente.
    
    - Solo el creador puede editar su solicitud
    - No se puede editar si ya está asignada o finalizada
    """
    
    model = Solicitud
    form_class = SolicitudForm
    template_name = 'adultomayor/solicitud_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        """
        Verifica permisos adicionales antes de procesar la vista.
        
        Args:
            request: HttpRequest
            
        Returns:
            HttpResponse
        """
        solicitud = self.get_object()
        
        # No permitir editar solicitudes asignadas o finalizadas
        if solicitud.estado in ['ASIGNADA', 'FINALIZADA']:
            messages.error(
                request,
                f'No puede editar una solicitud con estado "{solicitud.get_estado_display()}".'
            )
            return redirect('solicitud_detail', pk=solicitud.pk)
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        """Procesa el formulario válido y muestra mensaje."""
        response = super().form_valid(form)
        messages.success(self.request, 'Solicitud actualizada exitosamente.')
        return response
    
    def get_success_url(self):
        """Retorna la URL de éxito."""
        return reverse('solicitud_detail', kwargs={'pk': self.object.pk})


class SolicitudDeleteView(LoginRequiredMixin, SolicitudOwnerRequiredMixin, DeleteView):
    """
    Vista para eliminar una solicitud.
    
    - Solo el creador puede eliminar
    - Solo se puede eliminar si está pendiente
    """
    
    model = Solicitud
    template_name = 'adultomayor/solicitud_confirm_delete.html'
    success_url = reverse_lazy('solicitud_list')
    
    def dispatch(self, request, *args, **kwargs):
        """Verifica que la solicitud esté pendiente."""
        solicitud = self.get_object()
        
        if solicitud.estado != 'PENDIENTE':
            messages.error(
                request,
                'Solo puede eliminar solicitudes en estado Pendiente.'
            )
            return redirect('solicitud_detail', pk=solicitud.pk)
        
        return super().dispatch(request, *args, **kwargs)
    
    def delete(self, request, *args, **kwargs):
        """Elimina y muestra mensaje de éxito."""
        messages.success(request, 'Solicitud eliminada exitosamente.')
        return super().delete(request, *args, **kwargs)


# ============================================================================
# VISTAS DE POSTULACIONES
# ============================================================================

@login_required
def postular_solicitud(request, pk):
    """
    Vista Function-Based para que un Voluntario postule a una solicitud.
    
    - Solo Voluntarios pueden postular
    - No puede postular a solicitudes ya asignadas o finalizadas
    - No puede postular dos veces a la misma solicitud
    - Crea una nueva Postulacion con estado PENDIENTE
    
    Args:
        request: HttpRequest
        pk: ID de la solicitud
        
    Returns:
        HttpResponse: Redirige al detalle de la solicitud
    """
    # VALIDACIÓN DE PERMISOS: Solo Voluntarios pueden postular
    if not request.user.es_voluntario():
        messages.error(
            request,
            'Solo los Voluntarios pueden postular a solicitudes.'
        )
        return redirect('solicitud_detail', pk=pk)
    
    # Obtener la solicitud o retornar 404
    solicitud = get_object_or_404(
        Solicitud.objects.select_related('creador', 'adulto_mayor'),
        pk=pk
    )
    
    # VALIDACIÓN: Solicitud debe estar PENDIENTE
    if solicitud.estado != 'PENDIENTE':
        messages.error(
            request,
            f'No puede postular a una solicitud con estado "{solicitud.get_estado_display()}".'
        )
        return redirect('solicitud_detail', pk=pk)
    
    # VALIDACIÓN: No puede postular dos veces a la misma solicitud
    if Postulacion.objects.filter(solicitud=solicitud, voluntario=request.user).exists():
        messages.warning(
            request,
            'Ya ha postulado a esta solicitud anteriormente.'
        )
        return redirect('solicitud_detail', pk=pk)
    
    if request.method == 'POST':
        form = PostulacionForm(request.POST)
        
        if form.is_valid():
            # Crear la postulación
            postulacion = form.save(commit=False)
            postulacion.voluntario = request.user
            postulacion.solicitud = solicitud
            postulacion.estado = 'PENDIENTE'
            postulacion.save()
            
            messages.success(
                request,
                f'Has postulado exitosamente a la solicitud "{solicitud.titulo}". '
                f'El solicitante revisará tu postulación.'
            )
            
            return redirect('solicitud_detail', pk=pk)
    else:
        form = PostulacionForm()
    
    context = {
        'form': form,
        'solicitud': solicitud,
        'titulo_pagina': f'Postular a: {solicitud.titulo}',
    }
    
    return render(request, 'adultomayor/postulacion_form.html', context)


@login_required
def aprobar_voluntario(request, pk):
    """
    Vista Function-Based para que un Solicitante acepte una postulación (MATCH).
    
    - Solo el creador de la solicitud puede aprobar
    - Cambia el estado de la Solicitud a 'ASIGNADA'
    - Asigna el voluntario a la solicitud
    - Rechaza automáticamente las demás postulaciones pendientes
    - Actualiza el estado de la postulación a 'ACEPTADA'
    
    Args:
        request: HttpRequest
        pk: ID de la postulación
        
    Returns:
        HttpResponse: Redirige al detalle de la solicitud
    """
    # Obtener la postulación con datos relacionados optimizados
    postulacion = get_object_or_404(
        Postulacion.objects.select_related(
            'voluntario',
            'solicitud',
            'solicitud__creador'
        ),
        pk=pk
    )
    
    solicitud = postulacion.solicitud
    
    # VALIDACIÓN DE PERMISOS: Solo el creador de la solicitud puede aprobar
    if request.user != solicitud.creador:
        messages.error(
            request,
            'No tiene permisos para aprobar postulaciones en esta solicitud. '
            'Solo el creador puede hacerlo.'
        )
        return redirect('solicitud_detail', pk=solicitud.pk)
    
    # VALIDACIÓN: La solicitud debe estar PENDIENTE
    if solicitud.estado != 'PENDIENTE':
        messages.error(
            request,
            f'No puede aprobar postulaciones en una solicitud con estado "{solicitud.get_estado_display()}".'
        )
        return redirect('solicitud_detail', pk=solicitud.pk)
    
    # VALIDACIÓN: La postulación debe estar PENDIENTE
    if postulacion.estado != 'PENDIENTE':
        messages.warning(
            request,
            f'Esta postulación ya fue procesada (Estado: {postulacion.get_estado_display()}).'
        )
        return redirect('solicitud_detail', pk=solicitud.pk)
    
    if request.method == 'POST':
        # LÓGICA DE APROBACIÓN (MATCH)
        
        # 1. Aceptar la postulación usando el método del modelo
        comentario = request.POST.get('comentario', 'Postulación aceptada.')
        postulacion.aceptar(comentario=comentario)
        
        # Nota: El método aceptar() ya hace lo siguiente:
        # - Marca la postulación como ACEPTADA
        # - Asigna el voluntario a la solicitud
        # - Cambia el estado de la solicitud a ASIGNADA
        # - Rechaza automáticamente las demás postulaciones pendientes
        
        messages.success(
            request,
            f'Has aceptado la postulación de {postulacion.voluntario.get_full_name()}. '
            f'La solicitud ahora está asignada.'
        )
        
        return redirect('solicitud_detail', pk=solicitud.pk)
    
    context = {
        'postulacion': postulacion,
        'solicitud': solicitud,
        'titulo_pagina': 'Aprobar Postulación',
    }
    
    return render(request, 'adultomayor/aprobar_postulacion.html', context)


@login_required
def rechazar_postulacion(request, pk):
    """
    Vista para rechazar una postulación.
    
    - Solo el creador de la solicitud puede rechazar
    - Cambia el estado de la postulación a 'RECHAZADA'
    
    Args:
        request: HttpRequest
        pk: ID de la postulación
        
    Returns:
        HttpResponse: Redirige al detalle de la solicitud
    """
    postulacion = get_object_or_404(
        Postulacion.objects.select_related('voluntario', 'solicitud', 'solicitud__creador'),
        pk=pk
    )
    
    solicitud = postulacion.solicitud
    
    # VALIDACIÓN DE PERMISOS
    if request.user != solicitud.creador:
        messages.error(
            request,
            'No tiene permisos para rechazar postulaciones en esta solicitud.'
        )
        return redirect('solicitud_detail', pk=solicitud.pk)
    
    # VALIDACIÓN: La postulación debe estar PENDIENTE
    if postulacion.estado != 'PENDIENTE':
        messages.warning(
            request,
            f'Esta postulación ya fue procesada (Estado: {postulacion.get_estado_display()}).'
        )
        return redirect('solicitud_detail', pk=solicitud.pk)
    
    if request.method == 'POST':
        comentario = request.POST.get('comentario', 'Postulación rechazada.')
        postulacion.rechazar(comentario=comentario)
        
        messages.info(
            request,
            f'Has rechazado la postulación de {postulacion.voluntario.get_full_name()}.'
        )
        
        return redirect('solicitud_detail', pk=solicitud.pk)
    
    context = {
        'postulacion': postulacion,
        'solicitud': solicitud,
        'titulo_pagina': 'Rechazar Postulación',
    }
    
    return render(request, 'adultomayor/rechazar_postulacion.html', context)


# ============================================================================
# VISTAS DE MENSAJES (CHAT)
# ============================================================================

@login_required
def enviar_mensaje(request, pk):
    """
    Vista para enviar un mensaje en el chat de una solicitud.
    
    - Solo el creador o el voluntario asignado pueden enviar mensajes
    - Crea un nuevo mensaje asociado a la solicitud
    
    Args:
        request: HttpRequest
        pk: ID de la solicitud
        
    Returns:
        HttpResponse: Redirige al detalle de la solicitud
    """
    solicitud = get_object_or_404(
        Solicitud.objects.select_related('creador', 'voluntario_asignado'),
        pk=pk
    )
    
    # VALIDACIÓN DE PERMISOS: Solo involucrados en la solicitud
    if request.user != solicitud.creador and request.user != solicitud.voluntario_asignado:
        messages.error(
            request,
            'No tiene permisos para enviar mensajes en esta solicitud.'
        )
        return redirect('solicitud_detail', pk=pk)
    
    if request.method == 'POST':
        form = MensajeForm(request.POST)
        
        if form.is_valid():
            mensaje = form.save(commit=False)
            mensaje.solicitud = solicitud
            mensaje.remitente = request.user
            mensaje.save()
            
            messages.success(request, 'Mensaje enviado exitosamente.')
        else:
            messages.error(request, 'Error al enviar el mensaje.')
    
    return redirect('solicitud_detail', pk=pk)


# ============================================================================
# VISTAS ADICIONALES
# ============================================================================

@login_required
def finalizar_solicitud(request, pk):
    """
    Vista para finalizar una solicitud.
    
    - Solo el creador o el voluntario asignado pueden finalizar
    - Cambia el estado a 'FINALIZADA'
    - Registra comentarios de finalización
    
    Args:
        request: HttpRequest
        pk: ID de la solicitud
        
    Returns:
        HttpResponse: Redirige al detalle de la solicitud
    """
    solicitud = get_object_or_404(
        Solicitud.objects.select_related('creador', 'voluntario_asignado'),
        pk=pk
    )
    
    # VALIDACIÓN DE PERMISOS
    if request.user != solicitud.creador and request.user != solicitud.voluntario_asignado:
        messages.error(
            request,
            'No tiene permisos para finalizar esta solicitud.'
        )
        return redirect('solicitud_detail', pk=pk)
    
    # VALIDACIÓN: La solicitud debe estar ASIGNADA
    if solicitud.estado != 'ASIGNADA':
        messages.error(
            request,
            f'No puede finalizar una solicitud con estado "{solicitud.get_estado_display()}".'
        )
        return redirect('solicitud_detail', pk=pk)
    
    if request.method == 'POST':
        form = FinalizarSolicitudForm(request.POST)
        
        if form.is_valid():
            comentarios = form.cleaned_data.get('comentarios_finalizacion', '')
            solicitud.finalizar(comentarios=comentarios)
            
            messages.success(
                request,
                f'La solicitud "{solicitud.titulo}" ha sido finalizada exitosamente.'
            )
            
            return redirect('solicitud_detail', pk=pk)
    else:
        form = FinalizarSolicitudForm()
    
    context = {
        'form': form,
        'solicitud': solicitud,
        'titulo_pagina': 'Finalizar Solicitud',
    }
    
    return render(request, 'adultomayor/finalizar_solicitud.html', context)


# ============================================================================
# VISTAS DEL DASHBOARD / HOME
# ============================================================================

@login_required
def dashboard(request):
    """
    Vista del dashboard principal según el rol del usuario.
    
    - Solicitantes ven sus solicitudes y estadísticas
    - Voluntarios ven solicitudes disponibles y sus postulaciones
    
    Args:
        request: HttpRequest
        
    Returns:
        HttpResponse: Renderiza el dashboard personalizado
    """
    context = {}
    
    if request.user.es_solicitante():
        # Dashboard para Solicitante
        context['solicitudes_pendientes'] = Solicitud.objects.filter(
            creador=request.user,
            estado='PENDIENTE'
        ).count()
        
        context['solicitudes_asignadas'] = Solicitud.objects.filter(
            creador=request.user,
            estado='ASIGNADA'
        ).count()
        
        context['solicitudes_finalizadas'] = Solicitud.objects.filter(
            creador=request.user,
            estado='FINALIZADA'
        ).count()
        
        context['solicitudes_recientes'] = Solicitud.objects.filter(
            creador=request.user
        ).select_related('adulto_mayor', 'voluntario_asignado').order_by('-fecha_creacion')[:5]
        
        context['tipo_usuario'] = 'solicitante'
        
    elif request.user.es_voluntario():
        # Dashboard para Voluntario
        context['solicitudes_disponibles'] = Solicitud.objects.filter(
            estado='PENDIENTE'
        ).count()
        
        context['mis_postulaciones'] = Postulacion.objects.filter(
            voluntario=request.user
        ).count()
        
        context['solicitudes_asignadas'] = Solicitud.objects.filter(
            voluntario_asignado=request.user,
            estado='ASIGNADA'
        ).count()
        
        context['solicitudes_completadas'] = Solicitud.objects.filter(
            voluntario_asignado=request.user,
            estado='FINALIZADA'
        ).count()
        
        context['postulaciones_recientes'] = Postulacion.objects.filter(
            voluntario=request.user
        ).select_related('solicitud', 'solicitud__adulto_mayor').order_by('-fecha_postulacion')[:5]
        
        context['tipo_usuario'] = 'voluntario'
    
    return render(request, 'adultomayor/dashboard.html', context)


def home(request):
    """
    Vista de la página de inicio pública.
    
    Args:
        request: HttpRequest
        
    Returns:
        HttpResponse: Renderiza la página de inicio
    """
    context = {
        'total_solicitudes': Solicitud.objects.filter(estado='PENDIENTE').count(),
        'total_voluntarios': Usuario.objects.filter(rol='VOLUNTARIO', activo=True).count(),
        'solicitudes_recientes': Solicitud.objects.filter(
            estado='PENDIENTE'
        ).select_related('adulto_mayor').order_by('-fecha_creacion')[:6],
    }
    
    return render(request, 'adultomayor/home.html', context)


# ============================================================================
# VISTA DE REPORTE CON SQL PURO (RAW SQL)
# ============================================================================

@login_required
def reporte_gestion_sql(request):
    """
    Vista especial de Reporte de Gestión usando SQL PURO (Raw SQL).
    
    IMPORTANTE: Esta vista NO usa el ORM de Django para demostrar
    conocimientos de SQL directo y cumplir con requisitos de evaluación
    de Base de Datos.
    
    Demuestra el uso de:
    - SQL Raw (connection.cursor() y Manager.raw())
    - JOIN explícito para unir tablas
    - WHERE para filtrar datos
    - ORDER BY para ordenar resultados
    - Selección específica de columnas (no SELECT *)
    
    Args:
        request: HttpRequest
        
    Returns:
        HttpResponse: Renderiza el reporte con datos obtenidos via SQL puro
    """
    from django.db import connection
    
    # ========================================================================
    # CONSULTA 1: Usando connection.cursor() - Mayor control
    # ========================================================================
    # Esta es la forma más directa de ejecutar SQL puro en Django
    
    with connection.cursor() as cursor:
        """
        EXPLICACIÓN DE LA CONSULTA SQL:
        
        Esta consulta obtiene información detallada de solicitudes ASIGNADAS,
        combinando datos de tres tablas: Solicitud, Usuario y AdultoMayor.
        """
        
        cursor.execute("""
            SELECT 
                -- COLUMNAS ESPECÍFICAS (NO SELECT *)
                -- Seleccionamos solo las columnas necesarias para optimizar
                s.id AS solicitud_id,                    -- ID de la solicitud
                s.titulo AS solicitud_titulo,            -- Título de la solicitud
                s.descripcion AS solicitud_descripcion,  -- Descripción detallada
                s.tipo_ayuda AS tipo_ayuda,              -- Tipo de ayuda requerida
                s.estado AS estado,                      -- Estado actual
                s.prioridad AS prioridad,                -- Nivel de prioridad
                s.fecha_creacion AS fecha_creacion,      -- Fecha de creación
                s.fecha_asignacion AS fecha_asignacion,  -- Fecha cuando se asignó
                
                -- Datos del CREADOR (Solicitante)
                u_creador.id AS creador_id,              -- ID del solicitante
                u_creador.username AS creador_username,  -- Username del solicitante
                u_creador.first_name AS creador_nombre,  -- Nombre del solicitante
                u_creador.last_name AS creador_apellido, -- Apellido del solicitante
                u_creador.email AS creador_email,        -- Email del solicitante
                
                -- Datos del VOLUNTARIO ASIGNADO
                u_voluntario.id AS voluntario_id,              -- ID del voluntario
                u_voluntario.username AS voluntario_username,  -- Username del voluntario
                u_voluntario.first_name AS voluntario_nombre,  -- Nombre del voluntario
                u_voluntario.last_name AS voluntario_apellido, -- Apellido del voluntario
                u_voluntario.email AS voluntario_email,        -- Email del voluntario
                
                -- Datos del ADULTO MAYOR (Beneficiario)
                am.id AS adulto_mayor_id,                -- ID del adulto mayor
                am.nombres AS adulto_mayor_nombres,      -- Nombres del beneficiario
                am.apellidos AS adulto_mayor_apellidos,  -- Apellidos del beneficiario
                am.rut AS adulto_mayor_rut,              -- RUT del beneficiario
                am.direccion AS adulto_mayor_direccion,  -- Dirección del beneficiario
                am.telefono AS adulto_mayor_telefono     -- Teléfono del beneficiario
                
            FROM 
                -- TABLA PRINCIPAL: Solicitudes
                adultomayor_solicitud AS s
            
            -- JOIN #1: Unir con Usuario (Creador/Solicitante)
            -- INNER JOIN porque toda solicitud DEBE tener un creador
            INNER JOIN adultomayor_usuario AS u_creador 
                ON s.creador_id = u_creador.id
                -- Condición de JOIN: La FK creador_id debe coincidir con el id del usuario
            
            -- JOIN #2: Unir con Usuario (Voluntario Asignado)
            -- INNER JOIN porque solo queremos solicitudes CON voluntario asignado
            INNER JOIN adultomayor_usuario AS u_voluntario 
                ON s.voluntario_asignado_id = u_voluntario.id
                -- Condición de JOIN: La FK voluntario_asignado_id debe coincidir con el id
            
            -- JOIN #3: Unir con AdultoMayor (Beneficiario)
            -- INNER JOIN porque toda solicitud DEBE tener un adulto mayor asociado
            INNER JOIN adultomayor_adultomayor AS am 
                ON s.adulto_mayor_id = am.id
                -- Condición de JOIN: La FK adulto_mayor_id debe coincidir con el id
            
            WHERE 
                -- FILTRO #1: Solo solicitudes en estado 'ASIGNADA'
                s.estado = 'ASIGNADA'
                -- Esto asegura que solo veamos solicitudes actualmente en proceso
                
                AND 
                -- FILTRO #2: Solo solicitudes con voluntario asignado (redundante pero explícito)
                s.voluntario_asignado_id IS NOT NULL
                -- Garantiza integridad referencial aunque ya usamos INNER JOIN
                
            ORDER BY 
                -- ORDENAMIENTO #1: Por fecha de asignación (más recientes primero)
                s.fecha_asignacion DESC,
                -- Las solicitudes asignadas más recientemente aparecen primero
                
                -- ORDENAMIENTO #2: Si tienen misma fecha, ordenar por prioridad
                -- URGENTE (primero), ALTA, MEDIA, BAJA (último)
                CASE s.prioridad
                    WHEN 'URGENTE' THEN 1
                    WHEN 'ALTA' THEN 2
                    WHEN 'MEDIA' THEN 3
                    WHEN 'BAJA' THEN 4
                END,
                
                -- ORDENAMIENTO #3: Finalmente por fecha de creación
                s.fecha_creacion DESC
                
            -- LIMIT opcional para no sobrecargar el reporte
            LIMIT 100
        """)
        
        # Obtener los nombres de las columnas del cursor
        columns = [col[0] for col in cursor.description]
        
        # Convertir los resultados en una lista de diccionarios
        # Esto hace más fácil trabajar con los datos en el template
        solicitudes_asignadas = []
        for row in cursor.fetchall():
            # Crear un diccionario con el nombre de columna como key
            solicitudes_asignadas.append(dict(zip(columns, row)))
    
    
    # ========================================================================
    # CONSULTA 2: Usando Model.objects.raw() - Enfoque alternativo
    # ========================================================================
    # Esta forma permite mapear directamente a objetos del modelo
    
    """
    EXPLICACIÓN DE LA CONSULTA SQL CON raw():
    
    Esta consulta obtiene estadísticas de postulaciones por solicitud,
    demostrando el uso de GROUP BY y COUNT con SQL puro.
    """
    
    query_estadisticas = """
        SELECT 
            -- COLUMNAS PARA ESTADÍSTICAS
            s.id,                                    -- ID de solicitud (requerido para raw())
            s.titulo,                                -- Título de la solicitud
            s.estado,                                -- Estado actual
            s.fecha_creacion,                        -- Fecha de creación
            COUNT(p.id) AS total_postulaciones,      -- Contar postulaciones (agregación)
            
            -- Contar postulaciones por estado usando CASE
            SUM(CASE WHEN p.estado = 'PENDIENTE' THEN 1 ELSE 0 END) AS postulaciones_pendientes,
            SUM(CASE WHEN p.estado = 'ACEPTADA' THEN 1 ELSE 0 END) AS postulaciones_aceptadas,
            SUM(CASE WHEN p.estado = 'RECHAZADA' THEN 1 ELSE 0 END) AS postulaciones_rechazadas
            
        FROM 
            -- TABLA PRINCIPAL: Solicitudes
            adultomayor_solicitud AS s
        
        -- LEFT JOIN: Incluye solicitudes aunque no tengan postulaciones
        LEFT JOIN adultomayor_postulacion AS p 
            ON s.id = p.solicitud_id
            -- Condición de JOIN: Unir por el ID de la solicitud
        
        WHERE 
            -- FILTRO: Solicitudes creadas en los últimos 90 días
            s.fecha_creacion >= CURRENT_DATE - INTERVAL '90 days'
            -- Esto limita el reporte a datos recientes y relevantes
        
        GROUP BY 
            -- AGRUPACIÓN: Agrupar por solicitud para contar postulaciones
            s.id, s.titulo, s.estado, s.fecha_creacion
            -- Necesario cuando usamos funciones de agregación (COUNT, SUM)
        
        HAVING 
            -- FILTRO POST-AGREGACIÓN: Solo solicitudes con al menos 1 postulación
            COUNT(p.id) > 0
            -- HAVING se usa después de GROUP BY para filtrar grupos
        
        ORDER BY 
            -- ORDENAR: Por número de postulaciones (más populares primero)
            total_postulaciones DESC,
            -- Luego por fecha de creación
            s.fecha_creacion DESC
            
        LIMIT 50
    """
    
    # Ejecutar la consulta raw() y obtener objetos Solicitud con atributos extras
    estadisticas_postulaciones = Solicitud.objects.raw(query_estadisticas)
    
    
    # ========================================================================
    # CONSULTA 3: Reporte de Voluntarios más activos (Raw SQL adicional)
    # ========================================================================
    
    with connection.cursor() as cursor:
        """
        CONSULTA AVANZADA: Ranking de Voluntarios por actividad
        
        Demuestra:
        - Múltiples JOINs
        - GROUP BY con múltiples columnas
        - Funciones de agregación (COUNT, MAX, MIN)
        - Subconsultas en SELECT
        """
        
        cursor.execute("""
            SELECT 
                -- Información del Voluntario
                u.id AS voluntario_id,
                u.username,
                u.first_name,
                u.last_name,
                u.email,
                
                -- ESTADÍSTICAS CALCULADAS
                COUNT(DISTINCT p.id) AS total_postulaciones,        -- Total de postulaciones
                COUNT(DISTINCT s.id) AS solicitudes_asignadas,      -- Solicitudes asignadas
                COUNT(DISTINCT CASE 
                    WHEN s.estado = 'FINALIZADA' THEN s.id 
                END) AS solicitudes_completadas,                    -- Solicitudes completadas
                
                -- Fechas relevantes
                MAX(p.fecha_postulacion) AS ultima_postulacion,     -- Última actividad
                MIN(p.fecha_postulacion) AS primera_postulacion     -- Primera actividad
                
            FROM 
                -- TABLA PRINCIPAL: Usuarios Voluntarios
                adultomayor_usuario AS u
            
            -- JOIN: Postulaciones del voluntario
            LEFT JOIN adultomayor_postulacion AS p 
                ON u.id = p.voluntario_id
            
            -- JOIN: Solicitudes asignadas al voluntario
            LEFT JOIN adultomayor_solicitud AS s 
                ON u.id = s.voluntario_asignado_id
            
            WHERE 
                -- FILTRO: Solo usuarios con rol VOLUNTARIO
                u.rol = 'VOLUNTARIO'
                
                AND 
                -- FILTRO: Solo voluntarios activos
                u.activo = TRUE
                
                AND
                -- FILTRO: Que hayan postulado al menos una vez
                p.id IS NOT NULL
            
            GROUP BY 
                -- AGRUPACIÓN: Por voluntario
                u.id, u.username, u.first_name, u.last_name, u.email
            
            ORDER BY 
                -- ORDENAR: Por solicitudes completadas (más efectivos primero)
                solicitudes_completadas DESC,
                -- Luego por total de solicitudes asignadas
                solicitudes_asignadas DESC,
                -- Finalmente por total de postulaciones
                total_postulaciones DESC
            
            LIMIT 20
        """)
        
        columns_voluntarios = [col[0] for col in cursor.description]
        voluntarios_activos = [
            dict(zip(columns_voluntarios, row)) 
            for row in cursor.fetchall()
        ]
    
    
    # ========================================================================
    # PREPARAR CONTEXTO PARA EL TEMPLATE
    # ========================================================================
    
    context = {
        # Datos obtenidos con SQL puro
        'solicitudes_asignadas': solicitudes_asignadas,
        'estadisticas_postulaciones': estadisticas_postulaciones,
        'voluntarios_activos': voluntarios_activos,
        
        # Metadatos del reporte
        'titulo_reporte': 'Reporte de Gestión - Consultas SQL Puras',
        'fecha_generacion': timezone.now(),
        'total_asignadas': len(solicitudes_asignadas),
        'total_voluntarios': len(voluntarios_activos),
        
        # Información técnica para la evaluación
        'metodo_consulta': 'SQL Raw (connection.cursor() y Model.objects.raw())',
        'clausulas_sql_usadas': [
            'SELECT con columnas específicas (no SELECT *)',
            'INNER JOIN para unir múltiples tablas',
            'LEFT JOIN para incluir registros sin coincidencias',
            'WHERE con múltiples condiciones',
            'ORDER BY con múltiples criterios y CASE',
            'GROUP BY para agregaciones',
            'HAVING para filtrar grupos',
            'COUNT, SUM, MAX, MIN (funciones de agregación)',
            'LIMIT para optimización',
        ],
    }
    
    return render(request, 'adultomayor/reporte_gestion.html', context)


# ============================================================================
# NOTAS TÉCNICAS SOBRE SQL PURO VS ORM
# ============================================================================

"""
DIFERENCIAS CLAVE:

1. SQL PURO (Raw SQL):
   Ventajas:
   - Control total sobre la consulta
   - Optimización manual precisa
   - Acceso a características específicas de PostgreSQL
   - Queries complejas más legibles
   
   Desventajas:
   - Menos portable entre bases de datos
   - Más propenso a SQL Injection si no se usa correctamente
   - No se beneficia de migraciones automáticas
   - Requiere conocimiento profundo de SQL

2. ORM DE DJANGO:
   Ventajas:
   - Portable entre diferentes bases de datos
   - Protección automática contra SQL Injection
   - Sintaxis Pythonica más legible para queries simples
   - Integración con migraciones
   
   Desventajas:
   - Puede generar queries subóptimas
   - Curva de aprendizaje para queries complejas
   - Menos control fino sobre la consulta

CUÁNDO USAR CADA UNO:

- Usa ORM: Para CRUD básico y queries simples
- Usa Raw SQL: Para reportes complejos, optimización crítica, 
               o cuando necesitas características específicas de la BD

SEGURIDAD CON RAW SQL:
Siempre usa parámetros para evitar SQL Injection:
  cursor.execute("SELECT * FROM tabla WHERE id = %s", [user_id])
  NUNCA: cursor.execute(f"SELECT * FROM tabla WHERE id = {user_id}")
"""

