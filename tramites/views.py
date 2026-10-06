from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator

from .models import TipoTramite, SolicitudTramite, SeguimientoTramite
from .forms import TipoTramiteForm, SolicitudTramiteForm, SeguimientoTramiteForm
from cuentas.decorators import role_required
from cuentas.services import registrar_auditoria


# --- TIPOS DE TRÁMITE ---
@login_required
@role_required('ADMIN')
def tipo_tramite_list_view(request):
    query = request.GET.get('q', '').strip()
    qs = TipoTramite.objects.order_by('nombre')
    if query:
        qs = qs.filter(Q(nombre__icontains=query) | Q(descripcion__icontains=query))

    paginator = Paginator(qs, 15)
    tipos = paginator.get_page(request.GET.get('page'))
    return render(request, 'tramites/tipo_tramite_list.html', {'tipos': tipos, 'query': query})


@login_required
@role_required('ADMIN')
def tipo_tramite_create_view(request):
    if request.method == 'POST':
        form = TipoTramiteForm(request.POST)
        if form.is_valid():
            tipo = form.save()
            registrar_auditoria(request.user, 'Trámites', 'CREAR', f"Tipo de trámite {tipo} creado", request)
            messages.success(request, f"Tipo de trámite {tipo.nombre} creado exitosamente.")
            return redirect('tramites:tipo_tramite_list')
    else:
        form = TipoTramiteForm()
    return render(request, 'tramites/tipo_tramite_form.html', {'form': form, 'titulo': 'Crear Tipo de Trámite'})


@login_required
@role_required('ADMIN')
def tipo_tramite_update_view(request, pk):
    tipo = get_object_or_404(TipoTramite, pk=pk)
    if request.method == 'POST':
        form = TipoTramiteForm(request.POST, instance=tipo)
        if form.is_valid():
            form.save()
            registrar_auditoria(request.user, 'Trámites', 'ACTUALIZAR', f"Tipo de trámite {tipo} modificado", request)
            messages.success(request, f"Tipo de trámite {tipo.nombre} actualizado correctamente.")
            return redirect('tramites:tipo_tramite_list')
    else:
        form = TipoTramiteForm(instance=tipo)
    return render(request, 'tramites/tipo_tramite_form.html', {'form': form, 'titulo': f'Editar Tipo de Trámite: {tipo.nombre}'})


# --- SOLICITUDES DE TRÁMITE ---
@login_required
@role_required('ADMIN')
def solicitud_list_view(request):
    query = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '')
    tipo_id = request.GET.get('tipo', '')

    qs = SolicitudTramite.objects.select_related('estudiante', 'tipo_tramite').order_by('-fecha_solicitud')
    if query:
        qs = qs.filter(Q(id__icontains=query) | Q(estudiante__nombres__icontains=query) | Q(estudiante__apellidos__icontains=query))
    if estado:
        qs = qs.filter(estado=estado)
    if tipo_id:
        qs = qs.filter(tipo_tramite_id=tipo_id)

    paginator = Paginator(qs, 15)
    solicitudes = paginator.get_page(request.GET.get('page'))
    tipos = TipoTramite.objects.filter(estado=True)
    return render(request, 'tramites/solicitud_list.html', {
        'solicitudes': solicitudes,
        'tipos': tipos,
        'estado_filtro': estado,
        'tipo_filtro': tipo_id,
        'query': query
    })


@login_required
@role_required('ADMIN')
def solicitud_detail_view(request, pk):
    solicitud = get_object_or_404(
        SolicitudTramite.objects.select_related('estudiante', 'tipo_tramite'),
        pk=pk
    )
    seguimientos = solicitud.seguimientos.all()
    return render(request, 'tramites/solicitud_detail.html', {
        'solicitud': solicitud,
        'seguimientos': seguimientos
    })


@login_required
@role_required('ADMIN')
def solicitud_create_view(request):
    if request.method == 'POST':
        form = SolicitudTramiteForm(request.POST)
        if form.is_valid():
            solicitud = form.save()
            registrar_auditoria(request.user, 'Trámites', 'CREAR', f"Solicitud #{solicitud.id} creada", request)
            messages.success(request, "Solicitud de trámite creada exitosamente.")
            return redirect('tramites:solicitud_list')
    else:
        form = SolicitudTramiteForm()
    return render(request, 'tramites/solicitud_form.html', {'form': form, 'titulo': 'Crear Solicitud de Trámite'})


@login_required
@role_required('ADMIN')
def solicitud_update_view(request, pk):
    solicitud = get_object_or_404(SolicitudTramite, pk=pk)
    if request.method == 'POST':
        form = SolicitudTramiteForm(request.POST, instance=solicitud)
        if form.is_valid():
            form.save()
            registrar_auditoria(request.user, 'Trámites', 'ACTUALIZAR', f"Solicitud #{solicitud.id} modificada", request)
            messages.success(request, "Solicitud actualizada correctamente.")
            return redirect('tramites:solicitud_list')
    else:
        form = SolicitudTramiteForm(instance=solicitud)
    return render(request, 'tramites/solicitud_form.html', {'form': form, 'titulo': f'Editar Solicitud #{solicitud.id}'})


# --- SEGUIMIENTO DE TRÁMITES ---
@login_required
@role_required('ADMIN')
def seguimiento_list_view(request):
    solicitud_id = request.GET.get('solicitud', '')

    qs = SeguimientoTramite.objects.select_related('solicitud', 'solicitud__estudiante').order_by('-fecha')
    if solicitud_id:
        qs = qs.filter(solicitud_id=solicitud_id)

    paginator = Paginator(qs, 20)
    seguimientos = paginator.get_page(request.GET.get('page'))
    return render(request, 'tramites/seguimiento_list.html', {
        'seguimientos': seguimientos,
        'solicitud_filtro': solicitud_id
    })


@login_required
@role_required('ADMIN')
def seguimiento_create_view(request):
    if request.method == 'POST':
        form = SeguimientoTramiteForm(request.POST)
        if form.is_valid():
            seguimiento = form.save()
            registrar_auditoria(request.user, 'Trámites', 'CREAR', f"Seguimiento de solicitud #{seguimiento.solicitud.id} creado", request)
            messages.success(request, "Seguimiento registrado exitosamente.")
            return redirect('tramites:seguimiento_list')
    else:
        form = SeguimientoTramiteForm()
    return render(request, 'tramites/seguimiento_form.html', {'form': form, 'titulo': 'Registrar Seguimiento'})


@login_required
@role_required('ADMIN')
def seguimiento_update_view(request, pk):
    seguimiento = get_object_or_404(SeguimientoTramite, pk=pk)
    if request.method == 'POST':
        form = SeguimientoTramiteForm(request.POST, instance=seguimiento)
        if form.is_valid():
            form.save()
            registrar_auditoria(request.user, 'Trámites', 'ACTUALIZAR', f"Seguimiento #{seguimiento.id} modificado", request)
            messages.success(request, "Seguimiento actualizado correctamente.")
            return redirect('tramites:seguimiento_list')
    else:
        form = SeguimientoTramiteForm(instance=seguimiento)
    return render(request, 'tramites/seguimiento_form.html', {'form': form, 'titulo': 'Editar Seguimiento'})
