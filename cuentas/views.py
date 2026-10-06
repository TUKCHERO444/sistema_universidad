from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Avg, Q
from django.core.paginator import Paginator

from .models import Usuario, RegistroAuditoria
from .forms import CustomAuthenticationForm, UsuarioCreateForm, UsuarioUpdateForm
from .decorators import role_required
from .services import registrar_auditoria

from academico.models import Estudiante, Docente, Carrera, Curso, Periodo, Seccion
from matriculas.models import Matricula, DetalleMatricula
from calificaciones.models import Calificacion
from asistencia.models import SesionClase, Asistencia
from predicciones.models import PrediccionEstudiante, VersionModelo

def login_view(request):
    if request.user.is_authenticated:
        return redirect('cuentas:dashboard')

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        username = request.POST.get('username')
        
        # Verificar bloqueo temporal por intentos
        usuario_existente = Usuario.objects.filter(Q(username=username) | Q(email=username) | Q(dni=username)).first()
        if usuario_existente and usuario_existente.bloqueado_hasta and usuario_existente.bloqueado_hasta > timezone.now():
            messages.error(request, f"Cuenta bloqueada temporalmente por intentos fallidos. Intente después de {usuario_existente.bloqueado_hasta.strftime('%H:%M')}.")
            return render(request, 'cuentas/login.html', {'form': form})

        if form.is_valid():
            user = form.get_user()
            user.intentos_fallidos = 0
            user.bloqueado_hasta = None
            user.save()
            login(request, user)
            registrar_auditoria(user, 'Autenticación', 'LOGIN', f"Inicio de sesión exitoso desde IP", request)
            return redirect('cuentas:dashboard')
        else:
            if usuario_existente:
                usuario_existente.intentos_fallidos += 1
                if usuario_existente.intentos_fallidos >= 5:
                    usuario_existente.bloqueado_hasta = timezone.now() + timezone.timedelta(minutes=15)
                    messages.error(request, "Ha superado el límite de 5 intentos. Cuenta bloqueada por 15 minutos.")
                usuario_existente.save()
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = CustomAuthenticationForm()

    return render(request, 'cuentas/login.html', {'form': form})

def logout_view(request):
    if request.user.is_authenticated:
        registrar_auditoria(request.user, 'Autenticación', 'LOGOUT', "Cierre de sesión de usuario", request)
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('cuentas:login')

@login_required
def dashboard_view(request):
    usuario = request.user
    periodo_actual = Periodo.objects.filter(activo=True).first()

    contexto = {
        'periodo_actual': periodo_actual,
    }

    if usuario.es_admin:
        # Métricas institucionales
        contexto['total_estudiantes'] = Estudiante.objects.filter(estado=Estudiante.EstadoEstudiante.ACTIVO).count()
        contexto['total_docentes'] = Docente.objects.filter(activo=True).count()
        contexto['total_carreras'] = Carrera.objects.filter(activo=True).count()
        contexto['total_cursos'] = Curso.objects.filter(activo=True).count()
        
        if periodo_actual:
            contexto['total_matriculas'] = Matricula.objects.filter(periodo=periodo_actual, estado=Matricula.EstadoMatricula.REGISTRADA).count()
            contexto['total_secciones'] = Seccion.objects.filter(periodo=periodo_actual, activo=True).count()
        else:
            contexto['total_matriculas'] = 0
            contexto['total_secciones'] = 0

        # Alertas críticas de riesgo predictivo si hay modelo
        modelo_activo = VersionModelo.objects.filter(activo=True).first()
        contexto['modelo_activo'] = modelo_activo
        if modelo_activo:
            contexto['alertas_alto_riesgo'] = PrediccionEstudiante.objects.filter(
                version_modelo=modelo_activo,
                nivel_riesgo=PrediccionEstudiante.NivelRiesgo.ALTO
            ).select_related('instantanea__detalle_matricula__matricula__estudiante', 'instantanea__detalle_matricula__seccion__curso')[:6]
        
        contexto['ultimas_matriculas'] = Matricula.objects.select_related('estudiante', 'periodo').order_by('-fecha_registro')[:5]
        return render(request, 'cuentas/dashboard_admin.html', contexto)

    elif usuario.es_docente:
        perfil_docente = getattr(usuario, 'perfil_docente', None)
        if perfil_docente:
            secciones_docente = Seccion.objects.filter(docente=perfil_docente)
            if periodo_actual:
                secciones_docente = secciones_docente.filter(periodo=periodo_actual)
            
            contexto['secciones'] = secciones_docente.select_related('curso', 'periodo')
            contexto['total_secciones'] = secciones_docente.count()
            
            # Conteo total de alumnos asignados
            detalles = DetalleMatricula.objects.filter(
                seccion__in=secciones_docente,
                matricula__estado=Matricula.EstadoMatricula.REGISTRADA,
                estado=DetalleMatricula.EstadoDetalle.INSCRITO
            )
            contexto['total_estudiantes_asignados'] = detalles.count()
            
            # Alertas tempranas en sus cursos
            contexto['alertas_estudiantes'] = PrediccionEstudiante.objects.filter(
                instantanea__detalle_matricula__seccion__in=secciones_docente,
                nivel_riesgo__in=[PrediccionEstudiante.NivelRiesgo.ALTO, PrediccionEstudiante.NivelRiesgo.MEDIO]
            ).select_related('instantanea__detalle_matricula__matricula__estudiante', 'instantanea__detalle_matricula__seccion__curso')[:8]
        return render(request, 'cuentas/dashboard_docente.html', contexto)

    elif usuario.es_estudiante:
        perfil_estudiante = getattr(usuario, 'perfil_estudiante', None)
        if perfil_estudiante:
            matricula_activa = None
            if periodo_actual:
                matricula_activa = Matricula.objects.filter(
                    estudiante=perfil_estudiante,
                    periodo=periodo_actual,
                    estado=Matricula.EstadoMatricula.REGISTRADA
                ).first()

            contexto['estudiante'] = perfil_estudiante
            contexto['matricula_activa'] = matricula_activa
            if matricula_activa:
                contexto['cursos_inscritos'] = matricula_activa.detalles.filter(
                    estado=DetalleMatricula.EstadoDetalle.INSCRITO
                ).select_related('seccion__curso', 'seccion__docente', 'calificacion')
            else:
                contexto['cursos_inscritos'] = []
        return render(request, 'cuentas/dashboard_estudiante.html', contexto)

    return render(request, 'cuentas/dashboard_admin.html', contexto)

@login_required
def perfil_view(request):
    usuario = request.user
    return render(request, 'cuentas/perfil.html', {'usuario': usuario})

@login_required
@role_required('ADMIN')
def usuario_list_view(request):
    query = request.GET.get('q', '').strip()
    rol = request.GET.get('rol', '').strip()

    qs = Usuario.objects.all().order_by('username')
    if query:
        qs = qs.filter(Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(dni__icontains=query))
    if rol:
        qs = qs.filter(rol=rol)

    paginator = Paginator(qs, 15)
    page_number = request.GET.get('page')
    usuarios = paginator.get_page(page_number)

    return render(request, 'cuentas/usuario_list.html', {
        'usuarios': usuarios,
        'query': query,
        'rol_filtro': rol
    })

@login_required
@role_required('ADMIN')
def usuario_create_view(request):
    if request.method == 'POST':
        form = UsuarioCreateForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            registrar_auditoria(request.user, 'Usuarios', 'CREAR', f"Usuario {usuario.username} creado con rol {usuario.rol}", request)
            messages.success(request, f"Usuario {usuario.username} creado exitosamente.")
            return redirect('cuentas:usuario_list')
    else:
        form = UsuarioCreateForm()
    return render(request, 'cuentas/usuario_form.html', {'form': form, 'titulo': 'Crear Usuario'})

@login_required
@role_required('ADMIN')
def usuario_update_view(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        form = UsuarioUpdateForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            registrar_auditoria(request.user, 'Usuarios', 'ACTUALIZAR', f"Usuario {usuario.username} modificado", request)
            messages.success(request, f"Usuario {usuario.username} actualizado correctamente.")
            return redirect('cuentas:usuario_list')
    else:
        form = UsuarioUpdateForm(instance=usuario)
    return render(request, 'cuentas/usuario_form.html', {'form': form, 'titulo': f'Editar Usuario: {usuario.username}'})

@login_required
@role_required('ADMIN')
def auditoria_list_view(request):
    modulo = request.GET.get('modulo', '').strip()
    query = request.GET.get('q', '').strip()

    qs = RegistroAuditoria.objects.select_related('usuario').all()
    if modulo:
        qs = qs.filter(modulo=modulo)
    if query:
        qs = qs.filter(Q(descripcion__icontains=query) | Q(usuario__username__icontains=query))

    paginator = Paginator(qs, 25)
    page_number = request.GET.get('page')
    auditorias = paginator.get_page(page_number)

    modulos_disponibles = RegistroAuditoria.objects.values_list('modulo', flat=True).distinct()

    return render(request, 'cuentas/auditoria_list.html', {
        'auditorias': auditorias,
        'modulo_filtro': modulo,
        'query': query,
        'modulos_disponibles': modulos_disponibles
    })
