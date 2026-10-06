from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.core.paginator import Paginator

from .models import ConceptoPago, CuentaCobrar, Pago, Comprobante
from .forms import ConceptoPagoForm, CuentaCobrarForm, PagoForm, ComprobanteForm
from cuentas.decorators import role_required
from cuentas.services import registrar_auditoria


# --- CONCEPTOS DE PAGO ---
@login_required
@role_required('ADMIN')
def concepto_list_view(request):
    query = request.GET.get('q', '').strip()
    qs = ConceptoPago.objects.order_by('codigo')
    if query:
        qs = qs.filter(Q(codigo__icontains=query) | Q(nombre__icontains=query))

    paginator = Paginator(qs, 15)
    conceptos = paginator.get_page(request.GET.get('page'))
    return render(request, 'finanzas/concepto_list.html', {'conceptos': conceptos, 'query': query})


@login_required
@role_required('ADMIN')
def concepto_create_view(request):
    if request.method == 'POST':
        form = ConceptoPagoForm(request.POST)
        if form.is_valid():
            concepto = form.save()
            registrar_auditoria(request.user, 'Finanzas', 'CREAR', f"Concepto {concepto} creado", request)
            messages.success(request, f"Concepto {concepto.nombre} creado exitosamente.")
            return redirect('finanzas:concepto_list')
    else:
        form = ConceptoPagoForm()
    return render(request, 'finanzas/concepto_form.html', {'form': form, 'titulo': 'Crear Concepto de Pago'})


@login_required
@role_required('ADMIN')
def concepto_update_view(request, pk):
    concepto = get_object_or_404(ConceptoPago, pk=pk)
    if request.method == 'POST':
        form = ConceptoPagoForm(request.POST, instance=concepto)
        if form.is_valid():
            form.save()
            registrar_auditoria(request.user, 'Finanzas', 'ACTUALIZAR', f"Concepto {concepto} modificado", request)
            messages.success(request, f"Concepto {concepto.nombre} actualizado correctamente.")
            return redirect('finanzas:concepto_list')
    else:
        form = ConceptoPagoForm(instance=concepto)
    return render(request, 'finanzas/concepto_form.html', {'form': form, 'titulo': f'Editar Concepto: {concepto.nombre}'})


# --- CUENTAS POR COBRAR ---
@login_required
@role_required('ADMIN')
def cuenta_list_view(request):
    query = request.GET.get('q', '').strip()
    estado = request.GET.get('estado', '')
    estudiante_id = request.GET.get('estudiante', '')

    qs = CuentaCobrar.objects.select_related('estudiante', 'periodo', 'concepto').order_by('-fecha_emision')
    if query:
        qs = qs.filter(Q(id__icontains=query) | Q(estudiante__nombres__icontains=query) | Q(estudiante__apellidos__icontains=query))
    if estado:
        qs = qs.filter(estado=estado)
    if estudiante_id:
        qs = qs.filter(estudiante_id=estudiante_id)

    paginator = Paginator(qs, 15)
    cuentas = paginator.get_page(request.GET.get('page'))
    return render(request, 'finanzas/cuenta_list.html', {
        'cuentas': cuentas,
        'estado_filtro': estado,
        'estudiante_filtro': estudiante_id,
        'query': query
    })


@login_required
@role_required('ADMIN')
def cuenta_create_view(request):
    if request.method == 'POST':
        form = CuentaCobrarForm(request.POST)
        if form.is_valid():
            cuenta = form.save()
            registrar_auditoria(request.user, 'Finanzas', 'CREAR', f"Cuenta por cobrar #{cuenta.id} creada", request)
            messages.success(request, f"Cuenta por cobrar creada exitosamente.")
            return redirect('finanzas:cuenta_list')
    else:
        form = CuentaCobrarForm()
    return render(request, 'finanzas/cuenta_form.html', {'form': form, 'titulo': 'Crear Cuenta por Cobrar'})


@login_required
@role_required('ADMIN')
def cuenta_update_view(request, pk):
    cuenta = get_object_or_404(CuentaCobrar, pk=pk)
    if request.method == 'POST':
        form = CuentaCobrarForm(request.POST, instance=cuenta)
        if form.is_valid():
            form.save()
            registrar_auditoria(request.user, 'Finanzas', 'ACTUALIZAR', f"Cuenta #{cuenta.id} modificada", request)
            messages.success(request, "Cuenta por cobrar actualizada correctamente.")
            return redirect('finanzas:cuenta_list')
    else:
        form = CuentaCobrarForm(instance=cuenta)
    return render(request, 'finanzas/cuenta_form.html', {'form': form, 'titulo': f'Editar Cuenta #{cuenta.id}'})


# --- PAGOS ---
@login_required
@role_required('ADMIN')
def pago_list_view(request):
    query = request.GET.get('q', '').strip()
    metodo = request.GET.get('metodo', '')
    estado = request.GET.get('estado', '')

    qs = Pago.objects.select_related('cuenta', 'cuenta__estudiante').order_by('-fecha_pago')
    if query:
        qs = qs.filter(Q(id__icontains=query) | Q(cuenta__estudiante__nombres__icontains=query) | Q(numero_operacion__icontains=query))
    if metodo:
        qs = qs.filter(metodo=metodo)
    if estado:
        qs = qs.filter(estado=estado)

    paginator = Paginator(qs, 15)
    pagos = paginator.get_page(request.GET.get('page'))
    return render(request, 'finanzas/pago_list.html', {
        'pagos': pagos,
        'metodo_filtro': metodo,
        'estado_filtro': estado,
        'query': query
    })


@login_required
@role_required('ADMIN')
def pago_create_view(request):
    if request.method == 'POST':
        form = PagoForm(request.POST)
        if form.is_valid():
            pago = form.save()
            registrar_auditoria(request.user, 'Finanzas', 'CREAR', f"Pago #{pago.id} registrado", request)
            messages.success(request, f"Pago registrado exitosamente.")
            return redirect('finanzas:pago_list')
    else:
        form = PagoForm()
    return render(request, 'finanzas/pago_form.html', {'form': form, 'titulo': 'Registrar Pago'})


@login_required
@role_required('ADMIN')
def pago_update_view(request, pk):
    pago = get_object_or_404(Pago, pk=pk)
    if request.method == 'POST':
        form = PagoForm(request.POST, instance=pago)
        if form.is_valid():
            form.save()
            registrar_auditoria(request.user, 'Finanzas', 'ACTUALIZAR', f"Pago #{pago.id} modificado", request)
            messages.success(request, "Pago actualizado correctamente.")
            return redirect('finanzas:pago_list')
    else:
        form = PagoForm(instance=pago)
    return render(request, 'finanzas/pago_form.html', {'form': form, 'titulo': f'Editar Pago #{pago.id}'})


# --- COMPROBANTES ---
@login_required
@role_required('ADMIN')
def comprobante_list_view(request):
    query = request.GET.get('q', '').strip()
    tipo = request.GET.get('tipo', '')

    qs = Comprobante.objects.select_related('pago', 'pago__cuenta__estudiante').order_by('-fecha_emision')
    if query:
        qs = qs.filter(Q(serie__icontains=query) | Q(numero__icontains=query))
    if tipo:
        qs = qs.filter(tipo=tipo)

    paginator = Paginator(qs, 15)
    comprobantes = paginator.get_page(request.GET.get('page'))
    return render(request, 'finanzas/comprobante_list.html', {
        'comprobantes': comprobantes,
        'tipo_filtro': tipo,
        'query': query
    })


@login_required
@role_required('ADMIN')
def comprobante_create_view(request):
    if request.method == 'POST':
        form = ComprobanteForm(request.POST)
        if form.is_valid():
            comprobante = form.save()
            registrar_auditoria(request.user, 'Finanzas', 'CREAR', f"Comprobante {comprobante} creado", request)
            messages.success(request, "Comprobante creado exitosamente.")
            return redirect('finanzas:comprobante_list')
    else:
        form = ComprobanteForm()
    return render(request, 'finanzas/comprobante_form.html', {'form': form, 'titulo': 'Crear Comprobante'})


@login_required
@role_required('ADMIN')
def comprobante_update_view(request, pk):
    comprobante = get_object_or_404(Comprobante, pk=pk)
    if request.method == 'POST':
        form = ComprobanteForm(request.POST, instance=comprobante)
        if form.is_valid():
            form.save()
            registrar_auditoria(request.user, 'Finanzas', 'ACTUALIZAR', f"Comprobante {comprobante} modificado", request)
            messages.success(request, "Comprobante actualizado correctamente.")
            return redirect('finanzas:comprobante_list')
    else:
        form = ComprobanteForm(instance=comprobante)
    return render(request, 'finanzas/comprobante_form.html', {'form': form, 'titulo': f'Editar Comprobante'})
