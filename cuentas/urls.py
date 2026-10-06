from django.urls import path
from . import views

app_name = 'cuentas'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('perfil/', views.perfil_view, name='perfil'),
    path('usuarios/', views.usuario_list_view, name='usuario_list'),
    path('usuarios/crear/', views.usuario_create_view, name='usuario_create'),
    path('usuarios/<int:pk>/editar/', views.usuario_update_view, name='usuario_update'),
    path('auditoria/', views.auditoria_list_view, name='auditoria_list'),
]
