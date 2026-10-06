from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator

from .models import Egreso, GradoAcademico, Titulacion
from .forms import EgresoForm, GradoAcademicoForm, TitulacionForm
from cuentas.decorators import role_required
from cuentas.services import registrar_auditoria


# --- EGRESOS ---
@login_required
@role_required('ADMIN')
def egreso_list_view(request):
    query = request.GET.get('q', '').strip()
    qs = Egreso.objects.select_related('estudiante', 'estudiante__carrera').order_by('-fecha_egreso')
    if query:
        qs = qs.filter(Q(estudiante__nombres__icontains=query) | Q(estudiante__apellidos__icontains=query) | Q(estudiante__codigo__icontains=query))

    paginator = Paginator(qs, 15)
    egresos = paginator.get_page(request.GET.get('page'))
    return render(request, 'egresados/egreso_list.html', {'egresos': egresos, 'query': query})


@login_required
@role_required('ADMIN')
def egreso_create_view(request):
    if request.method == 'POST':
        form = EgresoForm(request.POST)
        if form.is_valid():
            egreso = form.save()
            registrar_auditoria(request.user, 'Egresados', 'CREAR', f"Egreso de {egreso.estudiante} registrado", request)
            messages.success(request, f"Egreso de {egreso.estudiante.nombre_completo} registrado exitosamente.")
            return redirect('egresados:egreso_list')
    else:
        form = EgresoForm()
    return render(request, 'egresados/egreso_form.html', {'form': form, 'titulo': 'Registrar Egreso'})


@login_required
@role_required('ADMIN')
def egreso_update_view(request, pk):
    egreso = get_object_or_404(Egreso, pk=pk)
    if request.method == 'POST':
        form = EgresoForm(request.POST, instance=egreso)
        if form.is_valid():
            form.save()
            registrar_auditoria(request.user, 'Egresados', 'ACTUALIZAR', f"Egreso de {egreso.estudiante} modificado", request)
            messages.success(request, "Egreso actualizado correctamente.")
            return redirect('egresados:egreso_list')
    else:
        form = EgresoForm(instance=egreso)
    return render(request, 'egresados/egreso_form.html', {'form': form, 'titulo': f'Editar Egreso: {egreso.estudiante.nombre_completo}'})


# --- GRADOS ACADÉMICOS ---
@login_required
@role_required('ADMIN')
def grado_list_view(request):
    query = request.GET.get('q', '').strip()
    tipo = request.GET.get('tipo', '')

    qs = GradoAcademico.objects.select_related('egreso', 'egreso__estudiante').order_by('-fecha_otorgamiento')
    if query:
        qs = qs.filter(Q(nombre__icontains=query) | Q(egreso__estudiante__nombres__icontains=query) | Q(egreso__estudiante__apellidos__icontains=query))
    if tipo:
        qs = qs.filter(tipo=tipo)

    paginator = Paginator(qs, 15)
    grados = paginator.get_page(request.GET.get('page'))
    return render(request, 'egresados/grado_list.html', {
        'grados': grados,
        'tipo_filtro': tipo,
        'query': query
    })


@login_required
@role_required('ADMIN')
def grado_create_view(request):
    if request.method == 'POST':
        form = GradoAcademicoForm(request.POST)
        if form.is_valid():
            grado = form.save()
            registrar_auditoria(request.user, 'Egresados', 'CREAR', f"Grado {grado} otorgado", request)
            messages.success(request, f"Grado académico {grado.nombre} registrado exitosamente.")
            return redirect('egresados:grado_list')
    else:
        form = GradoAcademicoForm()
    return render(request, 'egresados/grado_form.html', {'form': form, 'titulo': 'Registrar Grado Académico'})


@login_required
@role_required('ADMIN')
def grado_update_view(request, pk):
    grado = get_object_or_404(GradoAcademico, pk=pk)
    if request.method == 'POST':
        form = GradoAcademicoForm(request.POST, instance=grado)
        if form.is_valid():
            form.save()
            registrar_auditoria(request.user, 'Egresados', 'ACTUALIZAR', f"Grado {grado} modificado", request)
            messages.success(request, "Grado académico actualizado correctamente.")
            return redirect('egresados:grado_list')
    else:
        form = GradoAcademicoForm(instance=grado)
    return render(request, 'egresados/grado_form.html', {'form': form, 'titulo': f'Editar Grado: {grado.nombre}'})


# --- TITULACIONES ---
@login_required
@role_required('ADMIN')
def titulacion_list_view(request):
    query = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '')

    qs = Titulacion.objects.select_related('egreso', 'egreso__estudiante').order_by('-fecha_sustentacion')
    if query:
        qs = qs.filter(Q(titulo__icontains=query) | Q(egreso__estudiante__nombres__icontains=query) | Q(egreso__estudiante__apellidos__icontains=query))
    if estado:
        qs = qs.filter(estado=estado)

    paginator = Paginator(qs, 15)
    titulaciones = paginator.get_page(request.GET.get('page'))
    return render(request, 'egresados/titulacion_list.html', {
        'titulaciones': titulaciones,
        'estado_filtro': estado,
        'query': query
    })


@login_required
@role_required('ADMIN')
def titulacion_create_view(request):
    if request.method == 'POST':
        form = TitulacionForm(request.POST)
        if form.is_valid():
            titulacion = form.save()
            registrar_auditoria(request.user, 'Egresados', 'CREAR', f"Titulación {titulacion.titulo} registrada", request)
            messages.success(request, f"Titulación registrada exitosamente.")
            return redirect('egresados:titulacion_list')
    else:
        form = TitulacionForm()
    return render(request, 'egresados/titulacion_form.html', {'form': form, 'titulo': 'Registrar Titulación'})


@login_required
@role_required('ADMIN')
def titulacion_update_view(request, pk):
    titulacion = get_object_or_404(Titulacion, pk=pk)
    if request.method == 'POST':
        form = TitulacionForm(request.POST, instance=titulacion)
        if form.is_valid():
            form.save()
            registrar_auditoria(request.user, 'Egresados', 'ACTUALIZAR', f"Titulación {titulacion.titulo} modificada", request)
            messages.success(request, "Titulación actualizada correctamente.")
            return redirect('egresados:titulacion_list')
    else:
        form = TitulacionForm(instance=titulacion)
    return render(request, 'egresados/titulacion_form.html', {'form': form, 'titulo': f'Editar Titulación: {titulacion.titulo}'})
