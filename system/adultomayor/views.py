from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import connection
from .models import Solicitud, Profile
from .forms import UserRegisterForm, SolicitudForm

def index(request):
    return render(request, 'index.html')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})

@login_required
def solicitudes_list(request):
    # Logica para manejar acciones POST
    if request.method == 'POST':
        if 'crear_solicitud' in request.POST:
            form = SolicitudForm(request.POST)
            if form.is_valid():
                solicitud = form.save(commit=False)
                solicitud.presidente = request.user
                solicitud.save()
                return redirect('solicitudes_list')
        
        elif 'ser_voluntario' in request.POST:
            solicitud_id = request.POST.get('solicitud_id')
            solicitud = get_object_or_404(Solicitud, id=solicitud_id)
            if request.user.profile.rol == 'VOLUNTARIO':
                if solicitud.voluntarios.count() < solicitud.cantidad_voluntarios:
                    solicitud.voluntarios.add(request.user)
                    if solicitud.voluntarios.count() >= solicitud.cantidad_voluntarios:
                        solicitud.estado = 'ASIGNADA'
                        solicitud.save()
                return redirect('solicitudes_list')

        elif 'solicitar_ayuda' in request.POST:
            solicitud_id = request.POST.get('solicitud_id')
            solicitud = get_object_or_404(Solicitud, id=solicitud_id)
            if request.user.profile.rol == 'ADULTO_MAYOR':
                if solicitud.adultos_mayores.count() < solicitud.cantidad_beneficiarios:
                    solicitud.adultos_mayores.add(request.user)
                return redirect('solicitudes_list')

        elif 'finalizar_solicitud' in request.POST:
            solicitud_id = request.POST.get('solicitud_id')
            solicitud = get_object_or_404(Solicitud, id=solicitud_id)
            if solicitud.presidente == request.user:
                solicitud.estado = 'FINALIZADA'
                solicitud.save()
                return redirect('solicitudes_list')

        elif 'eliminar_solicitud' in request.POST:
            solicitud_id = request.POST.get('solicitud_id')
            solicitud = get_object_or_404(Solicitud, id=solicitud_id)
            if solicitud.presidente == request.user:
                solicitud.delete()
                return redirect('solicitudes_list')

    # Consulta ORM (Optimized for Rubric: Eficiencia en sentencias repetitivas)
    solicitudes = Solicitud.objects.select_related('presidente').prefetch_related('voluntarios', 'adultos_mayores').order_by('-created_at')

    # Consulta SQL Manual
    # Contamos cuantas solicitudes hay disponibles usando SQL directo
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM adultomayor_solicitud WHERE estado = 'DISPONIBLE'")
        row = cursor.fetchone()
        count_disponibles = row[0]

        # Consulta SQL Manual con el JOIN (Lo de rubrica basicamente)
        cursor.execute("""
            SELECT s.titulo, u.first_name, u.last_name 
            FROM adultomayor_solicitud s
            INNER JOIN auth_user u ON s.presidente_id = u.id
            ORDER BY s.created_at DESC
        """)
        solicitudes_reporte_sql = cursor.fetchall()

    form = SolicitudForm()
    
    return render(request, 'solicitudes_list.html', {
        'solicitudes': solicitudes,
        'form': form,
        'count_disponibles': count_disponibles,
        'solicitudes_reporte_sql': solicitudes_reporte_sql
    })

@login_required
def eliminar_cuenta(request):
    if request.method == 'POST':
        user = request.user
        user.delete()
        return redirect('index')
    return render(request, 'confirmar_eliminar_cuenta.html')
