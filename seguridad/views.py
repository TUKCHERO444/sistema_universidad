from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator

from .models import Rol, Permiso, RolPermiso
from .forms import RolForm, PermisoForm
from cuentas.decorators import role_required
from cuentas.services import registrar_auditoria


# --- ROLES ---
@login_required
@role_required('ADMIN')
def rol_list_view(request):
    query = request.GET.get('q', '').strip()
    qs = Rol.objects.annotate(total_permisos=Count('permisos')).order_by('nombre')
    if query:
        qs = qs.filter(Q(nombre__icontains=query) | Q(descripcion__icontains=query))

    paginator = Paginator(qs, 15)
    roles = paginator.get_page(request.GET.get('page'))
    return render(request, 'seguridad/rol_list.html', {'roles': roles, 'query': query})


@login_required
@role_required('ADMIN')
def rol_create_view(request):
    if request.method == 'POST':
        form = RolForm(request.POST)
        if form.is_valid():
            rol = form.save()
            registrar_auditoria(request.user, 'Seguridad', 'CREAR', f"Rol {rol} creado", request)
            messages.success(request, f"Rol {rol.nombre} creado exitosamente.")
            return redirect('seguridad:rol_list')
    else:
        form = RolForm()
    return render(request, 'seguridad/rol_form.html', {'form': form, 'titulo': 'Crear Rol'})


@login_required
@role_required('ADMIN')
def rol_update_view(request, pk):
    rol = get_object_or_404(Rol, pk=pk)
    if request.method == 'POST':
        form = RolForm(request.POST, instance=rol)
        if form.is_valid():
            form.save()
            registrar_auditoria(request.user, 'Seguridad', 'ACTUALIZAR', f"Rol {rol} modificado", request)
            messages.success(request, f"Rol {rol.nombre} actualizado correctamente.")
            return redirect('seguridad:rol_list')
    else:
        form = RolForm(instance=rol)
    return render(request, 'seguridad/rol_form.html', {'form': form, 'titulo': f'Editar Rol: {rol.nombre}'})


# --- PERMISOS ---
@login_required
@role_required('ADMIN')
def permiso_list_view(request):
    query = request.GET.get('q', '').strip()
    qs = Permiso.objects.annotate(total_roles=Count('roles')).order_by('codigo')
    if query:
        qs = qs.filter(Q(codigo__icontains=query) | Q(nombre__icontains=query))

    paginator = Paginator(qs, 15)
    permisos = paginator.get_page(request.GET.get('page'))
    return render(request, 'seguridad/permiso_list.html', {'permisos': permisos, 'query': query})


@login_required
@role_required('ADMIN')
def permiso_create_view(request):
    if request.method == 'POST':
        form = PermisoForm(request.POST)
        if form.is_valid():
            permiso = form.save()
            registrar_auditoria(request.user, 'Seguridad', 'CREAR', f"Permiso {permiso} creado", request)
            messages.success(request, f"Permiso {permiso.nombre} creado exitosamente.")
            return redirect('seguridad:permiso_list')
    else:
        form = PermisoForm()
    return render(request, 'seguridad/permiso_form.html', {'form': form, 'titulo': 'Crear Permiso'})


@login_required
@role_required('ADMIN')
def permiso_update_view(request, pk):
    permiso = get_object_or_404(Permiso, pk=pk)
    if request.method == 'POST':
        form = PermisoForm(request.POST, instance=permiso)
        if form.is_valid():
            form.save()
            registrar_auditoria(request.user, 'Seguridad', 'ACTUALIZAR', f"Permiso {permiso} modificado", request)
            messages.success(request, f"Permiso {permiso.nombre} actualizado correctamente.")
            return redirect('seguridad:permiso_list')
    else:
        form = PermisoForm(instance=permiso)
    return render(request, 'seguridad/permiso_form.html', {'form': form, 'titulo': f'Editar Permiso: {permiso.nombre}'})
