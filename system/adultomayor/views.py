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
            if not solicitud.voluntario and request.user.profile.rol == 'VOLUNTARIO':
                solicitud.voluntario = request.user
                solicitud.save()
                return redirect('solicitudes_list')

        elif 'solicitar_ayuda' in request.POST:
            solicitud_id = request.POST.get('solicitud_id')
            solicitud = get_object_or_404(Solicitud, id=solicitud_id)
            if not solicitud.adulto_mayor and request.user.profile.rol == 'ADULTO_MAYOR':
                solicitud.adulto_mayor = request.user
                solicitud.save()
                return redirect('solicitudes_list')

    # Consulta ORM (Rubrica 18)
    solicitudes = Solicitud.objects.all().order_by('-created_at')

    # Consulta SQL Manual (Rubrica 16)
    # Contamos cuantas solicitudes hay disponibles usando SQL directo
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM adultomayor_solicitud WHERE estado = 'DISPONIBLE'")
        row = cursor.fetchone()
        count_disponibles = row[0]

    form = SolicitudForm()
    
    return render(request, 'solicitudes_list.html', {
        'solicitudes': solicitudes,
        'form': form,
        'count_disponibles': count_disponibles
    })
