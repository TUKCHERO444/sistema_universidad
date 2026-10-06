from django.db import models
from django.utils.translation import gettext_lazy as _
from academico.models import Estudiante, Periodo


class ConceptoPago(models.Model):
    codigo = models.CharField(max_length=20, unique=True, verbose_name=_('Código'))
    nombre = models.CharField(max_length=100, verbose_name=_('Nombre'))
    descripcion = models.TextField(blank=True, null=True, verbose_name=_('Descripción'))
    estado = models.BooleanField(default=True, verbose_name=_('Estado'))

    class Meta:
        verbose_name = _('Concepto de Pago')
        verbose_name_plural = _('Conceptos de Pago')
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class CuentaCobrar(models.Model):
    class EstadoCuenta(models.TextChoices):
        PENDIENTE = 'PENDIENTE', _('Pendiente')
        PARCIAL = 'PARCIAL', _('Parcial')
        PAGADO = 'PAGADO', _('Pagado')
        ANULADO = 'ANULADO', _('Anulado')

    estudiante = models.ForeignKey(Estudiante, on_delete=models.PROTECT, related_name='cuentas_cobrar', verbose_name=_('Estudiante'))
    periodo = models.ForeignKey(Periodo, on_delete=models.SET_NULL, blank=True, null=True, related_name='cuentas_cobrar', verbose_name=_('Periodo Académico'))
    concepto = models.ForeignKey(ConceptoPago, on_delete=models.PROTECT, related_name='cuentas', verbose_name=_('Concepto de Pago'))
    monto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Monto'))
    descuento = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name=_('Descuento'))
    fecha_emision = models.DateField(verbose_name=_('Fecha de Emisión'))
    fecha_vencimiento = models.DateField(blank=True, null=True, verbose_name=_('Fecha de Vencimiento'))
    estado = models.CharField(max_length=10, choices=EstadoCuenta.choices, default=EstadoCuenta.PENDIENTE, verbose_name=_('Estado'))

    class Meta:
        verbose_name = _('Cuenta por Cobrar')
        verbose_name_plural = _('Cuentas por Cobrar')
        ordering = ['-fecha_emision']

    def __str__(self):
        return f"Cuenta #{self.id} - {self.estudiante} - S/ {self.monto}"

    @property
    def monto_neto(self):
        return self.monto - self.descuento


class Pago(models.Model):
    class MetodoPago(models.TextChoices):
        EFECTIVO = 'EFECTIVO', _('Efectivo')
        TARJETA = 'TARJETA', _('Tarjeta')
        TRANSFERENCIA = 'TRANSFERENCIA', _('Transferencia')
        BANCO = 'BANCO', _('Banco')
        OTRO = 'OTRO', _('Otro')

    class EstadoPago(models.TextChoices):
        REGISTRADO = 'REGISTRADO', _('Registrado')
        ANULADO = 'ANULADO', _('Anulado')

    cuenta = models.ForeignKey(CuentaCobrar, on_delete=models.CASCADE, related_name='pagos', verbose_name=_('Cuenta por Cobrar'))
    monto = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Monto'))
    fecha_pago = models.DateTimeField(auto_now_add=True, verbose_name=_('Fecha de Pago'))
    metodo = models.CharField(max_length=15, choices=MetodoPago.choices, verbose_name=_('Método de Pago'))
    numero_operacion = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Número de Operación'))
    estado = models.CharField(max_length=10, choices=EstadoPago.choices, default=EstadoPago.REGISTRADO, verbose_name=_('Estado'))

    class Meta:
        verbose_name = _('Pago')
        verbose_name_plural = _('Pagos')
        ordering = ['-fecha_pago']

    def __str__(self):
        return f"Pago #{self.id} - S/ {self.monto} ({self.get_metodo_display()})"


class Comprobante(models.Model):
    class TipoComprobante(models.TextChoices):
        BOLETA = 'BOLETA', _('Boleta')
        FACTURA = 'FACTURA', _('Factura')
        RECIBO = 'RECIBO', _('Recibo')

    pago = models.OneToOneField(Pago, on_delete=models.CASCADE, related_name='comprobante', verbose_name=_('Pago'))
    tipo = models.CharField(max_length=10, choices=TipoComprobante.choices, verbose_name=_('Tipo de Comprobante'))
    serie = models.CharField(max_length=10, blank=True, null=True, verbose_name=_('Serie'))
    numero = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('Número'))
    fecha_emision = models.DateTimeField(auto_now_add=True, verbose_name=_('Fecha de Emisión'))

    class Meta:
        verbose_name = _('Comprobante')
        verbose_name_plural = _('Comprobantes')
        ordering = ['-fecha_emision']

    def __str__(self):
        return f"{self.get_tipo_display()} {self.serie or ''}-{self.numero or ''}"
