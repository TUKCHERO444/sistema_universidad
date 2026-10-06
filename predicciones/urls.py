from django.urls import path
from . import views

app_name = 'predicciones'

urlpatterns = [
    path('', views.dashboard_predicciones_view, name='dashboard_predicciones'),
    path('docente/', views.docente_predicciones_view, name='docente_predicciones'),
    path('modelos/<int:pk>/activar/', views.modelo_activar_view, name='modelo_activar'),
    path('pipeline/entrenar/', views.entrenar_modelos_action_view, name='entrenar_modelos'),
    path('pipeline/predecir/', views.generar_predicciones_action_view, name='generar_predicciones'),
    path('estudiante/<int:pk>/', views.estudiante_riesgo_detalle_view, name='estudiante_riesgo_detalle'),
]
