from django.urls import path
from . import views

app_name = 'finanzas'

urlpatterns = [
    # Conceptos de Pago
    path('conceptos/', views.concepto_list_view, name='concepto_list'),
    path('conceptos/crear/', views.concepto_create_view, name='concepto_create'),
    path('conceptos/<int:pk>/editar/', views.concepto_update_view, name='concepto_update'),

    # Cuentas por Cobrar
    path('cuentas/', views.cuenta_list_view, name='cuenta_list'),
    path('cuentas/crear/', views.cuenta_create_view, name='cuenta_create'),
    path('cuentas/<int:pk>/editar/', views.cuenta_update_view, name='cuenta_update'),

    # Pagos
    path('pagos/', views.pago_list_view, name='pago_list'),
    path('pagos/crear/', views.pago_create_view, name='pago_create'),
    path('pagos/<int:pk>/editar/', views.pago_update_view, name='pago_update'),

    # Comprobantes
    path('comprobantes/', views.comprobante_list_view, name='comprobante_list'),
    path('comprobantes/crear/', views.comprobante_create_view, name='comprobante_create'),
    path('comprobantes/<int:pk>/editar/', views.comprobante_update_view, name='comprobante_update'),
]
