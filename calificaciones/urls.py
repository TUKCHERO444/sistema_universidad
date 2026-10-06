from django.urls import path
from . import views

app_name = 'calificaciones'

urlpatterns = [
    path('', views.calificacion_list_view, name='calificacion_list'),
    path('mis-calificaciones/', views.calificacion_list_view, name='mis_calificaciones'),
    path('seccion/<int:seccion_id>/', views.seccion_calificaciones_view, name='seccion_calificaciones'),
    path('<int:pk>/historial/', views.calificacion_historial_view, name='calificacion_historial'),
    path('mi-boleta/', views.mis_calificaciones_estudiante_view, name='mis_calificaciones_estudiante'),
]
