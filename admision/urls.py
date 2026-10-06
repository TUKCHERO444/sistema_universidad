from django.urls import path
from . import views

app_name = 'admision'

urlpatterns = [
    # Modalidades de Ingreso
    path('modalidades/', views.modalidad_list_view, name='modalidad_list'),
    path('modalidades/crear/', views.modalidad_create_view, name='modalidad_create'),
    path('modalidades/<int:pk>/editar/', views.modalidad_update_view, name='modalidad_update'),

    # Procesos de Admisión
    path('procesos/', views.proceso_list_view, name='proceso_list'),
    path('procesos/crear/', views.proceso_create_view, name='proceso_create'),
    path('procesos/<int:pk>/editar/', views.proceso_update_view, name='proceso_update'),

    # Postulaciones
    path('postulaciones/', views.postulacion_list_view, name='postulacion_list'),
    path('postulaciones/crear/', views.postulacion_create_view, name='postulacion_create'),
    path('postulaciones/<int:pk>/', views.postulacion_detail_view, name='postulacion_detail'),
    path('postulaciones/<int:pk>/editar/', views.postulacion_update_view, name='postulacion_update'),

    # Evaluaciones de Admisión
    path('evaluaciones/', views.evaluacion_list_view, name='evaluacion_list'),
    path('evaluaciones/crear/', views.evaluacion_create_view, name='evaluacion_create'),
    path('evaluaciones/<int:pk>/editar/', views.evaluacion_update_view, name='evaluacion_update'),
]
