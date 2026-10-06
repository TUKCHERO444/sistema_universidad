from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.db.models import Q

from .models import Matricula, DetalleMatricula
from .services import MatriculaService
from academico.models import Estudiante, Periodo, Seccion, Carrera
from cuentas.decorators import role_required

@login_required
@role_required('ADMIN')
def matricula_list_view(request):
    query = request.GET.get('q', '').strip()
    periodo_id = request.GET.get('periodo', '')
    estado = request.GET.get('estado', '')

    qs = Matricula.objects.select_related('estudiante', 'periodo', 'estudiante__carrera').order_by('-fecha_registro')
    if query:
        qs = qs.filter(Q(codigo__icontains=query) | Q(estudiante__nombres__icontains=query) | Q(estudiante__apellidos__icontains=query) | Q(estudiante__codigo__icontains=query))
    if periodo_id:
        qs = qs.filter(periodo_id=periodo_id)
    if estado:
        qs = qs.filter(estado=estado)

    paginator = Paginator(qs, 15)
    matriculas = paginator.get_page(request.GET.get('page'))
    periodos = Periodo.objects.all()

    return render(request, 'matriculas/matricula_list.html', {
        'matriculas': matriculas,
        'periodos': periodos,
        'periodo_filtro': periodo_id,
        'estado_filtro': estado,
        'query': query
    })

@login_required
@role_required('ADMIN')
def matricula_create_view(request):
    periodos = Periodo.objects.filter(estado=Periodo.EstadoPeriodo.ABIERTO)
    estudiantes = Estudiante.objects.filter(estado=Estudiante.EstadoEstudiante.ACTIVO).select_related('carrera')

    estudiante_id = request.GET.get('estudiante_id') or request.POST.get('estudiante_id')
    periodo_id = request.GET.get('periodo_id') or request.POST.get('periodo_id')

    secciones_disponibles = []
    estudiante_seleccionado = None
    periodo_seleccionado = None

    if estudiante_id and periodo_id:
        try:
            estudiante_seleccionado = Estudiante.objects.select_related('carrera').get(id=estudiante_id)
            periodo_seleccionado = Periodo.objects.get(id=periodo_id)
            secciones_disponibles = Seccion.objects.filter(
                periodo=periodo_seleccionado,
                curso__carrera=estudiante_seleccionado.carrera,
                activo=True
            ).select_related('curso', 'docente')
        except Exception:
            pass

    if request.method == 'POST' and 'confirmar_matricula' in request.POST:
        secciones_ids = request.POST.getlist('secciones_ids')
        try:
            matricula = MatriculaService.registrar_matricula(
                estudiante_id=int(estudiante_id),
                periodo_id=int(periodo_id),
                secciones_ids=[int(s) for s in secciones_ids],
                usuario_registro=request.user,
                request=request
            )
            messages.success(request, f"Matrícula {matricula.codigo} procesada y registrada exitosamente.")
            return redirect('matriculas:matricula_detail', pk=matricula.pk)
        except ValidationError as e:
            messages.error(request, f"Error de validación académica: {e.message if hasattr(e, 'message') else e}")
        except Exception as e:
            messages.error(request, f"Ocurrió un error al registrar la matrícula: {str(e)}")

    return render(request, 'matriculas/matricula_form.html', {
        'periodos': periodos,
        'estudiantes': estudiantes,
        'estudiante_seleccionado': estudiante_seleccionado,
        'periodo_seleccionado': periodo_seleccionado,
        'secciones_disponibles': secciones_disponibles,
    })

@login_required
def matricula_detail_view(request, pk):
    matricula = get_object_or_404(
        Matricula.objects.select_related('estudiante', 'periodo', 'estudiante__carrera', 'usuario_registro', 'usuario_anulacion'),
        pk=pk
    )

    # Validar acceso
    if request.user.es_estudiante:
        if not hasattr(request.user, 'perfil_estudiante') or request.user.perfil_estudiante.id != matricula.estudiante_id:
            messages.error(request, "No está autorizado para ver esta matrícula.")
            return redirect('cuentas:dashboard')

    detalles = matricula.detalles.select_related('seccion__curso', 'seccion__docente', 'calificacion').all()
    return render(request, 'matriculas/matricula_detail.html', {
        'matricula': matricula,
        'detalles': detalles
    })

@login_required
@role_required('ADMIN')
def matricula_anular_view(request, pk):
    matricula = get_object_or_404(Matricula, pk=pk)
    if request.method == 'POST':
        motivo = request.POST.get('motivo_anulacion', '').strip()
        if not motivo:
            messages.error(request, "Debe especificar un motivo formal para anular la matrícula.")
        else:
            try:
                MatriculaService.anular_matricula(matricula.id, motivo, request.user, request=request)
                messages.success(request, f"La matrícula {matricula.codigo} fue anulada correctamente. Vacantes liberadas.")
                return redirect('matriculas:matricula_detail', pk=matricula.pk)
            except Exception as e:
                messages.error(request, f"Error al anular: {e}")

    return render(request, 'matriculas/matricula_anular.html', {'matricula': matricula})

@login_required
@role_required('ESTUDIANTE')
def mis_matriculas_view(request):
    estudiante = get_object_or_404(Estudiante, usuario=request.user)
    matriculas = Matricula.objects.filter(estudiante=estudiante).select_related('periodo').order_by('-fecha_registro')
    return render(request, 'matriculas/mis_matriculas.html', {
        'estudiante': estudiante,
        'matriculas': matriculas
    })
