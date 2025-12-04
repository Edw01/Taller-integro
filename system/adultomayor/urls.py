from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('adultos/', views.adultomayor_list, name='adultomayor_list'),
    path('adultos/<int:pk>/', views.adultomayor_detail, name='adultomayor_detail'),
    path('adultos/nuevo/', views.adultomayor_create, name='adultomayor_create'),
    path('adultos/<int:pk>/editar/', views.adultomayor_update, name='adultomayor_update'),
    path('adultos/<int:pk>/eliminar/', views.adultomayor_delete, name='adultomayor_delete'),
]
