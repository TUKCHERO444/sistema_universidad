from django.urls import path
from . import views

app_name = 'analitica'

urlpatterns = [
    path('', views.dashboard_analitica_view, name='dashboard_analitica'),
    path('docente/', views.analisis_docente_view, name='analisis_docente'),
    path('alertas-docente/', views.alertas_docente_view, name='alertas_docente'),
    path('mi-evolucion/', views.mi_evolucion_view, name='mi_evolucion'),
]
