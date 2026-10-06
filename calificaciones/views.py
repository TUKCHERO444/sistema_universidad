from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from decimal import Decimal

from .models import Calificacion, HistorialCalificacion
from .services import CalificacionService
from academico.models import Seccion, Docente, Estudiante, Periodo
from matriculas.models import DetalleMatricula, Matricula
from cuentas.decorators import role_required
from cuentas.services import registrar_auditoria

@login_required
@role_required(['ADMIN', 'DOCENTE'])
def calificacion_list_view(request):
    periodo_actual = Periodo.objects.filter(activo=True).first()
    periodo_id = request.GET.get('periodo', '')
    seccion_id = request.GET.get('seccion', '')
    query = request.GET.get('q', '').strip()

    qs = Calificacion.objects.select_related(
        'detalle_matricula__matricula__estudiante',
        'detalle_matricula__seccion__curso',
        'detalle_matricula__seccion__docente',
        'detalle_matricula__seccion__periodo'
    ).filter(detalle_matricula__matricula__estado=Matricula.EstadoMatricula.REGISTRADA)

    if request.user.es_docente and hasattr(request.user, 'perfil_docente'):
        qs = qs.filter(detalle_matricula__seccion__docente=request.user.perfil_docente)

    if periodo_id:
        qs = qs.filter(detalle_matricula__seccion__periodo_id=periodo_id)
    elif periodo_actual and not request.GET:
        qs = qs.filter(detalle_matricula__seccion__periodo=periodo_actual)

    if seccion_id:
        qs = qs.filter(detalle_matricula__seccion_id=seccion_id)

    if query:
        qs = qs.filter(
            detalle_matricula__matricula__estudiante__apellidos__icontains=query
        ) | qs.filter(
            detalle_matricula__matricula__estudiante__codigo__icontains=query
        )

    paginator = Paginator(qs, 20)
    calificaciones = paginator.get_page(request.GET.get('page'))

    secciones_filtro = Seccion.objects.all()
    if request.user.es_docente and hasattr(request.user, 'perfil_docente'):
        secciones_filtro = secciones_filtro.filter(docente=request.user.perfil_docente)

    return render(request, 'calificaciones/calificacion_list.html', {
        'calificaciones': calificaciones,
        'periodos': Periodo.objects.all(),
        'secciones_filtro': secciones_filtro,
        'periodo_filtro': periodo_id,
        'seccion_filtro': seccion_id,
        'query': query
    })

@login_required
@role_required(['ADMIN', 'DOCENTE'])
def seccion_calificaciones_view(request, seccion_id):
    seccion = get_object_or_404(
        Seccion.objects.select_related('curso', 'docente', 'periodo', 'curso__carrera'),
        pk=seccion_id
    )

    if request.user.es_docente and hasattr(request.user, 'perfil_docente'):
        if seccion.docente != request.user.perfil_docente:
            messages.error(request, "No está autorizado para modificar calificaciones de esta sección.")
            return redirect('cuentas:dashboard')

    inscritos = DetalleMatricula.objects.filter(
        seccion=seccion,
        matricula__estado=Matricula.EstadoMatricula.REGISTRADA,
        estado=DetalleMatricula.EstadoDetalle.INSCRITO
    ).select_related('matricula__estudiante', 'calificacion').order_by('matricula__estudiante__apellidos')

    if request.method == 'POST':
        motivo = request.POST.get('motivo_general', 'Registro ordinario de notas').strip()
        actualizados = 0
        errores = []

        for det in inscritos:
            n1 = request.POST.get(f"nota1_{det.id}")
            n2 = request.POST.get(f"nota2_{det.id}")
            n3 = request.POST.get(f"nota3_{det.id}")

            calif_obj = getattr(det, 'calificacion', None)
            if not calif_obj:
                calif_obj = Calificacion.objects.create(detalle_matricula=det, registrado_por=request.user)

            try:
                CalificacionService.actualizar_notas(
                    calificacion_id=calif_obj.id,
                    nota1=n1,
                    nota2=n2,
                    nota3=n3,
                    usuario=request.user,
                    motivo=motivo,
                    request=request
                )
                actualizados += 1
            except ValidationError as e:
                errores.append(f"{det.matricula.estudiante.codigo}: {e}")
            except Exception as e:
                errores.append(f"{det.matricula.estudiante.codigo}: {str(e)}")

        if errores:
            for err in errores:
                messages.warning(request, err)
        if actualizados:
            messages.success(request, f"Se actualizaron {actualizados} registros de calificaciones correctamente.")
        return redirect('calificaciones:seccion_calificaciones', seccion_id=seccion.id)

    return render(request, 'calificaciones/seccion_calificaciones_sheet.html', {
        'seccion': seccion,
        'inscritos': inscritos
    })

@login_required
@role_required(['ADMIN', 'DOCENTE'])
def calificacion_historial_view(request, pk):
    calificacion = get_object_or_404(
        Calificacion.objects.select_related(
            'detalle_matricula__matricula__estudiante',
            'detalle_matricula__seccion__curso',
            'detalle_matricula__seccion__periodo'
        ),
        pk=pk
    )
    historial = calificacion.historial.select_related('modificado_por').order_by('-fecha_cambio')
    return render(request, 'calificaciones/calificacion_historial.html', {
        'calificacion': calificacion,
        'historial': historial
    })

@login_required
@role_required('ESTUDIANTE')
def mis_calificaciones_estudiante_view(request):
    estudiante = get_object_or_404(Estudiante, usuario=request.user)
    periodos = Periodo.objects.all().order_by('-fecha_inicio')
    periodo_id = request.GET.get('periodo', '')

    matricula = None
    if periodo_id:
        matricula = Matricula.objects.filter(
            estudiante=estudiante,
            periodo_id=periodo_id,
            estado=Matricula.EstadoMatricula.REGISTRADA
        ).first()
    else:
        matricula = Matricula.objects.filter(
            estudiante=estudiante,
            estado=Matricula.EstadoMatricula.REGISTRADA
        ).order_by('-periodo__fecha_inicio').first()

    detalles = []
    if matricula:
        detalles = matricula.detalles.filter(
            estado=DetalleMatricula.EstadoDetalle.INSCRITO
        ).select_related('seccion__curso', 'seccion__docente', 'calificacion')

    return render(request, 'calificaciones/mis_calificaciones.html', {
        'estudiante': estudiante,
        'periodos': periodos,
        'matricula': matricula,
        'detalles': detalles,
        'periodo_seleccionado_id': periodo_id
    })
