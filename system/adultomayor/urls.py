"""
URLs de la aplicación VoluntariadoMayor.

Este módulo define todas las rutas (URLs) de la aplicación y las mapea
a sus respectivas vistas.
"""

from django.urls import path
from . import views

# Namespace de la aplicación para evitar conflictos de nombres
app_name = 'adultomayor'

urlpatterns = [
    # ========================================================================
    # URLS GENERALES
    # ========================================================================
    
    # Página de inicio
    path('', views.home, name='home'),
    
    # Dashboard personalizado según rol
    path('dashboard/', views.dashboard, name='dashboard'),
    
    
    # ========================================================================
    # URLS DE SOLICITUDES
    # ========================================================================
    
    # Listar todas las solicitudes (filtradas según rol)
    path('solicitudes/', views.SolicitudListView.as_view(), name='solicitud_list'),
    
    # Ver detalle de una solicitud específica
    path('solicitudes/<int:pk>/', views.SolicitudDetailView.as_view(), name='solicitud_detail'),
    
    # Crear nueva solicitud (solo Solicitantes)
    # Usando Function-Based View
    path('solicitudes/crear/', views.crear_solicitud, name='solicitud_create'),
    
    # Alternativa usando Class-Based View (comentada, descomentar si prefiere CBV)
    # path('solicitudes/crear/', views.SolicitudCreateView.as_view(), name='solicitud_create'),
    
    # Editar solicitud existente (solo creador)
    path('solicitudes/<int:pk>/editar/', views.SolicitudUpdateView.as_view(), name='solicitud_update'),
    
    # Eliminar solicitud (solo creador y si está pendiente)
    path('solicitudes/<int:pk>/eliminar/', views.SolicitudDeleteView.as_view(), name='solicitud_delete'),
    
    # Finalizar solicitud
    path('solicitudes/<int:pk>/finalizar/', views.finalizar_solicitud, name='solicitud_finalizar'),
    
    
    # ========================================================================
    # URLS DE POSTULACIONES
    # ========================================================================
    
    # Postular a una solicitud (solo Voluntarios)
    path('solicitudes/<int:pk>/postular/', views.postular_solicitud, name='postular_solicitud'),
    
    # Aprobar una postulación - MATCH (solo creador de la solicitud)
    path('postulaciones/<int:pk>/aprobar/', views.aprobar_voluntario, name='aprobar_postulacion'),
    
    # Rechazar una postulación (solo creador de la solicitud)
    path('postulaciones/<int:pk>/rechazar/', views.rechazar_postulacion, name='rechazar_postulacion'),
    
    
    # ========================================================================
    # URLS DE MENSAJES (CHAT)
    # ========================================================================
    
    # Enviar mensaje en una solicitud
    path('solicitudes/<int:pk>/mensaje/', views.enviar_mensaje, name='enviar_mensaje'),
    
    
    # ========================================================================
    # URLS DE REPORTES
    # ========================================================================
    
    # Reporte de gestión con SQL puro (para evaluación de Base de Datos)
    path('reporte/gestion/', views.reporte_gestion_sql, name='reporte_gestion'),
]
