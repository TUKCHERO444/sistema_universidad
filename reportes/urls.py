from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.centro_reportes_view, name='centro_reportes'),
    path('acta/<int:seccion_id>/pdf/', views.acta_pdf_view, name='acta_pdf'),
    path('acta/<int:seccion_id>/excel/', views.acta_excel_view, name='acta_excel'),
    path('predicciones/pdf/', views.predicciones_pdf_view, name='predicciones_pdf'),
    path('boleta/<int:matricula_id>/pdf/', views.estudiante_pdf_view, name='estudiante_pdf'),
    path('docente/', views.docente_reportes_view, name='docente_reportes'),
    path('mis-reportes/', views.estudiante_reportes_view, name='estudiante_reportes'),
]
