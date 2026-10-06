from django.urls import path
from . import views

app_name = 'egresados'

urlpatterns = [
    # Egresos
    path('egresos/', views.egreso_list_view, name='egreso_list'),
    path('egresos/crear/', views.egreso_create_view, name='egreso_create'),
    path('egresos/<int:pk>/editar/', views.egreso_update_view, name='egreso_update'),

    # Grados Académicos
    path('grados/', views.grado_list_view, name='grado_list'),
    path('grados/crear/', views.grado_create_view, name='grado_create'),
    path('grados/<int:pk>/editar/', views.grado_update_view, name='grado_update'),

    # Titulaciones
    path('titulaciones/', views.titulacion_list_view, name='titulacion_list'),
    path('titulaciones/crear/', views.titulacion_create_view, name='titulacion_create'),
    path('titulaciones/<int:pk>/editar/', views.titulacion_update_view, name='titulacion_update'),
]
