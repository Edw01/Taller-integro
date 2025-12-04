from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import datetime
from .models import AdultoMayor

# Create your views here.

def home(request):
    """Vista principal del dashboard"""
    adultos = AdultoMayor.objects.all()
    activos = adultos.filter(activo=True).count()
    
    # Registros del mes actual
    mes_actual = datetime.now().month
    año_actual = datetime.now().year
    registros_mes = adultos.filter(
        fecha_registro__month=mes_actual,
        fecha_registro__year=año_actual
    ).count()
    
    # Promedio de edad
    edades = [adulto.edad() for adulto in adultos]
    promedio_edad = round(sum(edades) / len(edades)) if edades else 0
    
    # Últimos 5 registros
    ultimos_registros = adultos.order_by('-fecha_registro')[:5]
    
    context = {
        'total_adultos': adultos.count(),
        'activos': activos,
        'registros_mes': registros_mes,
        'promedio_edad': promedio_edad,
        'ultimos_registros': ultimos_registros,
    }
    return render(request, 'index.html', context)

def adultomayor_list(request):
    """Vista de listado con filtros"""
    adultos = AdultoMayor.objects.all()
    
    # Búsqueda
    search = request.GET.get('search', '')
    if search:
        adultos = adultos.filter(
            nombre__icontains=search
        ) | adultos.filter(
            apellido__icontains=search
        ) | adultos.filter(
            rut__icontains=search
        )
    
    # Filtro por estado
    estado = request.GET.get('estado', '')
    if estado == 'activo':
        adultos = adultos.filter(activo=True)
    elif estado == 'inactivo':
        adultos = adultos.filter(activo=False)
    
    # Ordenamiento
    order = request.GET.get('order', 'apellido')
    adultos = adultos.order_by(order)
    
    context = {
        'adultos': adultos,
    }
    return render(request, 'adultomayor/list.html', context)

def adultomayor_detail(request, pk):
    """Vista de detalle"""
    adulto = get_object_or_404(AdultoMayor, pk=pk)
    context = {
        'adulto': adulto,
    }
    return render(request, 'adultomayor/detail.html', context)

def adultomayor_create(request):
    """Vista para crear nuevo adulto mayor"""
    if request.method == 'POST':
        try:
            adulto = AdultoMayor(
                nombre=request.POST.get('nombre'),
                apellido=request.POST.get('apellido'),
                rut=request.POST.get('rut'),
                fecha_nacimiento=request.POST.get('fecha_nacimiento'),
                telefono=request.POST.get('telefono', ''),
                direccion=request.POST.get('direccion', ''),
                email=request.POST.get('email', ''),
                contacto_emergencia=request.POST.get('contacto_emergencia', ''),
                telefono_emergencia=request.POST.get('telefono_emergencia', ''),
                activo=request.POST.get('activo') == 'on',
            )
            adulto.save()
            messages.success(request, f'Adulto mayor {adulto.nombre} {adulto.apellido} registrado exitosamente.')
            return redirect('adultomayor_detail', pk=adulto.pk)
        except Exception as e:
            messages.error(request, f'Error al registrar: {str(e)}')
    
    context = {
        'form': {'instance': AdultoMayor()},
    }
    return render(request, 'adultomayor/form.html', context)

def adultomayor_update(request, pk):
    """Vista para editar adulto mayor"""
    adulto = get_object_or_404(AdultoMayor, pk=pk)
    
    if request.method == 'POST':
        try:
            adulto.nombre = request.POST.get('nombre')
            adulto.apellido = request.POST.get('apellido')
            adulto.rut = request.POST.get('rut')
            adulto.fecha_nacimiento = request.POST.get('fecha_nacimiento')
            adulto.telefono = request.POST.get('telefono', '')
            adulto.direccion = request.POST.get('direccion', '')
            adulto.email = request.POST.get('email', '')
            adulto.contacto_emergencia = request.POST.get('contacto_emergencia', '')
            adulto.telefono_emergencia = request.POST.get('telefono_emergencia', '')
            adulto.activo = request.POST.get('activo') == 'on'
            adulto.save()
            messages.success(request, f'Datos de {adulto.nombre} {adulto.apellido} actualizados exitosamente.')
            return redirect('adultomayor_detail', pk=adulto.pk)
        except Exception as e:
            messages.error(request, f'Error al actualizar: {str(e)}')
    
    context = {
        'form': {'instance': adulto},
    }
    return render(request, 'adultomayor/form.html', context)

def adultomayor_delete(request, pk):
    """Vista para eliminar adulto mayor"""
    adulto = get_object_or_404(AdultoMayor, pk=pk)
    
    if request.method == 'POST':
        nombre_completo = f'{adulto.nombre} {adulto.apellido}'
        adulto.delete()
        messages.success(request, f'Registro de {nombre_completo} eliminado exitosamente.')
        return redirect('adultomayor_list')
    
    context = {
        'adulto': adulto,
    }
    return render(request, 'adultomayor/confirm_delete.html', context)
