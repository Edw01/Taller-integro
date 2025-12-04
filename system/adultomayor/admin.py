from django.contrib import admin
from .models import AdultoMayor

# Register your models here.

@admin.register(AdultoMayor)
class AdultoMayorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'apellido', 'rut', 'edad', 'telefono', 'activo', 'fecha_registro']
    list_filter = ['activo', 'fecha_registro']
    search_fields = ['nombre', 'apellido', 'rut']
    list_per_page = 20
