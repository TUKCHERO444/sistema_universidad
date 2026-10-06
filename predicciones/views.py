from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

from .models import VersionModelo, InstantaneaPredictiva, PrediccionEstudiante
from .ml_service import PrediccionMLService
from academico.models import Periodo, Seccion, Docente, Carrera
from cuentas.decorators import role_required
from cuentas.services import registrar_auditoria

@login_required
@role_required('ADMIN')
def dashboard_predicciones_view(request):
    periodo_id = request.GET.get('periodo', '')
    nivel_riesgo = request.GET.get('nivel', '')
    query = request.GET.get('q', '').strip()

    modelos = VersionModelo.objects.all().order_by('-fecha_entrenamiento')
    modelo_activo = VersionModelo.objects.filter(activo=True).first()

    qs_predicciones = PrediccionEstudiante.objects.all().select_related(
        'instantanea__detalle_matricula__matricula__estudiante',
        'instantanea__detalle_matricula__seccion__curso',
        'instantanea__detalle_matricula__seccion__docente',
        'instantanea__detalle_matricula__seccion__periodo',
        'version_modelo'
    ).order_by('-probabilidad_riesgo')

    if modelo_activo:
        qs_predicciones = qs_predicciones.filter(version_modelo=modelo_activo)

    if periodo_id:
        qs_predicciones = qs_predicciones.filter(instantanea__detalle_matricula__seccion__periodo_id=periodo_id)
    if nivel_riesgo:
        qs_predicciones = qs_predicciones.filter(nivel_riesgo=nivel_riesgo)
    if query:
        qs_predicciones = qs_predicciones.filter(
            Q(instantanea__detalle_matricula__matricula__estudiante__nombres__icontains=query) |
            Q(instantanea__detalle_matricula__matricula__estudiante__apellidos__icontains=query) |
            Q(instantanea__detalle_matricula__matricula__estudiante__codigo__icontains=query) |
            Q(instantanea__detalle_matricula__seccion__curso__codigo__icontains=query)
        )

    paginator = Paginator(qs_predicciones, 20)
    predicciones = paginator.get_page(request.GET.get('page'))

    # Conteo de instantáneas
    total_snapshots = InstantaneaPredictiva.objects.count()
    snapshots_evaluables = InstantaneaPredictiva.objects.filter(resultado_real_desaprobado__isnull=False).count()

    return render(request, 'predicciones/dashboard_predicciones.html', {
        'modelos': modelos,
        'modelo_activo': modelo_activo,
        'predicciones': predicciones,
        'periodos': Periodo.objects.all(),
        'periodo_filtro': periodo_id,
        'nivel_filtro': nivel_riesgo,
        'query': query,
        'total_snapshots': total_snapshots,
        'snapshots_evaluables': snapshots_evaluables
    })

@login_required
@role_required('DOCENTE')
def docente_predicciones_view(request):
    docente = get_object_or_404(Docente, usuario=request.user)
    modelo_activo = VersionModelo.objects.filter(activo=True).first()

    predicciones = []
    if modelo_activo:
        predicciones = PrediccionEstudiante.objects.filter(
            version_modelo=modelo_activo,
            instantanea__detalle_matricula__seccion__docente=docente
        ).select_related(
            'instantanea__detalle_matricula__matricula__estudiante',
            'instantanea__detalle_matricula__seccion__curso',
            'instantanea__detalle_matricula__seccion__periodo'
        ).order_by('-probabilidad_riesgo')

    return render(request, 'predicciones/docente_predicciones.html', {
        'docente': docente,
        'modelo_activo': modelo_activo,
        'predicciones': predicciones
    })

@login_required
@role_required('ADMIN')
def modelo_activar_view(request, pk):
    if request.method == 'POST':
        modelo = get_object_or_404(VersionModelo, pk=pk)
        VersionModelo.objects.filter(activo=True).update(activo=False)
        modelo.activo = True
        modelo.save()

        registrar_auditoria(request.user, 'Predicciones ML', 'ACTIVAR_MODELO', f"Modelo {modelo.nombre} ({modelo.version}) activado", request)
        messages.success(request, f"El modelo {modelo.nombre} ({modelo.version}) ha sido activado para inferencias.")
    return redirect('predicciones:dashboard_predicciones')

@login_required
@role_required('ADMIN')
def entrenar_modelos_action_view(request):
    if request.method == 'POST':
        # Primero construir o actualizar instantáneas
        creados = PrediccionMLService.construir_todas_las_instantaneas()
        
        # Entrenar y evaluar pipeline comparativo
        resultado = PrediccionMLService.entrenar_y_evaluar_modelos(usuario=request.user, es_sintetico=True)
        if resultado.get('exito'):
            # Ejecutar inferencia por lote
            PrediccionMLService.generar_predicciones_lote()
            registrar_auditoria(request.user, 'Predicciones ML', 'ENTRENAR_MODELOS', "Pipeline de entrenamiento y evaluación comparativa ejecutado", request)
            messages.success(request, f"Pipeline de Machine Learning completado. Se evaluaron {resultado.get('modelos_evaluados')} modelos. Modelo activo: {resultado.get('modelo_activo')}.")
        else:
            messages.warning(request, resultado.get('mensaje', 'Error durante el entrenamiento.'))
    return redirect('predicciones:dashboard_predicciones')

@login_required
@role_required('ADMIN')
def generar_predicciones_action_view(request):
    if request.method == 'POST':
        PrediccionMLService.construir_todas_las_instantaneas()
        res = PrediccionMLService.generar_predicciones_lote()
        if res.get('exito'):
            registrar_auditoria(request.user, 'Predicciones ML', 'INFERENCIA_LOTE', f"Inferencia por lote ejecutada ({res.get('predicciones_generadas')} casos)", request)
            messages.success(request, f"Se generaron {res.get('predicciones_generadas')} estimaciones de riesgo con el modelo {res.get('version_utilizada')}.")
        else:
            messages.error(request, res.get('mensaje'))
    return redirect('predicciones:dashboard_predicciones')

@login_required
@role_required(['ADMIN', 'DOCENTE'])
def estudiante_riesgo_detalle_view(request, pk):
    prediccion = get_object_or_404(
        PrediccionEstudiante.objects.select_related(
            'instantanea__detalle_matricula__matricula__estudiante',
            'instantanea__detalle_matricula__seccion__curso',
            'instantanea__detalle_matricula__seccion__docente',
            'instantanea__detalle_matricula__seccion__periodo',
            'version_modelo'
        ),
        pk=pk
    )

    if request.user.es_docente and hasattr(request.user, 'perfil_docente'):
        if prediccion.instantanea.detalle_matricula.seccion.docente != request.user.perfil_docente:
            messages.error(request, "No autorizado.")
            return redirect('cuentas:dashboard')

    return render(request, 'predicciones/estudiante_riesgo_detalle.html', {
        'p': prediccion,
        's': prediccion.instantanea,
        'm': prediccion.version_modelo
    })
