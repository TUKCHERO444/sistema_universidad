from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator

from .models import Carrera, Curso, Periodo, Docente, Estudiante, Seccion, Facultad, PlanEstudio, PlanCurso, Prerrequisito
from .forms import CarreraForm, CursoForm, PeriodoForm, DocenteForm, EstudianteForm, SeccionForm, FacultadForm, PlanEstudioForm, PlanCursoForm
from cuentas.models import Usuario
from cuentas.decorators import role_required
from cuentas.services import registrar_auditoria
from matriculas.models import Matricula, DetalleMatricula

# --- FACULTADES ---
@login_required
@role_required('ADMIN')
def facultad_list_view(request):
    query = request.GET.get('q', '').strip()
    qs = Facultad.objects.annotate(total_carreras=Count('carreras')).order_by('nombre')
    if query:
        qs = qs.filter(Q(nombre__icontains=query) | Q(codigo__icontains=query))

    paginator = Paginator(qs, 15)
    facultades = paginator.get_page(request.GET.get('page'))
    return render(request, 'academico/facultad_list.html', {'facultades': facultades, 'query': query})


@login_required
@role_required('ADMIN')
def facultad_create_view(request):
    if request.method == 'POST':
        form = FacultadForm(request.POST)
        if form.is_valid():
            facultad = form.save()
            registrar_auditoria(request.user, 'Académico', 'CREAR', f"Facultad {facultad} creada", request)
            messages.success(request, f"Facultad {facultad.nombre} creada exitosamente.")
            return redirect('academico:facultad_list')
    else:
        form = FacultadForm()
    return render(request, 'academico/facultad_form.html', {'form': form, 'titulo': 'Crear Facultad'})


@login_required
@role_required('ADMIN')
def facultad_update_view(request, pk):
    facultad = get_object_or_404(Facultad, pk=pk)
    if request.method == 'POST':
        form = FacultadForm(request.POST, instance=facultad)
        if form.is_valid():
            form.save()
            registrar_auditoria(request.user, 'Académico', 'ACTUALIZAR', f"Facultad {facultad} modificada", request)
            messages.success(request, f"Facultad {facultad.nombre} actualizada correctamente.")
            return redirect('academico:facultad_list')
    else:
        form = FacultadForm(instance=facultad)
    return render(request, 'academico/facultad_form.html', {'form': form, 'titulo': f'Editar Facultad: {facultad.nombre}'})


# --- CARRERAS ---
@login_required
@role_required('ADMIN')
def carrera_list_view(request):
    query = request.GET.get('q', '').strip()
    facultad_id = request.GET.get('facultad', '')
    qs = Carrera.objects.select_related('facultad').annotate(total_cursos=Count('cursos'), total_estudiantes=Count('estudiantes')).order_by('nombre')
    if query:
        qs = qs.filter(Q(nombre__icontains=query) | Q(codigo__icontains=query))
    if facultad_id:
        qs = qs.filter(facultad_id=facultad_id)

    paginator = Paginator(qs, 15)
    carreras = paginator.get_page(request.GET.get('page'))
    facultades = Facultad.objects.filter(estado=True)
    return render(request, 'academico/carrera_list.html', {
        'carreras': carreras,
        'facultades': facultades,
        'facultad_filtro': facultad_id,
        'query': query
    })


@login_required
@role_required('ADMIN')
def carrera_create_view(request):
    if request.method == 'POST':
        form = CarreraForm(request.POST)
        if form.is_valid():
            carrera = form.save()
            registrar_auditoria(request.user, 'Académico', 'CREAR', f"Carrera {carrera} creada", request)
            messages.success(request, f"Carrera {carrera.nombre} creada exitosamente.")
            return redirect('academico:carrera_list')
    else:
        form = CarreraForm()
    return render(request, 'academico/carrera_form.html', {'form': form, 'titulo': 'Crear Carrera Universitaria'})


@login_required
@role_required('ADMIN')
def carrera_update_view(request, pk):
    carrera = get_object_or_404(Carrera, pk=pk)
    if request.method == 'POST':
        form = CarreraForm(request.POST, instance=carrera)
        if form.is_valid():
            form.save()
            registrar_auditoria(request.user, 'Académico', 'ACTUALIZAR', f"Carrera {carrera} modificada", request)
            messages.success(request, f"Carrera {carrera.nombre} actualizada correctamente.")
            return redirect('academico:carrera_list')
    else:
        form = CarreraForm(instance=carrera)
    return render(request, 'academico/carrera_form.html', {'form': form, 'titulo': f'Editar Carrera: {carrera.nombre}'})


# --- PLANES DE ESTUDIO ---
@login_required
@role_required('ADMIN')
def plan_estudio_list_view(request):
    query = request.GET.get('q', '').strip()
    carrera_id = request.GET.get('carrera', '')
    estado = request.GET.get('estado', '')

    qs = PlanEstudio.objects.select_related('carrera').annotate(total_cursos=Count('cursos')).order_by('-year_inicio')
    if query:
        qs = qs.filter(Q(nombre__icontains=query) | Q(codigo__icontains=query))
    if carrera_id:
        qs = qs.filter(carrera_id=carrera_id)
    if estado:
        qs = qs.filter(estado=estado)

    paginator = Paginator(qs, 15)
    planes = paginator.get_page(request.GET.get('page'))
    carreras = Carrera.objects.filter(activo=True)
    return render(request, 'academico/plan_estudio_list.html', {
        'planes': planes,
        'carreras': carreras,
        'carrera_filtro': carrera_id,
        'estado_filtro': estado,
        'query': query
    })


@login_required
@role_required('ADMIN')
def plan_estudio_create_view(request):
    if request.method == 'POST':
        form = PlanEstudioForm(request.POST)
        if form.is_valid():
            plan = form.save()
            registrar_auditoria(request.user, 'Académico', 'CREAR', f"Plan de estudio {plan} creado", request)
            messages.success(request, f"Plan de estudio {plan.nombre} creado exitosamente.")
            return redirect('academico:plan_estudio_list')
    else:
        form = PlanEstudioForm()
    return render(request, 'academico/plan_estudio_form.html', {'form': form, 'titulo': 'Crear Plan de Estudio'})


@login_required
@role_required('ADMIN')
def plan_estudio_update_view(request, pk):
    plan = get_object_or_404(PlanEstudio, pk=pk)
    if request.method == 'POST':
        form = PlanEstudioForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            registrar_auditoria(request.user, 'Académico', 'ACTUALIZAR', f"Plan de estudio {plan} modificado", request)
            messages.success(request, f"Plan de estudio {plan.nombre} actualizado correctamente.")
            return redirect('academico:plan_estudio_list')
    else:
        form = PlanEstudioForm(instance=plan)
    return render(request, 'academico/plan_estudio_form.html', {'form': form, 'titulo': f'Editar Plan de Estudio: {plan.nombre}'})


# --- CURSOS ---
@login_required
@role_required('ADMIN')
def curso_list_view(request):
    query = request.GET.get('q', '').strip()
    carrera_id = request.GET.get('carrera', '')

    qs = Curso.objects.select_related('carrera').order_by('carrera__nombre', 'ciclo', 'nombre')
    if query:
        qs = qs.filter(Q(nombre__icontains=query) | Q(codigo__icontains=query))
    if carrera_id:
        qs = qs.filter(carrera_id=carrera_id)

    paginator = Paginator(qs, 15)
    cursos = paginator.get_page(request.GET.get('page'))
    carreras = Carrera.objects.filter(activo=True)
    return render(request, 'academico/curso_list.html', {
        'cursos': cursos,
        'carreras': carreras,
        'carrera_filtro': carrera_id,
        'query': query
    })


@login_required
@role_required('ADMIN')
def curso_create_view(request):
    if request.method == 'POST':
        form = CursoForm(request.POST)
        if form.is_valid():
            curso = form.save()
            registrar_auditoria(request.user, 'Académico', 'CREAR', f"Curso {curso} creado", request)
            messages.success(request, f"Curso {curso.nombre} creado exitosamente.")
            return redirect('academico:curso_list')
    else:
        form = CursoForm()
    return render(request, 'academico/curso_form.html', {'form': form, 'titulo': 'Crear Asignatura / Curso'})


@login_required
@role_required('ADMIN')
def curso_update_view(request, pk):
    curso = get_object_or_404(Curso, pk=pk)
    if request.method == 'POST':
        form = CursoForm(request.POST, instance=curso)
        if form.is_valid():
            form.save()
            registrar_auditoria(request.user, 'Académico', 'ACTUALIZAR', f"Curso {curso} actualizado", request)
            messages.success(request, f"Curso {curso.nombre} actualizado correctamente.")
            return redirect('academico:curso_list')
    else:
        form = CursoForm(instance=curso)
    return render(request, 'academico/curso_form.html', {'form': form, 'titulo': f'Editar Curso: {curso.nombre}'})


# --- PERIODOS ACADÉMICOS ---
@login_required
@role_required('ADMIN')
def periodo_list_view(request):
    periodos = Periodo.objects.annotate(total_secciones=Count('secciones')).order_by('-fecha_inicio')
    return render(request, 'academico/periodo_list.html', {'periodos': periodos})


@login_required
@role_required('ADMIN')
def periodo_create_view(request):
    if request.method == 'POST':
        form = PeriodoForm(request.POST)
        if form.is_valid():
            periodo = form.save(commit=False)
            if periodo.activo:
                Periodo.objects.filter(activo=True).update(activo=False)
            periodo.save()
            registrar_auditoria(request.user, 'Académico', 'CREAR', f"Periodo {periodo} creado", request)
            messages.success(request, f"Periodo académico {periodo.codigo} creado exitosamente.")
            return redirect('academico:periodo_list')
    else:
        form = PeriodoForm()
    return render(request, 'academico/periodo_form.html', {'form': form, 'titulo': 'Crear Periodo Académico'})


@login_required
@role_required('ADMIN')
def periodo_update_view(request, pk):
    periodo = get_object_or_404(Periodo, pk=pk)
    if request.method == 'POST':
        form = PeriodoForm(request.POST, instance=periodo)
        if form.is_valid():
            per = form.save(commit=False)
            if per.activo:
                Periodo.objects.exclude(pk=per.pk).filter(activo=True).update(activo=False)
            per.save()
            registrar_auditoria(request.user, 'Académico', 'ACTUALIZAR', f"Periodo {per} actualizado", request)
            messages.success(request, f"Periodo {per.codigo} actualizado.")
            return redirect('academico:periodo_list')
    else:
        form = PeriodoForm(instance=periodo)
    return render(request, 'academico/periodo_form.html', {'form': form, 'titulo': f'Editar Periodo: {periodo.codigo}'})


# --- DOCENTES ---
@login_required
@role_required('ADMIN')
def docente_list_view(request):
    query = request.GET.get('q', '').strip()
    qs = Docente.objects.annotate(total_secciones=Count('secciones')).order_by('apellidos')
    if query:
        qs = qs.filter(Q(apellidos__icontains=query) | Q(nombres__icontains=query) | Q(codigo__icontains=query) | Q(dni__icontains=query))

    paginator = Paginator(qs, 15)
    docentes = paginator.get_page(request.GET.get('page'))
    return render(request, 'academico/docente_list.html', {'docentes': docentes, 'query': query})


@login_required
@role_required('ADMIN')
def docente_create_view(request):
    if request.method == 'POST':
        form = DocenteForm(request.POST)
        if form.is_valid():
            docente_data = form.cleaned_data
            username = docente_data['codigo'].lower().replace('-', '_')
            user, _ = Usuario.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': docente_data['nombres'],
                    'last_name': docente_data['apellidos'],
                    'email': docente_data['correo'],
                    'dni': docente_data['dni'],
                    'telefono': docente_data['telefono'],
                    'rol': Usuario.Rol.DOCENTE
                }
            )
            user.set_password('docente123')
            user.save()

            docente = form.save(commit=False)
            docente.usuario = user
            docente.save()

            registrar_auditoria(request.user, 'Académico', 'CREAR', f"Docente {docente} registrado", request)
            messages.success(request, f"Docente {docente.nombre_completo} registrado con éxito (Usuario: {username}).")
            return redirect('academico:docente_list')
    else:
        form = DocenteForm()
    return render(request, 'academico/docente_form.html', {'form': form, 'titulo': 'Registrar Docente'})


# --- ESTUDIANTES ---
@login_required
@role_required('ADMIN')
def estudiante_list_view(request):
    query = request.GET.get('q', '').strip()
    carrera_id = request.GET.get('carrera', '')
    estado = request.GET.get('estado', '')

    qs = Estudiante.objects.select_related('carrera').order_by('apellidos')
    if query:
        qs = qs.filter(Q(apellidos__icontains=query) | Q(nombres__icontains=query) | Q(codigo__icontains=query) | Q(dni__icontains=query))
    if carrera_id:
        qs = qs.filter(carrera_id=carrera_id)
    if estado:
        qs = qs.filter(estado=estado)

    paginator = Paginator(qs, 15)
    estudiantes = paginator.get_page(request.GET.get('page'))
    carreras = Carrera.objects.filter(activo=True)
    return render(request, 'academico/estudiante_list.html', {
        'estudiantes': estudiantes,
        'carreras': carreras,
        'carrera_filtro': carrera_id,
        'estado_filtro': estado,
        'query': query
    })


@login_required
@role_required('ADMIN')
def estudiante_create_view(request):
    if request.method == 'POST':
        form = EstudianteForm(request.POST)
        if form.is_valid():
            est_data = form.cleaned_data
            username = est_data['codigo'].lower().replace('-', '_')
            user, _ = Usuario.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': est_data['nombres'],
                    'last_name': est_data['apellidos'],
                    'email': est_data['correo'],
                    'dni': est_data['dni'],
                    'telefono': est_data['telefono'],
                    'rol': Usuario.Rol.ESTUDIANTE
                }
            )
            user.set_password('estudiante123')
            user.save()

            estudiante = form.save(commit=False)
            estudiante.usuario = user
            estudiante.save()

            registrar_auditoria(request.user, 'Académico', 'CREAR', f"Estudiante {estudiante} registrado", request)
            messages.success(request, f"Estudiante {estudiante.nombre_completo} registrado (Usuario: {username}).")
            return redirect('academico:estudiante_list')
    else:
        form = EstudianteForm()
    return render(request, 'academico/estudiante_form.html', {'form': form, 'titulo': 'Registrar Estudiante'})


# --- SECCIONES ---
@login_required
@role_required('ADMIN')
def seccion_list_view(request):
    periodo_id = request.GET.get('periodo', '')
    curso_id = request.GET.get('curso', '')

    qs = Seccion.objects.select_related('curso', 'periodo', 'docente').order_by('-periodo__fecha_inicio', 'curso__nombre', 'codigo_seccion')
    if periodo_id:
        qs = qs.filter(periodo_id=periodo_id)
    if curso_id:
        qs = qs.filter(curso_id=curso_id)

    paginator = Paginator(qs, 15)
    secciones = paginator.get_page(request.GET.get('page'))
    periodos = Periodo.objects.all()
    cursos = Curso.objects.filter(activo=True)

    return render(request, 'academico/seccion_list.html', {
        'secciones': secciones,
        'periodos': periodos,
        'cursos': cursos,
        'periodo_filtro': periodo_id,
        'curso_filtro': curso_id
    })


@login_required
@role_required('ADMIN')
def seccion_create_view(request):
    if request.method == 'POST':
        form = SeccionForm(request.POST)
        if form.is_valid():
            seccion = form.save()
            registrar_auditoria(request.user, 'Académico', 'CREAR', f"Sección {seccion} creada", request)
            messages.success(request, f"Sección {seccion} creada exitosamente.")
            return redirect('academico:seccion_list')
    else:
        form = SeccionForm()
    return render(request, 'academico/seccion_form.html', {'form': form, 'titulo': 'Crear Sección de Curso'})


# --- VISTAS ESPECÍFICAS DOCENTE / ESTUDIANTE ---
@login_required
@role_required('DOCENTE')
def mis_secciones_view(request):
    docente = get_object_or_404(Docente, usuario=request.user)
    periodo_actual = Periodo.objects.filter(activo=True).first()

    secciones = Seccion.objects.filter(docente=docente).select_related('curso', 'periodo')
    if periodo_actual:
        secciones = secciones.filter(periodo=periodo_actual)

    return render(request, 'academico/mis_secciones.html', {
        'docente': docente,
        'secciones': secciones,
        'periodo_actual': periodo_actual
    })


@login_required
@role_required('ESTUDIANTE')
def mis_cursos_estudiante_view(request):
    estudiante = get_object_or_404(Estudiante, usuario=request.user)
    periodo_actual = Periodo.objects.filter(activo=True).first()

    matricula = None
    cursos_detalles = []
    if periodo_actual:
        matricula = Matricula.objects.filter(
            estudiante=estudiante,
            periodo=periodo_actual,
            estado=Matricula.EstadoMatricula.REGISTRADA
        ).first()
        if matricula:
            cursos_detalles = matricula.detalles.filter(
                estado=DetalleMatricula.EstadoDetalle.INSCRITO
            ).select_related('seccion__curso', 'seccion__docente', 'calificacion')

    return render(request, 'academico/mis_cursos_estudiante.html', {
        'estudiante': estudiante,
        'matricula': matricula,
        'cursos_detalles': cursos_detalles,
        'periodo_actual': periodo_actual
    })
