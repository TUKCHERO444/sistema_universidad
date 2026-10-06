from django.urls import path
from . import views

app_name = 'seguridad'

urlpatterns = [
    # Roles
    path('roles/', views.rol_list_view, name='rol_list'),
    path('roles/crear/', views.rol_create_view, name='rol_create'),
    path('roles/<int:pk>/editar/', views.rol_update_view, name='rol_update'),

    # Permisos
    path('permisos/', views.permiso_list_view, name='permiso_list'),
    path('permisos/crear/', views.permiso_create_view, name='permiso_create'),
    path('permisos/<int:pk>/editar/', views.permiso_update_view, name='permiso_update'),
]
