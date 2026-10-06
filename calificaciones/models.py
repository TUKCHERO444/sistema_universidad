from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal, ROUND_HALF_UP
from matriculas.models import DetalleMatricula
from cuentas.models import Usuario

class Calificacion(models.Model):
    class EstadoAprobacion(models.TextChoices):
        APROBADO = 'APROBADO', _('Aprobado')
        DESAPROBADO = 'DESAPROBADO', _('Desaprobado')
        PENDIENTE = 'PENDIENTE', _('Pendiente')

    nota_min_validator = MinValueValidator(Decimal('0.00'), _('La nota mínima es 0.00'))
    nota_max_validator = MaxValueValidator(Decimal('20.00'), _('La nota máxima es 20.00'))

    detalle_matricula = models.OneToOneField(
        DetalleMatricula,
        on_delete=models.CASCADE,
        related_name='calificacion',
        verbose_name=_('Inscripción')
    )
    nota1 = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[nota_min_validator, nota_max_validator],
        verbose_name=_('Evaluación 1 (N1)')
    )
    nota2 = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[nota_min_validator, nota_max_validator],
        verbose_name=_('Evaluación 2 (N2)')
    )
    nota3 = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[nota_min_validator, nota_max_validator],
        verbose_name=_('Evaluación 3 (N3)')
    )
    promedio_final = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Promedio Final')
    )
    estado_aprobacion = models.CharField(
        max_length=15,
        choices=EstadoAprobacion.choices,
        default=EstadoAprobacion.PENDIENTE,
        verbose_name=_('Resultado')
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)
    ultima_modificacion = models.DateTimeField(auto_now=True)
    registrado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='calificaciones_registradas',
        verbose_name=_('Registrado por')
    )

    class Meta:
        verbose_name = _('Calificación')
        verbose_name_plural = _('Calificaciones')
        ordering = ['detalle_matricula__matricula__estudiante__apellidos']

    def __str__(self):
        return f"{self.detalle_matricula.estudiante.codigo} - {self.detalle_matricula.seccion.curso.codigo}: PF={self.promedio_final if self.promedio_final is not None else 'Pendiente'}"

    def calcular_promedio(self):
        """
        Regla de negocio:
        - Promedio aritmético de las 3 notas.
        - Se calcula ÚNICAMENTE si las 3 notas existen (nota vacía = pendiente; 0 es una nota válida).
        - Cálculo con Decimal y redondeo ROUND_HALF_UP a dos decimales.
        - Aprobación con promedio final igual o superior a 13.00.
        """
        if self.nota1 is not None and self.nota2 is not None and self.nota3 is not None:
            suma = Decimal(str(self.nota1)) + Decimal(str(self.nota2)) + Decimal(str(self.nota3))
            prom = (suma / Decimal('3.00')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            self.promedio_final = prom
            if self.promedio_final >= Decimal('13.00'):
                self.estado_aprobacion = self.EstadoAprobacion.APROBADO
            else:
                self.estado_aprobacion = self.EstadoAprobacion.DESAPROBADO
        else:
            self.promedio_final = None
            self.estado_aprobacion = self.EstadoAprobacion.PENDIENTE

    def save(self, *args, **kwargs):
        self.calcular_promedio()
        super().save(*args, **kwargs)


class HistorialCalificacion(models.Model):
    calificacion = models.ForeignKey(
        Calificacion,
        on_delete=models.CASCADE,
        related_name='historial',
        verbose_name=_('Calificación')
    )
    evaluacion = models.CharField(max_length=20, verbose_name=_('Evaluación Modificada'))
    nota_anterior = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    nota_nueva = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    motivo_cambio = models.TextField(verbose_name=_('Motivo de la Modificación'))
    modificado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Modificado por')
    )
    fecha_cambio = models.DateTimeField(auto_now_add=True, verbose_name=_('Fecha del Cambio'))

    class Meta:
        verbose_name = _('Historial de Calificación')
        verbose_name_plural = _('Historial de Calificaciones')
        ordering = ['-fecha_cambio']
