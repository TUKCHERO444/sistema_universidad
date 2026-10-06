from django.urls import path
from . import views

app_name = 'academico'

urlpatterns = [
    # Carreras
    path('carreras/', views.carrera_list_view, name='carrera_list'),
    path('carreras/crear/', views.carrera_create_view, name='carrera_create'),
    path('carreras/<int:pk>/editar/', views.carrera_update_view, name='carrera_update'),

    # Cursos
    path('cursos/', views.curso_list_view, name='curso_list'),
    path('cursos/crear/', views.curso_create_view, name='curso_create'),
    path('cursos/<int:pk>/editar/', views.curso_update_view, name='curso_update'),

    # Periodos
    path('periodos/', views.periodo_list_view, name='periodo_list'),
    path('periodos/crear/', views.periodo_create_view, name='periodo_create'),
    path('periodos/<int:pk>/editar/', views.periodo_update_view, name='periodo_update'),

    # Docentes
    path('docentes/', views.docente_list_view, name='docente_list'),
    path('docentes/crear/', views.docente_create_view, name='docente_create'),

    # Estudiantes
    path('estudiantes/', views.estudiante_list_view, name='estudiante_list'),
    path('estudiantes/crear/', views.estudiante_create_view, name='estudiante_create'),

    # Secciones
    path('secciones/', views.seccion_list_view, name='seccion_list'),
    path('secciones/crear/', views.seccion_create_view, name='seccion_create'),

    # Facultades
    path('facultades/', views.facultad_list_view, name='facultad_list'),
    path('facultades/crear/', views.facultad_create_view, name='facultad_create'),
    path('facultades/<int:pk>/editar/', views.facultad_update_view, name='facultad_update'),

    # Planes de Estudio
    path('planes-estudio/', views.plan_estudio_list_view, name='plan_estudio_list'),
    path('planes-estudio/crear/', views.plan_estudio_create_view, name='plan_estudio_create'),
    path('planes-estudio/<int:pk>/editar/', views.plan_estudio_update_view, name='plan_estudio_update'),

    # Rol Docente y Estudiante
    path('mis-secciones/', views.mis_secciones_view, name='mis_secciones'),
    path('mis-cursos/', views.mis_cursos_estudiante_view, name='mis_cursos_estudiante'),
]
