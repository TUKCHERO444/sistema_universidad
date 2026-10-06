from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator

from .models import Aula, Horario, CalendarioAcademico
from .forms import AulaForm, HorarioForm, CalendarioAcademicoForm
from cuentas.decorators import role_required
from cuentas.services import registrar_auditoria


# --- AULAS ---
@login_required
@role_required('ADMIN')
def aula_list_view(request):
    query = request.GET.get('q', '').strip()
    tipo = request.GET.get('tipo', '')

    qs = Aula.objects.annotate(total_horarios=Count('horarios')).order_by('codigo')
    if query:
        qs = qs.filter(Q(codigo__icontains=query) | Q(nombre__icontains=query) | Q(pabellon__icontains=query))
    if tipo:
        qs = qs.filter(tipo=tipo)

    paginator = Paginator(qs, 15)
    aulas = paginator.get_page(request.GET.get('page'))
    return render(request, 'infraestructura/aula_list.html', {
        'aulas': aulas,
        'tipo_filtro': tipo,
        'query': query
    })


@login_required
@role_required('ADMIN')
def aula_create_view(request):
    if request.method == 'POST':
        form = AulaForm(request.POST)
        if form.is_valid():
            aula = form.save()
            registrar_auditoria(request.user, 'Infraestructura', 'CREAR', f"Aula {aula} creada", request)
            messages.success(request, f"Aula {aula.codigo} creada exitosamente.")
            return redirect('infraestructura:aula_list')
    else:
        form = AulaForm()
    return render(request, 'infraestructura/aula_form.html', {'form': form, 'titulo': 'Crear Aula'})


@login_required
@role_required('ADMIN')
def aula_update_view(request, pk):
    aula = get_object_or_404(Aula, pk=pk)
    if request.method == 'POST':
        form = AulaForm(request.POST, instance=aula)
        if form.is_valid():
            form.save()
            registrar_auditoria(request.user, 'Infraestructura', 'ACTUALIZAR', f"Aula {aula} modificada", request)
            messages.success(request, f"Aula {aula.codigo} actualizada correctamente.")
            return redirect('infraestructura:aula_list')
    else:
        form = AulaForm(instance=aula)
    return render(request, 'infraestructura/aula_form.html', {'form': form, 'titulo': f'Editar Aula: {aula.codigo}'})


# --- HORARIOS ---
@login_required
@role_required('ADMIN')
def horario_list_view(request):
    seccion_id = request.GET.get('seccion', '')
    dia = request.GET.get('dia', '')

    qs = Horario.objects.select_related('seccion', 'seccion__curso', 'aula').order_by('dia_semana', 'hora_inicio')
    if seccion_id:
        qs = qs.filter(seccion_id=seccion_id)
    if dia:
        qs = qs.filter(dia_semana=dia)

    paginator = Paginator(qs, 20)
    horarios = paginator.get_page(request.GET.get('page'))
    return render(request, 'infraestructura/horario_list.html', {
        'horarios': horarios,
        'seccion_filtro': seccion_id,
        'dia_filtro': dia
    })


@login_required
@role_required('ADMIN')
def horario_create_view(request):
    if request.method == 'POST':
        form = HorarioForm(request.POST)
        if form.is_valid():
            horario = form.save()
            registrar_auditoria(request.user, 'Infraestructura', 'CREAR', f"Horario {horario} creado", request)
            messages.success(request, "Horario creado exitosamente.")
            return redirect('infraestructura:horario_list')
    else:
        form = HorarioForm()
    return render(request, 'infraestructura/horario_form.html', {'form': form, 'titulo': 'Crear Horario'})


@login_required
@role_required('ADMIN')
def horario_update_view(request, pk):
    horario = get_object_or_404(Horario, pk=pk)
    if request.method == 'POST':
        form = HorarioForm(request.POST, instance=horario)
        if form.is_valid():
            form.save()
            registrar_auditoria(request.user, 'Infraestructura', 'ACTUALIZAR', f"Horario {horario} modificado", request)
            messages.success(request, "Horario actualizado correctamente.")
            return redirect('infraestructura:horario_list')
    else:
        form = HorarioForm(instance=horario)
    return render(request, 'infraestructura/horario_form.html', {'form': form, 'titulo': 'Editar Horario'})


# --- CALENDARIO ACADÉMICO ---
@login_required
@role_required('ADMIN')
def calendario_list_view(request):
    periodo_id = request.GET.get('periodo', '')

    qs = CalendarioAcademico.objects.select_related('periodo').order_by('fecha_inicio')
    if periodo_id:
        qs = qs.filter(periodo_id=periodo_id)

    paginator = Paginator(qs, 20)
    eventos = paginator.get_page(request.GET.get('page'))
    return render(request, 'infraestructura/calendario_list.html', {
        'eventos': eventos,
        'periodo_filtro': periodo_id
    })


@login_required
@role_required('ADMIN')
def calendario_create_view(request):
    if request.method == 'POST':
        form = CalendarioAcademicoForm(request.POST)
        if form.is_valid():
            evento = form.save()
            registrar_auditoria(request.user, 'Infraestructura', 'CREAR', f"Evento {evento.nombre} creado", request)
            messages.success(request, f"Evento {evento.nombre} creado exitosamente.")
            return redirect('infraestructura:calendario_list')
    else:
        form = CalendarioAcademicoForm()
    return render(request, 'infraestructura/calendario_form.html', {'form': form, 'titulo': 'Crear Evento de Calendario'})


@login_required
@role_required('ADMIN')
def calendario_update_view(request, pk):
    evento = get_object_or_404(CalendarioAcademico, pk=pk)
    if request.method == 'POST':
        form = CalendarioAcademicoForm(request.POST, instance=evento)
        if form.is_valid():
            form.save()
            registrar_auditoria(request.user, 'Infraestructura', 'ACTUALIZAR', f"Evento {evento.nombre} modificado", request)
            messages.success(request, "Evento actualizado correctamente.")
            return redirect('infraestructura:calendario_list')
    else:
        form = CalendarioAcademicoForm(instance=evento)
    return render(request, 'infraestructura/calendario_form.html', {'form': form, 'titulo': f'Editar Evento: {evento.nombre}'})
