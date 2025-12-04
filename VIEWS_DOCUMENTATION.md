# Documentación Técnica - Views de VoluntariadoMayor

## Descripción General

El archivo `views.py` contiene toda la lógica de negocio de la aplicación VoluntariadoMayor. Implementa vistas utilizando tanto **Function-Based Views (FBV)** como **Class-Based Views (CBV)** de Django, demostrando diferentes enfoques profesionales.

---

## 🔐 Sistema de Permisos (Mixins Personalizados)

### SolicitanteRequiredMixin
- **Propósito**: Restringe acceso solo a usuarios con rol SOLICITANTE
- **Uso**: Decorador para Class-Based Views
- **Hereda de**: `UserPassesTestMixin`

### VoluntarioRequiredMixin
- **Propósito**: Restringe acceso solo a usuarios con rol VOLUNTARIO
- **Uso**: Decorador para Class-Based Views
- **Hereda de**: `UserPassesTestMixin`

### SolicitudOwnerRequiredMixin
- **Propósito**: Verifica que el usuario sea el creador de la solicitud
- **Uso**: Protege edición y eliminación de solicitudes
- **Hereda de**: `UserPassesTestMixin`

---

## 📋 Vistas de Solicitudes

### 1. SolicitudListView (CBV - ListView)
**Ruta**: `/solicitudes/`  
**Método HTTP**: GET  
**Acceso**: Público  

**Funcionalidad**:
- Lista todas las solicitudes con filtrado inteligente según el rol
- **Voluntarios**: Ven solo solicitudes PENDIENTES
- **Solicitantes**: Ven solo SUS propias solicitudes
- **Usuarios no autenticados**: Ven solicitudes PENDIENTES

**Optimizaciones ORM**:
```python
queryset = Solicitud.objects.select_related(
    'creador',           # JOIN con Usuario creador
    'adulto_mayor',      # JOIN con AdultoMayor
    'voluntario_asignado'  # JOIN con Usuario voluntario
).prefetch_related(
    'postulaciones'      # Prefetch de postulaciones
).annotate(
    num_postulaciones=Count('postulaciones')  # Cuenta postulaciones
)
```

**¿Por qué select_related?**
- Evita el problema N+1 queries
- Realiza JOINs en SQL en lugar de consultas separadas
- Reduce dramáticamente el número de queries a la base de datos

**Filtros Disponibles**:
- Búsqueda por texto (título, descripción, tipo_ayuda)
- Filtro por prioridad

---

### 2. SolicitudDetailView (CBV - DetailView)
**Ruta**: `/solicitudes/<pk>/`  
**Método HTTP**: GET  
**Acceso**: Público  

**Funcionalidad**:
- Muestra detalle completo de una solicitud
- Incluye postulaciones si el usuario es el creador
- Incluye chat si hay voluntario asignado
- Usa Prefetch para optimizar queries relacionadas

**Optimización con Prefetch**:
```python
Prefetch(
    'postulaciones',
    queryset=Postulacion.objects.select_related('voluntario')
)
```

---

### 3. crear_solicitud (FBV - Function-Based View)
**Ruta**: `/solicitudes/crear/`  
**Método HTTP**: GET, POST  
**Acceso**: `@login_required` + Validación manual de rol SOLICITANTE  

**Funcionalidad**:
- Permite a Solicitantes crear nuevas solicitudes
- Asigna automáticamente el creador (request.user)
- Establece estado inicial como PENDIENTE

**Validaciones**:
1. Usuario debe estar autenticado (`@login_required`)
2. Usuario debe tener rol SOLICITANTE
3. Formulario debe ser válido

**Flujo de Ejecución**:
```
1. Verificar permisos (es_solicitante)
2. Si POST → Validar formulario
3. Guardar con commit=False
4. Asignar creador = request.user
5. Guardar en BD
6. Redirect a detalle
```

---

### 4. SolicitudCreateView (CBV - CreateView) [Alternativa]
**Ruta**: `/solicitudes/crear/` (comentada en urls.py)  
**Acceso**: `LoginRequiredMixin` + `SolicitanteRequiredMixin`  

**Diferencia con FBV**:
- Más concisa pero menos explícita
- Usa mixins para validación de permisos
- Misma funcionalidad que la FBV

---

### 5. SolicitudUpdateView (CBV - UpdateView)
**Ruta**: `/solicitudes/<pk>/editar/`  
**Método HTTP**: GET, POST  
**Acceso**: `LoginRequiredMixin` + `SolicitudOwnerRequiredMixin`  

**Validaciones**:
1. Usuario debe ser el creador
2. Solicitud debe estar en estado PENDIENTE
3. No se puede editar si está ASIGNADA o FINALIZADA

---

### 6. SolicitudDeleteView (CBV - DeleteView)
**Ruta**: `/solicitudes/<pk>/eliminar/`  
**Método HTTP**: GET, POST  
**Acceso**: `LoginRequiredMixin` + `SolicitudOwnerRequiredMixin`  

**Validaciones**:
1. Usuario debe ser el creador
2. Solo se puede eliminar si está PENDIENTE

---

## 🤝 Vistas de Postulaciones

### 7. postular_solicitud (FBV)
**Ruta**: `/solicitudes/<pk>/postular/`  
**Método HTTP**: GET, POST  
**Acceso**: `@login_required` + Validación VOLUNTARIO  

**Funcionalidad**:
- Permite a Voluntarios postular a solicitudes
- Crea objeto Postulacion con estado PENDIENTE

**Validaciones Estrictas**:
1. Usuario debe ser VOLUNTARIO
2. Solicitud debe estar PENDIENTE
3. No puede postular dos veces a la misma solicitud (validación de duplicado)

**Query de Validación**:
```python
if Postulacion.objects.filter(
    solicitud=solicitud, 
    voluntario=request.user
).exists():
    # Ya postulaste
```

---

### 8. aprobar_voluntario (FBV) - **MATCH**
**Ruta**: `/postulaciones/<pk>/aprobar/`  
**Método HTTP**: GET, POST  
**Acceso**: `@login_required` + Validación de ownership  

**Funcionalidad - LÓGICA CRÍTICA DEL MATCH**:
1. Acepta la postulación seleccionada
2. Asigna el voluntario a la solicitud
3. Cambia estado de Solicitud a ASIGNADA
4. Rechaza automáticamente todas las demás postulaciones pendientes

**Optimización con select_related**:
```python
postulacion = get_object_or_404(
    Postulacion.objects.select_related(
        'voluntario',
        'solicitud',
        'solicitud__creador'
    ),
    pk=pk
)
```

**Validaciones**:
1. Usuario debe ser el creador de la solicitud
2. Solicitud debe estar PENDIENTE
3. Postulación debe estar PENDIENTE

**Uso del Método del Modelo**:
```python
postulacion.aceptar(comentario=comentario)
# Este método encapsula toda la lógica del match
```

---

### 9. rechazar_postulacion (FBV)
**Ruta**: `/postulaciones/<pk>/rechazar/`  
**Método HTTP**: GET, POST  
**Acceso**: `@login_required` + Validación de ownership  

**Funcionalidad**:
- Rechaza una postulación específica
- No afecta otras postulaciones
- Solicitud permanece PENDIENTE

---

## 💬 Vistas de Mensajes (Chat)

### 10. enviar_mensaje (FBV)
**Ruta**: `/solicitudes/<pk>/mensaje/`  
**Método HTTP**: POST  
**Acceso**: `@login_required` + Validación de participación  

**Funcionalidad**:
- Permite comunicación entre Solicitante y Voluntario
- Solo usuarios involucrados en la solicitud pueden enviar mensajes

**Validación de Permisos**:
```python
if request.user != solicitud.creador and 
   request.user != solicitud.voluntario_asignado:
    # No autorizado
```

---

## ✅ Vista de Finalización

### 11. finalizar_solicitud (FBV)
**Ruta**: `/solicitudes/<pk>/finalizar/`  
**Método HTTP**: GET, POST  
**Acceso**: `@login_required` + Validación  

**Funcionalidad**:
- Marca solicitud como FINALIZADA
- Registra comentarios de finalización
- Solo creador o voluntario asignado pueden finalizar

**Validaciones**:
1. Usuario debe estar involucrado (creador o voluntario)
2. Solicitud debe estar ASIGNADA

---

## 📊 Vistas de Dashboard

### 12. dashboard (FBV)
**Ruta**: `/dashboard/`  
**Método HTTP**: GET  
**Acceso**: `@login_required`  

**Funcionalidad**:
- Dashboard personalizado según rol del usuario
- **Para Solicitantes**:
  - Contador de solicitudes por estado
  - Lista de solicitudes recientes
- **Para Voluntarios**:
  - Solicitudes disponibles
  - Mis postulaciones
  - Solicitudes asignadas y completadas

---

### 13. home (FBV)
**Ruta**: `/`  
**Método HTTP**: GET  
**Acceso**: Público  

**Funcionalidad**:
- Página de inicio pública
- Muestra estadísticas generales
- Lista solicitudes pendientes recientes

---

## 🎯 Conceptos Clave Implementados

### 1. Optimización con ORM
- **select_related()**: Para relaciones ForeignKey (1-to-1, Many-to-1)
- **prefetch_related()**: Para relaciones Many-to-Many y reverse ForeignKey
- **annotate()**: Para agregar campos calculados (COUNT, SUM, etc.)

### 2. Validación de Permisos
- Decorador `@login_required` para FBV
- Mixins `LoginRequiredMixin` para CBV
- Mixins personalizados para roles específicos
- Validaciones manuales dentro de las vistas

### 3. Mensajes al Usuario
```python
from django.contrib import messages

messages.success(request, 'Operación exitosa')
messages.error(request, 'Error en la operación')
messages.warning(request, 'Advertencia')
messages.info(request, 'Información')
```

### 4. Redirecciones Seguras
```python
return redirect('solicitud_detail', pk=solicitud.pk)
# O
return redirect(reverse('solicitud_detail', kwargs={'pk': pk}))
```

### 5. get_object_or_404
```python
solicitud = get_object_or_404(Solicitud, pk=pk)
# Retorna 404 si no existe, más seguro que .get()
```

---

## 🔍 Problema N+1 y su Solución

### ❌ Sin Optimización (N+1 queries):
```python
solicitudes = Solicitud.objects.all()
for solicitud in solicitudes:
    print(solicitud.creador.username)  # Query adicional por cada solicitud
    print(solicitud.adulto_mayor.nombre)  # Otra query adicional
# Total: 1 + N + N queries = 1 + 2N queries
```

### ✅ Con select_related (1 query):
```python
solicitudes = Solicitud.objects.select_related('creador', 'adulto_mayor').all()
for solicitud in solicitudes:
    print(solicitud.creador.username)  # Sin query adicional
    print(solicitud.adulto_mayor.nombre)  # Sin query adicional
# Total: 1 query (con JOINs)
```

---

## 🛡️ Flujo de Validación de Permisos

```
1. Usuario hace request
   ↓
2. @login_required verifica autenticación
   ↓
3. Mixin/Validación manual verifica rol
   ↓
4. Validación de ownership (si aplica)
   ↓
5. Validación de estado del objeto
   ↓
6. Procesar lógica de negocio
   ↓
7. Retornar respuesta
```

---

## 📝 Patrones de Diseño Utilizados

1. **DRY (Don't Repeat Yourself)**: Lógica de negocio en métodos del modelo
2. **Separation of Concerns**: Mixins para permisos, vistas para lógica
3. **Fat Models, Thin Views**: Métodos complejos en modelos (aceptar, rechazar, finalizar)
4. **Query Optimization**: select_related, prefetch_related, annotate

---

## 🚀 Próximos Pasos (No Implementados Aún)

1. **Templates HTML**: Crear archivos de template para renderizar las vistas
2. **Autenticación**: Implementar login, logout, registro
3. **API REST**: Opcional - Para frontend JavaScript/React
4. **Tests**: Escribir tests unitarios y de integración
5. **Deployment**: Configurar para producción

---

## 📚 Referencias

- [Django Views Documentation](https://docs.djangoproject.com/en/5.2/topics/http/views/)
- [Django ORM Optimization](https://docs.djangoproject.com/en/5.2/topics/db/optimization/)
- [Django Messages Framework](https://docs.djangoproject.com/en/5.2/ref/contrib/messages/)
- [Django Authentication](https://docs.djangoproject.com/en/5.2/topics/auth/)
