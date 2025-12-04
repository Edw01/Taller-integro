# 📁 Documentación de Estructura Visual y Templates

## Descripción General

Esta documentación explica la estructura completa de templates HTML5 semánticos y CSS externos creados para la aplicación VoluntariadoMayor, cumpliendo con todos los requisitos académicos de diseño web.

---

## 🎯 Requisitos Cumplidos

### ✅ HTML5 Semántico
- [x] Uso de etiquetas semánticas (`<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<footer>`)
- [x] Estructura clara y organizada
- [x] Accesibilidad (atributos alt, aria-labels, roles)
- [x] Meta tags apropiados (charset, viewport, description)

### ✅ CSS Externo
- [x] Hoja de estilos en archivo separado (`static/css/styles.css`)
- [x] Variables CSS (Custom Properties) para mantenibilidad
- [x] Diseño responsive con media queries
- [x] Sistema de grid moderno
- [x] Animaciones y transiciones suaves

### ✅ Django Template Language
- [x] Uso eficiente de `{% for %}` para iterar solicitudes
- [x] Uso de `{% if %}` para mostrar contenido según rol del usuario
- [x] Template inheritance con `{% extends %}` y `{% block %}`
- [x] Filtros de template (`|truncatewords`, `|date`, etc.)
- [x] Template tags (`{% url %}`, `{% static %}`, `{% load %}`)

---

## 📂 Estructura de Archivos Creados

```
system/
├── templates/
│   ├── base.html                          # Template base (padre)
│   └── adultomayor/
│       ├── home.html                      # Página de inicio
│       ├── dashboard.html                 # Dashboard personalizado
│       ├── solicitud_list.html            # Lista de solicitudes ⭐
│       └── reporte_gestion.html          # Reporte SQL
│
└── static/
    └── css/
        └── styles.css                     # Hoja de estilos externa ⭐
```

---

## 🏗️ base.html - Template Base

### Estructura Semántica HTML5

```html
<!DOCTYPE html>
<html lang="es">
<head>
    <!-- Meta tags -->
    <!-- CSS externo -->
</head>
<body>
    <!-- HEADER con navegación -->
    <header class="main-header">
        <nav class="navbar">
            <!-- Logo, menú, usuario -->
        </nav>
    </header>
    
    <!-- MAIN content -->
    <main class="main-content">
        <div class="container">
            <!-- Mensajes del sistema -->
            <!-- Breadcrumb -->
            <!-- Page header -->
            <!-- Content blocks -->
        </div>
    </main>
    
    <!-- FOOTER -->
    <footer class="main-footer">
        <!-- Footer content -->
    </footer>
    
    <!-- Scripts -->
</body>
</html>
```

### Características Destacadas

#### 1. **Etiquetas Semánticas HTML5**
```html
<header>     <!-- Encabezado principal -->
<nav>        <!-- Navegación -->
<main>       <!-- Contenido principal -->
<section>    <!-- Secciones temáticas -->
<article>    <!-- Contenido independiente -->
<footer>     <!-- Pie de página -->
<aside>      <!-- Contenido relacionado -->
```

#### 2. **Sistema de Bloques Django**
```django
{% block title %}{% endblock %}          <!-- Título de la página -->
{% block extra_css %}{% endblock %}      <!-- CSS adicional -->
{% block page_title %}{% endblock %}     <!-- Título visible -->
{% block content %}{% endblock %}        <!-- Contenido principal -->
{% block extra_js %}{% endblock %}       <!-- JavaScript adicional -->
```

#### 3. **Navegación Dinámica**
```django
{% if user.is_authenticated %}
    <!-- Menú para usuarios autenticados -->
    
    {% if user.es_solicitante %}
        <!-- Botones específicos para Solicitantes -->
        <a href="{% url 'adultomayor:solicitud_create' %}">
            Nueva Solicitud
        </a>
    {% endif %}
    
    {% if user.es_voluntario %}
        <!-- Contenido específico para Voluntarios -->
    {% endif %}
{% else %}
    <!-- Menú para usuarios no autenticados -->
{% endif %}
```

#### 4. **Sistema de Mensajes Django**
```django
{% if messages %}
    {% for message in messages %}
        <div class="alert alert-{{ message.tags }}">
            {{ message }}
        </div>
    {% endfor %}
{% endif %}
```

---

## 📋 solicitud_list.html - Lista de Solicitudes

### Demostración de Bucles {% for %}

```django
{% if solicitudes %}
    {% for solicitud in solicitudes %}
        <article class="solicitud-card">
            <!-- Contenido de cada solicitud -->
            
            <!-- CONTADOR: forloop.counter -->
            Solicitud #{{ forloop.counter }}
            
            <!-- COMPROBACIONES: forloop.first, forloop.last -->
            {% if forloop.first %}
                <span>Primera solicitud</span>
            {% endif %}
        </article>
    {% endfor %}
{% else %}
    <!-- Estado vacío -->
    <div class="empty-state">
        No hay solicitudes disponibles
    </div>
{% endif %}
```

### Demostración de Condicionales {% if %}

#### 1. **Condicionales según Rol del Usuario**
```django
{% if user.is_authenticated %}
    {% if user.es_voluntario %}
        <!-- SOLO PARA VOLUNTARIOS -->
        {% if solicitud.estado == 'PENDIENTE' %}
            <a href="{% url 'adultomayor:postular_solicitud' solicitud.pk %}" 
               class="btn btn-postular">
                <span class="icon">✋</span> Postular
            </a>
        {% elif solicitud.voluntario_asignado == user %}
            <span class="badge badge-info">
                ✓ Asignado a ti
            </span>
        {% endif %}
    
    {% elif user.es_solicitante and user == solicitud.creador %}
        <!-- SOLO PARA EL CREADOR DE LA SOLICITUD -->
        {% if solicitud.estado == 'PENDIENTE' %}
            <a href="{% url 'adultomayor:solicitud_update' solicitud.pk %}" 
               class="btn btn-edit">
                ✏️ Editar
            </a>
        {% endif %}
        
        {% if solicitud.estado == 'ASIGNADA' %}
            <a href="{% url 'adultomayor:solicitud_finalizar' solicitud.pk %}" 
               class="btn btn-success">
                ✓ Finalizar
            </a>
        {% endif %}
    {% endif %}
{% else %}
    <!-- USUARIO NO AUTENTICADO -->
    <a href="{% url 'admin:login' %}" class="btn btn-login-prompt">
        🔐 Inicia sesión para postular
    </a>
{% endif %}
```

#### 2. **Condicionales según Estado de la Solicitud**
```django
<!-- Mostrar badge de color según el estado -->
<span class="badge badge-{{ solicitud.estado|lower }}">
    {{ solicitud.get_estado_display }}
</span>

<!-- Mostrar información solo si existe -->
{% if solicitud.fecha_limite %}
    <div class="info-item">
        <span>Fecha Límite:</span>
        <span>{{ solicitud.fecha_limite|date:"d/m/Y" }}</span>
    </div>
{% endif %}

{% if solicitud.voluntario_asignado %}
    <div class="info-item">
        <span>Voluntario:</span>
        <span>{{ solicitud.voluntario_asignado.get_full_name }}</span>
    </div>
{% endif %}
```

#### 3. **Condicionales Anidadas Complejas**
```django
{% if user.is_authenticated %}
    {% if user.es_solicitante %}
        {% if user == solicitud.creador %}
            <!-- Mostrar contador de postulaciones SOLO para el creador -->
            <div class="info-item">
                <span>Postulaciones:</span>
                <span>{{ solicitud.num_postulaciones|default:0 }}</span>
            </div>
        {% endif %}
    {% endif %}
{% endif %}
```

### Características de Diseño

#### 1. **Sistema de Filtros**
```html
<form method="get" class="filters-form">
    <!-- Búsqueda por texto -->
    <input type="text" name="search" value="{{ search_query }}">
    
    <!-- Filtro por prioridad -->
    <select name="prioridad">
        <option value="">Todas</option>
        <option value="URGENTE" 
                {% if prioridad_filter == 'URGENTE' %}selected{% endif %}>
            Urgente
        </option>
    </select>
    
    <button type="submit">Filtrar</button>
</form>
```

#### 2. **Grid Responsive de Cards**
```css
.solicitudes-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 25px;
}
```

#### 3. **Cards con Estructura Semántica**
```html
<article class="solicitud-card">
    <div class="card-header">
        <!-- ID y badges de estado -->
    </div>
    
    <div class="card-body">
        <!-- Título, descripción, información -->
    </div>
    
    <div class="card-footer">
        <!-- Botones de acción -->
    </div>
</article>
```

---

## 🎨 styles.css - Hoja de Estilos Externa

### 1. Variables CSS (Custom Properties)

```css
:root {
    /* Colores Principales */
    --color-primary: #667eea;
    --color-secondary: #764ba2;
    --color-success: #28a745;
    --color-danger: #dc3545;
    
    /* Espaciado */
    --spacing-sm: 10px;
    --spacing-md: 15px;
    --spacing-lg: 20px;
    
    /* Border Radius */
    --radius-md: 8px;
    --radius-lg: 12px;
    
    /* Sombras */
    --shadow-md: 0 4px 10px rgba(0, 0, 0, 0.1);
    
    /* Transiciones */
    --transition-normal: 0.3s ease;
}
```

**Ventajas**:
- Fácil mantenimiento (cambiar un color en un solo lugar)
- Consistencia en todo el diseño
- Reutilización de valores
- Facilita el theming

### 2. Sistema de Reset

```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: var(--color-text);
}
```

### 3. Sistema de Grid Moderno

```css
.solicitudes-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 25px;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
}
```

**auto-fill vs auto-fit**:
- `auto-fill`: Crea todas las columnas posibles (incluso vacías)
- `auto-fit`: Colapsa columnas vacías y expande las existentes

### 4. Diseño Responsive

```css
@media (max-width: 768px) {
    .navbar .container {
        flex-direction: column;
    }
    
    .solicitudes-grid {
        grid-template-columns: 1fr;
    }
    
    .card-footer {
        flex-direction: column;
    }
}
```

### 5. Animaciones y Transiciones

```css
.solicitud-card {
    transition: transform 0.3s, box-shadow 0.3s;
}

.solicitud-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

@keyframes slideIn {
    from {
        transform: translateY(-20px);
        opacity: 0;
    }
    to {
        transform: translateY(0);
        opacity: 1;
    }
}

.alert {
    animation: slideIn 0.3s ease;
}
```

### 6. Sistema de Badges Dinámicos

```css
.badge {
    display: inline-block;
    padding: 5px 12px;
    border-radius: 20px;
    font-weight: 600;
}

/* Badges de Estado */
.badge-pendiente { background-color: #ffc107; color: #333; }
.badge-asignada { background-color: #007bff; color: white; }
.badge-finalizada { background-color: #28a745; color: white; }

/* Badges de Prioridad */
.badge-urgente { background-color: #dc3545; color: white; }
.badge-alta { background-color: #fd7e14; color: white; }
.badge-media { background-color: #ffc107; color: #333; }
.badge-baja { background-color: #28a745; color: white; }
```

### 7. Sistema de Botones Completo

```css
.btn {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 10px 20px;
    border-radius: 8px;
    transition: all 0.2s ease;
}

.btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
}

.btn-primary { background-color: #667eea; color: white; }
.btn-success { background-color: #28a745; color: white; }
.btn-danger { background-color: #dc3545; color: white; }
```

---

## 🔗 Sistema de URLs Completo

### urls.py de la aplicación

```python
from django.urls import path
from . import views

app_name = 'adultomayor'

urlpatterns = [
    # Generales
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Solicitudes
    path('solicitudes/', views.SolicitudListView.as_view(), name='solicitud_list'),
    path('solicitudes/<int:pk>/', views.SolicitudDetailView.as_view(), name='solicitud_detail'),
    path('solicitudes/crear/', views.crear_solicitud, name='solicitud_create'),
    path('solicitudes/<int:pk>/editar/', views.SolicitudUpdateView.as_view(), name='solicitud_update'),
    path('solicitudes/<int:pk>/eliminar/', views.SolicitudDeleteView.as_view(), name='solicitud_delete'),
    path('solicitudes/<int:pk>/finalizar/', views.finalizar_solicitud, name='solicitud_finalizar'),
    
    # Postulaciones
    path('solicitudes/<int:pk>/postular/', views.postular_solicitud, name='postular_solicitud'),
    path('postulaciones/<int:pk>/aprobar/', views.aprobar_voluntario, name='aprobar_postulacion'),
    path('postulaciones/<int:pk>/rechazar/', views.rechazar_postulacion, name='rechazar_postulacion'),
    
    # Mensajes
    path('solicitudes/<int:pk>/mensaje/', views.enviar_mensaje, name='enviar_mensaje'),
    
    # Reportes
    path('reporte/gestion/', views.reporte_gestion_sql, name='reporte_gestion'),
]
```

### Uso de URLs en Templates

```django
<!-- URL simple -->
<a href="{% url 'adultomayor:home' %}">Inicio</a>

<!-- URL con parámetro -->
<a href="{% url 'adultomayor:solicitud_detail' solicitud.pk %}">
    Ver Detalle
</a>

<!-- URL con query parameters -->
<a href="{% url 'adultomayor:solicitud_list' %}?prioridad=URGENTE">
    Urgentes
</a>
```

---

## 📱 Responsive Design

### Breakpoints Utilizados

```css
/* Mobile First Approach */

/* Mobile: Default (< 768px) */
/* Una columna, menú vertical */

/* Tablet: >= 768px */
@media (min-width: 768px) {
    /* 2 columnas */
}

/* Desktop: >= 1024px */
@media (min-width: 1024px) {
    /* 3+ columnas */
}
```

### Técnicas Responsive Aplicadas

1. **Grid Adaptativo**
```css
grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
```

2. **Flexbox con Wrap**
```css
display: flex;
flex-wrap: wrap;
gap: 20px;
```

3. **Viewport Units**
```css
width: 100vw;
height: 100vh;
font-size: calc(16px + 0.5vw);
```

4. **Media Queries para Navegación**
```css
@media (max-width: 768px) {
    .navbar-menu {
        flex-direction: column;
        width: 100%;
    }
}
```

---

## ✅ Checklist de Cumplimiento

### HTML5 Semántico
- [x] Uso de `<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<footer>`
- [x] Meta tags completos (charset, viewport, description)
- [x] Estructura jerárquica clara (h1-h6)
- [x] Atributos semánticos (lang, alt, title)

### CSS Externo
- [x] Archivo separado `static/css/styles.css`
- [x] Variables CSS (Custom Properties)
- [x] Sistema de grid moderno
- [x] Responsive design con media queries
- [x] Animaciones y transiciones

### Django Templates
- [x] Template inheritance (`{% extends %}`)
- [x] Bloques (`{% block %}`)
- [x] Bucles `{% for %}` con variables (counter, first, last)
- [x] Condicionales `{% if %}` anidadas
- [x] Filtros (`|truncatewords`, `|date`, `|default`)
- [x] URLs dinámicas (`{% url %}`)
- [x] Archivos estáticos (`{% static %}`)

### Diseño
- [x] Limpio y ordenado
- [x] Consistente en colores y espaciado
- [x] Feedback visual (hover, active, focus)
- [x] Responsive y adaptable
- [x] Accesible

---

## 🎓 Conceptos Web Demostrados

1. **Separación de Responsabilidades**
   - HTML: Estructura
   - CSS: Presentación
   - JavaScript: Comportamiento

2. **Mobile First**
   - Diseño desde móvil hacia desktop
   - Progressive enhancement

3. **BEM Naming (parcial)**
   - `.solicitud-card`
   - `.card-header`, `.card-body`, `.card-footer`

4. **Flexbox y Grid**
   - Layouts modernos y flexibles
   - Responsive sin media queries (auto-fill)

5. **CSS Variables**
   - Mantenibilidad
   - Theming
   - Reutilización

---

**Conclusión**: La estructura visual cumple con todos los requisitos académicos, demostrando dominio de HTML5 semántico, CSS externo profesional, y uso eficiente del Django Template Language con bucles y condicionales.
