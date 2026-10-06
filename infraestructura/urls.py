from django.urls import path
from . import views

app_name = 'infraestructura'

urlpatterns = [
    # Aulas
    path('aulas/', views.aula_list_view, name='aula_list'),
    path('aulas/crear/', views.aula_create_view, name='aula_create'),
    path('aulas/<int:pk>/editar/', views.aula_update_view, name='aula_update'),

    # Horarios
    path('horarios/', views.horario_list_view, name='horario_list'),
    path('horarios/crear/', views.horario_create_view, name='horario_create'),
    path('horarios/<int:pk>/editar/', views.horario_update_view, name='horario_update'),

    # Calendario Académico
    path('calendario/', views.calendario_list_view, name='calendario_list'),
    path('calendario/crear/', views.calendario_create_view, name='calendario_create'),
    path('calendario/<int:pk>/editar/', views.calendario_update_view, name='calendario_update'),
]
