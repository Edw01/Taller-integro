from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('solicitudes/', views.solicitudes_list, name='solicitudes_list'),
    path('eliminar_cuenta/', views.eliminar_cuenta, name='eliminar_cuenta'),
]
