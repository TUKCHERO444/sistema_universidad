from django.db import models
from django.utils.translation import gettext_lazy as _
from academico.models import Estudiante


class TipoTramite(models.Model):
    nombre = models.CharField(max_length=150, unique=True, verbose_name=_('Nombre'))
    descripcion = models.TextField(blank=True, null=True, verbose_name=_('Descripción'))
    costo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name=_('Costo'))
    estado = models.BooleanField(default=True, verbose_name=_('Estado'))

    class Meta:
        verbose_name = _('Tipo de Trámite')
        verbose_name_plural = _('Tipos de Trámite')
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class SolicitudTramite(models.Model):
    class EstadoSolicitud(models.TextChoices):
        PENDIENTE = 'PENDIENTE', _('Pendiente')
        EN_REVISION = 'EN_REVISION', _('En Revisión')
        APROBADA = 'APROBADA', _('Aprobada')
        RECHAZADA = 'RECHAZADA', _('Rechazada')
        CANCELADA = 'CANCELADA', _('Cancelada')

    estudiante = models.ForeignKey(Estudiante, on_delete=models.PROTECT, related_name='solicitudes_tramite', verbose_name=_('Estudiante'))
    tipo_tramite = models.ForeignKey(TipoTramite, on_delete=models.PROTECT, related_name='solicitudes', verbose_name=_('Tipo de Trámite'))
    fecha_solicitud = models.DateTimeField(auto_now_add=True, verbose_name=_('Fecha de Solicitud'))
    motivo = models.TextField(blank=True, null=True, verbose_name=_('Motivo'))
    estado = models.CharField(max_length=15, choices=EstadoSolicitud.choices, default=EstadoSolicitud.PENDIENTE, verbose_name=_('Estado'))

    class Meta:
        verbose_name = _('Solicitud de Trámite')
        verbose_name_plural = _('Solicitudes de Trámite')
        ordering = ['-fecha_solicitud']

    def __str__(self):
        return f"Solicitud #{self.id} - {self.tipo_tramite.nombre} ({self.estado})"


class SeguimientoTramite(models.Model):
    solicitud = models.ForeignKey(SolicitudTramite, on_delete=models.CASCADE, related_name='seguimientos', verbose_name=_('Solicitud de Trámite'))
    fecha = models.DateTimeField(auto_now_add=True, verbose_name=_('Fecha de Seguimiento'))
    estado = models.CharField(max_length=50, verbose_name=_('Estado'))
    observacion = models.TextField(blank=True, null=True, verbose_name=_('Observación'))

    class Meta:
        verbose_name = _('Seguimiento de Trámite')
        verbose_name_plural = _('Seguimientos de Trámite')
        ordering = ['-fecha']

    def __str__(self):
        return f"Seguimiento #{self.id} - {self.solicitud} - {self.estado}"
