from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator

from .models import ModalidadIngreso, ProcesoAdmision, Postulacion, EvaluacionAdmision, ResultadoAdmision
from .forms import ModalidadIngresoForm, ProcesoAdmisionForm, PostulacionForm, EvaluacionAdmisionForm
from cuentas.decorators import role_required
from cuentas.services import registrar_auditoria


# --- MODALIDADES DE INGRESO ---
@login_required
@role_required('ADMIN')
def modalidad_list_view(request):
    query = request.GET.get('q', '').strip()
    qs = ModalidadIngreso.objects.order_by('nombre')
    if query:
        qs = qs.filter(Q(nombre__icontains=query) | Q(descripcion__icontains=query))

    paginator = Paginator(qs, 15)
    modalidades = paginator.get_page(request.GET.get('page'))
    return render(request, 'admision/modalidad_list.html', {'modalidades': modalidades, 'query': query})


@login_required
@role_required('ADMIN')
def modalidad_create_view(request):
    if request.method == 'POST':
        form = ModalidadIngresoForm(request.POST)
        if form.is_valid():
            modalidad = form.save()
            registrar_auditoria(request.user, 'Admisión', 'CREAR', f"Modalidad {modalidad} creada", request)
            messages.success(request, f"Modalidad {modalidad.nombre} creada exitosamente.")
            return redirect('admision:modalidad_list')
    else:
        form = ModalidadIngresoForm()
    return render(request, 'admision/modalidad_form.html', {'form': form, 'titulo': 'Crear Modalidad de Ingreso'})


@login_required
@role_required('ADMIN')
def modalidad_update_view(request, pk):
    modalidad = get_object_or_404(ModalidadIngreso, pk=pk)
    if request.method == 'POST':
        form = ModalidadIngresoForm(request.POST, instance=modalidad)
        if form.is_valid():
            form.save()
            registrar_auditoria(request.user, 'Admisión', 'ACTUALIZAR', f"Modalidad {modalidad} modificada", request)
            messages.success(request, f"Modalidad {modalidad.nombre} actualizada correctamente.")
            return redirect('admision:modalidad_list')
    else:
        form = ModalidadIngresoForm(instance=modalidad)
    return render(request, 'admision/modalidad_form.html', {'form': form, 'titulo': f'Editar Modalidad: {modalidad.nombre}'})


# --- PROCESOS DE ADMISIÓN ---
@login_required
@role_required('ADMIN')
def proceso_list_view(request):
    query = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '')

    qs = ProcesoAdmision.objects.annotate(total_postulaciones=Count('postulaciones')).order_by('-year', '-fecha_inicio')
    if query:
        qs = qs.filter(Q(nombre__icontains=query) | Q(year__icontains=query))
    if estado:
        qs = qs.filter(estado=estado)

    paginator = Paginator(qs, 15)
    procesos = paginator.get_page(request.GET.get('page'))
    return render(request, 'admision/proceso_list.html', {
        'procesos': procesos,
        'estado_filtro': estado,
        'query': query
    })


@login_required
@role_required('ADMIN')
def proceso_create_view(request):
    if request.method == 'POST':
        form = ProcesoAdmisionForm(request.POST)
        if form.is_valid():
            proceso = form.save()
            registrar_auditoria(request.user, 'Admisión', 'CREAR', f"Proceso {proceso} creado", request)
            messages.success(request, f"Proceso de admisión {proceso.nombre} creado exitosamente.")
            return redirect('admision:proceso_list')
    else:
        form = ProcesoAdmisionForm()
    return render(request, 'admision/proceso_form.html', {'form': form, 'titulo': 'Crear Proceso de Admisión'})


@login_required
@role_required('ADMIN')
def proceso_update_view(request, pk):
    proceso = get_object_or_404(ProcesoAdmision, pk=pk)
    if request.method == 'POST':
        form = ProcesoAdmisionForm(request.POST, instance=proceso)
        if form.is_valid():
            form.save()
            registrar_auditoria(request.user, 'Admisión', 'ACTUALIZAR', f"Proceso {proceso} modificado", request)
            messages.success(request, f"Proceso {proceso.nombre} actualizado correctamente.")
            return redirect('admision:proceso_list')
    else:
        form = ProcesoAdmisionForm(instance=proceso)
    return render(request, 'admision/proceso_form.html', {'form': form, 'titulo': f'Editar Proceso: {proceso.nombre}'})


# --- POSTULACIONES ---
@login_required
@role_required('ADMIN')
def postulacion_list_view(request):
    query = request.GET.get('q', '').strip()
    proceso_id = request.GET.get('proceso', '')
    estado = request.GET.get('estado', '')

    qs = Postulacion.objects.select_related('proceso', 'carrera', 'modalidad').order_by('-fecha_postulacion')
    if query:
        qs = qs.filter(Q(id__icontains=query) | Q(carrera__nombre__icontains=query))
    if proceso_id:
        qs = qs.filter(proceso_id=proceso_id)
    if estado:
        qs = qs.filter(estado=estado)

    paginator = Paginator(qs, 15)
    postulaciones = paginator.get_page(request.GET.get('page'))
    procesos = ProcesoAdmision.objects.all()
    return render(request, 'admision/postulacion_list.html', {
        'postulaciones': postulaciones,
        'procesos': procesos,
        'proceso_filtro': proceso_id,
        'estado_filtro': estado,
        'query': query
    })


@login_required
@role_required('ADMIN')
def postulacion_detail_view(request, pk):
    postulacion = get_object_or_404(
        Postulacion.objects.select_related('proceso', 'carrera', 'modalidad', 'resultado'),
        pk=pk
    )
    evaluaciones = postulacion.evaluaciones.all()
    return render(request, 'admision/postulacion_detail.html', {
        'postulacion': postulacion,
        'evaluaciones': evaluaciones
    })


@login_required
@role_required('ADMIN')
def postulacion_create_view(request):
    if request.method == 'POST':
        form = PostulacionForm(request.POST)
        if form.is_valid():
            postulacion = form.save()
            registrar_auditoria(request.user, 'Admisión', 'CREAR', f"Postulación {postulacion.id} creada", request)
            messages.success(request, "Postulación creada exitosamente.")
            return redirect('admision:postulacion_list')
    else:
        form = PostulacionForm()
    return render(request, 'admision/postulacion_form.html', {'form': form, 'titulo': 'Crear Postulación'})


@login_required
@role_required('ADMIN')
def postulacion_update_view(request, pk):
    postulacion = get_object_or_404(Postulacion, pk=pk)
    if request.method == 'POST':
        form = PostulacionForm(request.POST, instance=postulacion)
        if form.is_valid():
            form.save()
            registrar_auditoria(request.user, 'Admisión', 'ACTUALIZAR', f"Postulación {postulacion.id} modificada", request)
            messages.success(request, "Postulación actualizada correctamente.")
            return redirect('admision:postulacion_list')
    else:
        form = PostulacionForm(instance=postulacion)
    return render(request, 'admision/postulacion_form.html', {'form': form, 'titulo': f'Editar Postulación #{postulacion.id}'})


# --- EVALUACIONES DE ADMISIÓN ---
@login_required
@role_required('ADMIN')
def evaluacion_list_view(request):
    postulacion_id = request.GET.get('postulacion', '')

    qs = EvaluacionAdmision.objects.select_related('postulacion', 'postulacion__carrera').order_by('-fecha')
    if postulacion_id:
        qs = qs.filter(postulacion_id=postulacion_id)

    paginator = Paginator(qs, 20)
    evaluaciones = paginator.get_page(request.GET.get('page'))
    return render(request, 'admision/evaluacion_list.html', {
        'evaluaciones': evaluaciones,
        'postulacion_filtro': postulacion_id
    })


@login_required
@role_required('ADMIN')
def evaluacion_create_view(request):
    if request.method == 'POST':
        form = EvaluacionAdmisionForm(request.POST)
        if form.is_valid():
            evaluacion = form.save()
            registrar_auditoria(request.user, 'Admisión', 'CREAR', f"Evaluación {evaluacion.nombre} creada", request)
            messages.success(request, "Evaluación creada exitosamente.")
            return redirect('admision:evaluacion_list')
    else:
        form = EvaluacionAdmisionForm()
    return render(request, 'admision/evaluacion_form.html', {'form': form, 'titulo': 'Crear Evaluación de Admisión'})


@login_required
@role_required('ADMIN')
def evaluacion_update_view(request, pk):
    evaluacion = get_object_or_404(EvaluacionAdmision, pk=pk)
    if request.method == 'POST':
        form = EvaluacionAdmisionForm(request.POST, instance=evaluacion)
        if form.is_valid():
            form.save()
            registrar_auditoria(request.user, 'Admisión', 'ACTUALIZAR', f"Evaluación {evaluacion.nombre} modificada", request)
            messages.success(request, "Evaluación actualizada correctamente.")
            return redirect('admision:evaluacion_list')
    else:
        form = EvaluacionAdmisionForm(instance=evaluacion)
    return render(request, 'admision/evaluacion_form.html', {'form': form, 'titulo': f'Editar Evaluación: {evaluacion.nombre}'})
