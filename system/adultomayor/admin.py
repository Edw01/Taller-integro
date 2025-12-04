from django.contrib import admin
from .models import Profile, Solicitud

# Register your models here.

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'rut', 'rol')
    search_fields = ('user__username', 'rut')
    list_filter = ('rol',)

@admin.register(Solicitud)
class SolicitudAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'presidente', 'voluntario', 'adulto_mayor', 'estado', 'created_at')
    list_filter = ('estado', 'created_at')
    search_fields = ('titulo', 'descripcion', 'presidente__username')
