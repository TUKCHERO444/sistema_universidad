import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .services import AnaliticaService
from academico.models import Periodo, Carrera, Curso, Docente, Estudiante, Seccion
from predicciones.models import VersionModelo, PrediccionEstudiante
from cuentas.decorators import role_required

@login_required
@role_required('ADMIN')
def dashboard_analitica_view(request):
    periodo_id = request.GET.get('periodo', '')
    carrera_id = request.GET.get('carrera', '')
    curso_id = request.GET.get('curso', '')

    periodos = Periodo.objects.all().order_by('-fecha_inicio')
    periodo_actual = Periodo.objects.filter(activo=True).first()
    carreras = Carrera.objects.filter(activo=True)
    cursos = Curso.objects.filter(activo=True)

    periodo_seleccionado_id = int(periodo_id) if periodo_id else (periodo_actual.id if periodo_actual else None)

    # Gráficos interactivos Plotly
    grafico_carreras = AnaliticaService.generar_grafico_matriculas_por_carrera(periodo_seleccionado_id)
    grafico_notas = AnaliticaService.generar_grafico_distribucion_notas(periodo_seleccionado_id, int(curso_id) if curso_id else None)
    grafico_secciones = AnaliticaService.generar_grafico_aprobacion_secciones(periodo_seleccionado_id)

    # Alertas deterministas basadas en reglas
    alertas_reglas = AnaliticaService.obtener_alertas_por_reglas(periodo_seleccionado_id)

    # Alertas ML del modelo activo
    modelo_activo = VersionModelo.objects.filter(activo=True).first()
    alertas_ml = []
    if modelo_activo:
        alertas_ml = PrediccionEstudiante.objects.filter(
            version_modelo=modelo_activo,
            nivel_riesgo__in=[PrediccionEstudiante.NivelRiesgo.ALTO, PrediccionEstudiante.NivelRiesgo.MEDIO]
        ).select_related('instantanea__detalle_matricula__matricula__estudiante', 'instantanea__detalle_matricula__seccion__curso')[:10]

    return render(request, 'analitica/dashboard_analitica.html', {
        'periodos': periodos,
        'carreras': carreras,
        'cursos': cursos,
        'periodo_filtro': periodo_seleccionado_id,
        'carrera_filtro': carrera_id,
        'curso_filtro': curso_id,
        'grafico_carreras_json': json.dumps(grafico_carreras) if grafico_carreras else None,
        'grafico_notas_json': json.dumps(grafico_notas) if grafico_notas else None,
        'grafico_secciones_json': json.dumps(grafico_secciones) if grafico_secciones else None,
        'alertas_reglas': alertas_reglas[:8],
        'alertas_ml': alertas_ml,
        'modelo_activo': modelo_activo
    })

@login_required
@role_required('DOCENTE')
def analisis_docente_view(request):
    docente = get_object_or_404(Docente, usuario=request.user)
    periodo_actual = Periodo.objects.filter(activo=True).first()
    periodo_id = request.GET.get('periodo', '')
    
    periodo_seleccionado_id = int(periodo_id) if periodo_id else (periodo_actual.id if periodo_actual else None)

    grafico_secciones = AnaliticaService.generar_grafico_aprobacion_secciones(periodo_seleccionado_id, docente=docente)
    alertas_reglas = AnaliticaService.obtener_alertas_por_reglas(periodo_seleccionado_id, docente=docente)

    return render(request, 'analitica/analisis_docente.html', {
        'docente': docente,
        'periodos': Periodo.objects.all(),
        'periodo_filtro': periodo_seleccionado_id,
        'grafico_secciones_json': json.dumps(grafico_secciones) if grafico_secciones else None,
        'alertas_reglas': alertas_reglas
    })

@login_required
@role_required('DOCENTE')
def alertas_docente_view(request):
    docente = get_object_or_404(Docente, usuario=request.user)
    periodo_actual = Periodo.objects.filter(activo=True).first()

    alertas_reglas = AnaliticaService.obtener_alertas_por_reglas(periodo_actual.id if periodo_actual else None, docente=docente)
    
    # Predicciones ML para sus secciones
    modelo_activo = VersionModelo.objects.filter(activo=True).first()
    predicciones = []
    if modelo_activo:
        predicciones = PrediccionEstudiante.objects.filter(
            version_modelo=modelo_activo,
            instantanea__detalle_matricula__seccion__docente=docente
        ).select_related('instantanea__detalle_matricula__matricula__estudiante', 'instantanea__detalle_matricula__seccion__curso')

    return render(request, 'analitica/alertas_docente.html', {
        'docente': docente,
        'periodo_actual': periodo_actual,
        'alertas_reglas': alertas_reglas,
        'predicciones': predicciones,
        'modelo_activo': modelo_activo
    })

@login_required
@role_required('ESTUDIANTE')
def mi_evolucion_view(request):
    estudiante = get_object_or_404(Estudiante, usuario=request.user)
    grafico_evolucion = AnaliticaService.generar_grafico_evolucion_estudiante(estudiante.id)

    return render(request, 'analitica/mi_evolucion.html', {
        'estudiante': estudiante,
        'grafico_evolucion_json': json.dumps(grafico_evolucion) if grafico_evolucion else None
    })
