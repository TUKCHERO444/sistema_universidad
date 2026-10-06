from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .services import ReporteService
from academico.models import Seccion, Periodo, Docente, Estudiante, Curso
from matriculas.models import Matricula, DetalleMatricula
from calificaciones.models import Calificacion
from predicciones.models import VersionModelo, PrediccionEstudiante
from cuentas.decorators import role_required
from cuentas.services import registrar_auditoria

@login_required
@role_required(['ADMIN', 'DOCENTE'])
def centro_reportes_view(request):
    periodos = Periodo.objects.all().order_by('-fecha_inicio')
    secciones = Seccion.objects.all().select_related('curso', 'docente', 'periodo')
    
    if request.user.es_docente and hasattr(request.user, 'perfil_docente'):
        secciones = secciones.filter(docente=request.user.perfil_docente)

    modelo_activo = VersionModelo.objects.filter(activo=True).first()

    return render(request, 'reportes/centro_reportes.html', {
        'periodos': periodos,
        'secciones': secciones,
        'modelo_activo': modelo_activo
    })

@login_required
@role_required(['ADMIN', 'DOCENTE'])
def acta_pdf_view(request, seccion_id):
    seccion = get_object_or_404(Seccion.objects.select_related('curso__carrera', 'docente', 'periodo'), pk=seccion_id)

    if request.user.es_docente and hasattr(request.user, 'perfil_docente'):
        if seccion.docente != request.user.perfil_docente:
            raise Http404("No autorizado")

    calificaciones = Calificacion.objects.filter(
        detalle_matricula__seccion=seccion,
        detalle_matricula__matricula__estado=Matricula.EstadoMatricula.REGISTRADA
    ).select_related('detalle_matricula__matricula__estudiante').order_by('detalle_matricula__matricula__estudiante__apellidos')

    pdf_buffer = ReporteService.generar_pdf_acta_calificaciones(seccion, calificaciones, es_sintetico=True)
    registrar_auditoria(request.user, 'Reportes', 'EXPORTAR_PDF', f"Descarga de Acta PDF de sección {seccion}", request)

    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Acta_{seccion.curso.codigo}_Sec{seccion.codigo_seccion}.pdf"'
    return response

@login_required
@role_required(['ADMIN', 'DOCENTE'])
def acta_excel_view(request, seccion_id):
    seccion = get_object_or_404(Seccion.objects.select_related('curso__carrera', 'docente', 'periodo'), pk=seccion_id)

    if request.user.es_docente and hasattr(request.user, 'perfil_docente'):
        if seccion.docente != request.user.perfil_docente:
            raise Http404("No autorizado")

    calificaciones = Calificacion.objects.filter(
        detalle_matricula__seccion=seccion,
        detalle_matricula__matricula__estado=Matricula.EstadoMatricula.REGISTRADA
    ).select_related('detalle_matricula__matricula__estudiante').order_by('detalle_matricula__matricula__estudiante__apellidos')

    excel_buffer = ReporteService.generar_excel_calificaciones(seccion, calificaciones, es_sintetico=True)
    registrar_auditoria(request.user, 'Reportes', 'EXPORTAR_EXCEL', f"Descarga de Acta Excel de sección {seccion}", request)

    response = HttpResponse(excel_buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="Acta_{seccion.curso.codigo}_Sec{seccion.codigo_seccion}.xlsx"'
    return response

@login_required
@role_required(['ADMIN', 'DOCENTE'])
def predicciones_pdf_view(request):
    modelo_activo = VersionModelo.objects.filter(activo=True).first()
    if not modelo_activo:
        messages.error(request, "No hay modelo predictivo activo para exportar.")
        return redirect('reportes:centro_reportes')

    qs = PrediccionEstudiante.objects.filter(version_modelo=modelo_activo).select_related(
        'instantanea__detalle_matricula__matricula__estudiante',
        'instantanea__detalle_matricula__seccion__curso'
    ).order_by('-probabilidad_riesgo')

    if request.user.es_docente and hasattr(request.user, 'perfil_docente'):
        qs = qs.filter(instantanea__detalle_matricula__seccion__docente=request.user.perfil_docente)

    pdf_buffer = ReporteService.generar_pdf_predicciones_riesgo(modelo_activo, qs, es_sintetico=modelo_activo.es_sintetico)
    registrar_auditoria(request.user, 'Reportes', 'EXPORTAR_PDF_ML', "Descarga de Reporte Confidencial de Predicciones ML", request)

    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="Reporte_Predicciones_Riesgo_ML.pdf"'
    return response

@login_required
@role_required(['ADMIN', 'ESTUDIANTE'])
def estudiante_pdf_view(request, matricula_id):
    matricula = get_object_or_404(Matricula.objects.select_related('estudiante__carrera', 'periodo'), pk=matricula_id)

    if request.user.es_estudiante:
        if not hasattr(request.user, 'perfil_estudiante') or request.user.perfil_estudiante.id != matricula.estudiante_id:
            raise Http404("No autorizado")

    calificaciones = Calificacion.objects.filter(
        detalle_matricula__matricula=matricula
    ).select_related('detalle_matricula__seccion__curso', 'detalle_matricula__seccion__docente')

    seccion_fake = Seccion(
        curso=Curso(nombre="BOLETA OFICIAL DE CALIFICACIONES", codigo="BOLETA", carrera=matricula.estudiante.carrera, ciclo=1, creditos=matricula.total_creditos),
        periodo=matricula.periodo,
        docente=Docente(nombres=matricula.estudiante.nombres, apellidos=matricula.estudiante.apellidos, codigo=matricula.estudiante.codigo),
        codigo_seccion="PERIODO"
    )

    pdf_buffer = ReporteService.generar_pdf_acta_calificaciones(seccion_fake, calificaciones, es_sintetico=True)
    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Boleta_{matricula.codigo}.pdf"'
    return response

@login_required
@role_required('DOCENTE')
def docente_reportes_view(request):
    docente = get_object_or_404(Docente, usuario=request.user)
    secciones = Seccion.objects.filter(docente=docente).select_related('curso', 'periodo')
    modelo_activo = VersionModelo.objects.filter(activo=True).first()

    return render(request, 'reportes/docente_reportes.html', {
        'docente': docente,
        'secciones': secciones,
        'modelo_activo': modelo_activo
    })

@login_required
@role_required('ESTUDIANTE')
def estudiante_reportes_view(request):
    estudiante = get_object_or_404(Estudiante, usuario=request.user)
    matriculas = Matricula.objects.filter(estudiante=estudiante, estado=Matricula.EstadoMatricula.REGISTRADA).select_related('periodo')
    return render(request, 'reportes/estudiante_reportes.html', {
        'estudiante': estudiante,
        'matriculas': matriculas
    })
