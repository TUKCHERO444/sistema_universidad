from django.urls import path
from . import views

app_name = 'tramites'

urlpatterns = [
    # Tipos de Trámite
    path('tipos/', views.tipo_tramite_list_view, name='tipo_tramite_list'),
    path('tipos/crear/', views.tipo_tramite_create_view, name='tipo_tramite_create'),
    path('tipos/<int:pk>/editar/', views.tipo_tramite_update_view, name='tipo_tramite_update'),

    # Solicitudes de Trámite
    path('solicitudes/', views.solicitud_list_view, name='solicitud_list'),
    path('solicitudes/crear/', views.solicitud_create_view, name='solicitud_create'),
    path('solicitudes/<int:pk>/', views.solicitud_detail_view, name='solicitud_detail'),
    path('solicitudes/<int:pk>/editar/', views.solicitud_update_view, name='solicitud_update'),

    # Seguimiento de Trámites
    path('seguimientos/', views.seguimiento_list_view, name='seguimiento_list'),
    path('seguimientos/crear/', views.seguimiento_create_view, name='seguimiento_create'),
    path('seguimientos/<int:pk>/editar/', views.seguimiento_update_view, name='seguimiento_update'),
]
