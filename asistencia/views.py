from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q

from .models import SesionClase, Asistencia, HistorialAsistencia
from .services import AsistenciaService
from academico.models import Seccion, Docente, Estudiante, Periodo
from matriculas.models import DetalleMatricula, Matricula
from cuentas.decorators import role_required
from cuentas.services import registrar_auditoria

@login_required
@role_required(['ADMIN', 'DOCENTE'])
def sesion_list_view(request):
    periodo_actual = Periodo.objects.filter(activo=True).first()
    periodo_id = request.GET.get('periodo', '')
    seccion_id = request.GET.get('seccion', '')

    qs = SesionClase.objects.select_related('seccion__curso', 'seccion__docente', 'seccion__periodo').order_by('-fecha', '-hora_inicio')

    if request.user.es_docente and hasattr(request.user, 'perfil_docente'):
        qs = qs.filter(seccion__docente=request.user.perfil_docente)

    if periodo_id:
        qs = qs.filter(seccion__periodo_id=periodo_id)
    elif periodo_actual and not request.GET:
        qs = qs.filter(seccion__periodo=periodo_actual)

    if seccion_id:
        qs = qs.filter(seccion_id=seccion_id)

    paginator = Paginator(qs, 20)
    sesiones = paginator.get_page(request.GET.get('page'))

    secciones_filtro = Seccion.objects.all()
    if request.user.es_docente and hasattr(request.user, 'perfil_docente'):
        secciones_filtro = secciones_filtro.filter(docente=request.user.perfil_docente)

    return render(request, 'asistencia/sesion_list.html', {
        'sesiones': sesiones,
        'periodos': Periodo.objects.all(),
        'secciones_filtro': secciones_filtro,
        'periodo_filtro': periodo_id,
        'seccion_filtro': seccion_id
    })

@login_required
@role_required(['ADMIN', 'DOCENTE'])
def sesion_registro_seccion_view(request, seccion_id):
    seccion = get_object_or_404(Seccion.objects.select_related('curso', 'docente', 'periodo'), pk=seccion_id)

    # Validar que si es docente solo acceda a su seccion
    if request.user.es_docente and hasattr(request.user, 'perfil_docente'):
        if seccion.docente != request.user.perfil_docente:
            messages.error(request, "No está autorizado para gestionar esta sección.")
            return redirect('cuentas:dashboard')

    if request.method == 'POST' and 'crear_sesion' in request.POST:
        fecha_str = request.POST.get('fecha')
        hora_ini = request.POST.get('hora_inicio')
        hora_fin = request.POST.get('hora_fin')
        tema = request.POST.get('tema', '').strip()

        try:
            sesion = SesionClase.objects.create(
                seccion=seccion,
                fecha=fecha_str,
                hora_inicio=hora_ini,
                hora_fin=hora_fin,
                tema=tema,
                creado_por=request.user
            )
            registrar_auditoria(request.user, 'Asistencia', 'CREAR_SESION', f"Sesión creada para {seccion} fecha {fecha_str}", request)
            messages.success(request, f"Sesión de clase del {fecha_str} habilitada para toma de asistencia.")
            return redirect('asistencia:sesion_matriz', sesion_id=sesion.id)
        except Exception as e:
            messages.error(request, f"Error al crear sesión: {e}")

    sesiones_seccion = seccion.sesiones.order_by('-fecha', '-hora_inicio')
    inscritos = DetalleMatricula.objects.filter(
        seccion=seccion,
        matricula__estado=Matricula.EstadoMatricula.REGISTRADA,
        estado=DetalleMatricula.EstadoDetalle.INSCRITO
    ).select_related('matricula__estudiante')

    return render(request, 'asistencia/sesion_seccion_hub.html', {
        'seccion': seccion,
        'sesiones': sesiones_seccion,
        'total_inscritos': inscritos.count(),
        'hoy': timezone.now().date()
    })

@login_required
@role_required(['ADMIN', 'DOCENTE'])
def sesion_matriz_view(request, sesion_id):
    sesion = get_object_or_404(SesionClase.objects.select_related('seccion__curso', 'seccion__docente', 'seccion__periodo'), pk=sesion_id)
    seccion = sesion.seccion

    if request.user.es_docente and hasattr(request.user, 'perfil_docente'):
        if seccion.docente != request.user.perfil_docente:
            messages.error(request, "No está autorizado para gestionar esta sesión.")
            return redirect('cuentas:dashboard')

    inscritos = DetalleMatricula.objects.filter(
        seccion=seccion,
        matricula__estado=Matricula.EstadoMatricula.REGISTRADA,
        estado=DetalleMatricula.EstadoDetalle.INSCRITO
    ).select_related('matricula__estudiante').order_by('matricula__estudiante__apellidos')

    if request.method == 'POST':
        asistencias_dict = {}
        for det in inscritos:
            estado = request.POST.get(f"estado_{det.id}")
            obs = request.POST.get(f"obs_{det.id}", "")
            if estado:
                asistencias_dict[det.id] = {'estado': estado, 'observacion': obs}

        try:
            AsistenciaService.registrar_o_actualizar_asistencias(sesion.id, asistencias_dict, request.user, request=request)
            messages.success(request, "Registro de asistencia guardado exitosamente.")
            return redirect('asistencia:sesion_registro_seccion', seccion_id=seccion.id)
        except Exception as e:
            messages.error(request, f"Error al registrar asistencia: {e}")

    # Cargar asistencias existentes
    asistencias_map = {a.detalle_matricula_id: a for a in sesion.asistencias.all()}

    filas = []
    for det in inscritos:
        asist = asistencias_map.get(det.id)
        resumen = AsistenciaService.calcular_resumen_asistencia(det.id)
        filas.append({
            'detalle': det,
            'estudiante': det.matricula.estudiante,
            'estado_actual': asist.estado if asist else 'PRESENTE',
            'observacion': asist.observacion if asist else '',
            'resumen_acumulado': resumen
        })

    return render(request, 'asistencia/sesion_matriz.html', {
        'sesion': sesion,
        'seccion': seccion,
        'filas': filas
    })

@login_required
@role_required('ESTUDIANTE')
def mi_asistencia_view(request):
    estudiante = get_object_or_404(Estudiante, usuario=request.user)
    periodo_actual = Periodo.objects.filter(activo=True).first()

    inscripciones = []
    if periodo_actual:
        detalles = DetalleMatricula.objects.filter(
            matricula__estudiante=estudiante,
            matricula__periodo=periodo_actual,
            matricula__estado=Matricula.EstadoMatricula.REGISTRADA,
            estado=DetalleMatricula.EstadoDetalle.INSCRITO
        ).select_related('seccion__curso', 'seccion__docente')

        for det in detalles:
            resumen = AsistenciaService.calcular_resumen_asistencia(det.id)
            sesiones_historial = Asistencia.objects.filter(
                detalle_matricula=det,
                sesion__cerrada=True
            ).select_related('sesion').order_by('sesion__fecha')
            inscripciones.append({
                'detalle': det,
                'seccion': det.seccion,
                'resumen': resumen,
                'sesiones': sesiones_historial
            })

    return render(request, 'asistencia/mi_asistencia.html', {
        'estudiante': estudiante,
        'periodo_actual': periodo_actual,
        'inscripciones': inscripciones
    })
