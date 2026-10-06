from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from academico.models import Seccion
from matriculas.models import DetalleMatricula
from cuentas.models import Usuario

class SesionClase(models.Model):
    seccion = models.ForeignKey(
        Seccion,
        on_delete=models.CASCADE,
        related_name='sesiones',
        verbose_name=_('Sección')
    )
    fecha = models.DateField(verbose_name=_('Fecha de Clase'))
    hora_inicio = models.TimeField(verbose_name=_('Hora de Inicio'))
    hora_fin = models.TimeField(verbose_name=_('Hora de Fin'))
    tema = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Tema / Contenido Tratado'))
    cerrada = models.BooleanField(
        default=False,
        verbose_name=_('Sesión Cerrada'),
        help_text=_('Una sesión se considera cerrada cuando todas las asistencias están registradas y validadas.')
    )
    cerrada_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sesiones_cerradas',
        verbose_name=_('Cerrada por')
    )
    fecha_cierre = models.DateTimeField(null=True, blank=True, verbose_name=_('Fecha de Cierre'))
    creado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sesiones_creadas',
        verbose_name=_('Creado por')
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Sesión de Clase')
        verbose_name_plural = _('Sesiones de Clase')
        ordering = ['-fecha', '-hora_inicio']
        unique_together = ('seccion', 'fecha', 'hora_inicio')

    def __str__(self):
        return f"{self.seccion.curso.codigo} - {self.fecha} ({self.hora_inicio.strftime('%H:%M')} - {self.hora_fin.strftime('%H:%M')})"

    def clean(self):
        if self.hora_inicio and self.hora_fin and self.hora_inicio >= self.hora_fin:
            raise ValidationError({'hora_fin': _('La hora de fin debe ser posterior a la hora de inicio.')})
        if self.fecha and self.fecha > timezone.now().date():
            raise ValidationError({'fecha': _('No se pueden programar sesiones en fechas futuras para registro de asistencia inmediata.')})
        if self.seccion and self.seccion.periodo.esta_cerrado:
            raise ValidationError(_('No se pueden crear ni modificar sesiones en un periodo académico cerrado.'))


class Asistencia(models.Model):
    class EstadoAsistencia(models.TextChoices):
        PRESENTE = 'PRESENTE', _('Presente')
        TARDANZA = 'TARDANZA', _('Tardanza')
        FALTA = 'FALTA', _('Falta')
        JUSTIFICADA = 'JUSTIFICADA', _('Justificada')

    sesion = models.ForeignKey(
        SesionClase,
        on_delete=models.CASCADE,
        related_name='asistencias',
        verbose_name=_('Sesión')
    )
    detalle_matricula = models.ForeignKey(
        DetalleMatricula,
        on_delete=models.CASCADE,
        related_name='asistencias',
        verbose_name=_('Inscripción de Estudiante')
    )
    estado = models.CharField(
        max_length=15,
        choices=EstadoAsistencia.choices,
        default=EstadoAsistencia.PRESENTE,
        verbose_name=_('Estado')
    )
    observacion = models.CharField(max_length=255, blank=True, null=True, verbose_name=_('Observación / Motivo'))
    registrado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='asistencias_registradas',
        verbose_name=_('Registrado por')
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    ultima_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Asistencia')
        verbose_name_plural = _('Asistencias')
        unique_together = ('sesion', 'detalle_matricula')

    def __str__(self):
        return f"{self.detalle_matricula.estudiante.codigo} - {self.sesion.fecha}: {self.get_estado_display()}"


class HistorialAsistencia(models.Model):
    asistencia = models.ForeignKey(
        Asistencia,
        on_delete=models.CASCADE,
        related_name='historial',
        verbose_name=_('Asistencia')
    )
    estado_anterior = models.CharField(max_length=15, verbose_name=_('Estado Anterior'))
    estado_nuevo = models.CharField(max_length=15, verbose_name=_('Estado Nuevo'))
    motivo_cambio = models.TextField(blank=True, null=True, verbose_name=_('Motivo del Cambio'))
    modificado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Modificado por')
    )
    fecha_cambio = models.DateTimeField(auto_now_add=True, verbose_name=_('Fecha del Cambio'))

    class Meta:
        verbose_name = _('Historial de Asistencia')
        verbose_name_plural = _('Historial de Asistencias')
        ordering = ['-fecha_cambio']
