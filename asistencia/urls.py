from django.urls import path
from . import views

app_name = 'asistencia'

urlpatterns = [
    path('', views.sesion_list_view, name='sesion_list'),
    path('mis-asistencias/', views.sesion_list_view, name='mis_asistencias'),
    path('seccion/<int:seccion_id>/', views.sesion_registro_seccion_view, name='sesion_registro_seccion'),
    path('sesion/<int:sesion_id>/matriz/', views.sesion_matriz_view, name='sesion_matriz'),
    path('mi-asistencia/', views.mi_asistencia_view, name='mi_asistencia'),
]
