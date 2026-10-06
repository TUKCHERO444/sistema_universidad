from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from academico.models import Estudiante, Periodo, Seccion
from cuentas.models import Usuario

class Matricula(models.Model):
    class EstadoMatricula(models.TextChoices):
        REGISTRADA = 'REGISTRADA', _('Registrada')
        ANULADA = 'ANULADA', _('Anulada')

    codigo = models.CharField(max_length=25, unique=True, verbose_name=_('Código de Matrícula'))
    estudiante = models.ForeignKey(
        Estudiante,
        on_delete=models.PROTECT,
        related_name='matriculas',
        verbose_name=_('Estudiante')
    )
    periodo = models.ForeignKey(
        Periodo,
        on_delete=models.PROTECT,
        related_name='matriculas',
        verbose_name=_('Periodo Académico')
    )
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name=_('Fecha de Registro'))
    estado = models.CharField(
        max_length=15,
        choices=EstadoMatricula.choices,
        default=EstadoMatricula.REGISTRADA,
        verbose_name=_('Estado')
    )
    total_creditos = models.PositiveSmallIntegerField(default=0, verbose_name=_('Total de Créditos'))
    motivo_anulacion = models.TextField(blank=True, null=True, verbose_name=_('Motivo de Anulación'))
    usuario_registro = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='matriculas_registradas',
        verbose_name=_('Registrado por')
    )
    usuario_anulacion = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='matriculas_anuladas',
        verbose_name=_('Anulado por')
    )
    fecha_anulacion = models.DateTimeField(null=True, blank=True, verbose_name=_('Fecha de Anulación'))

    class Meta:
        verbose_name = _('Matrícula')
        verbose_name_plural = _('Matrículas')
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"{self.codigo} - {self.estudiante.nombre_completo} ({self.periodo.codigo})"

    @property
    def es_valida(self):
        return self.estado == self.EstadoMatricula.REGISTRADA


class DetalleMatricula(models.Model):
    class EstadoDetalle(models.TextChoices):
        INSCRITO = 'INSCRITO', _('Inscrito')
        RETIRADO = 'RETIRADO', _('Retirado')
        ANULADO = 'ANULADO', _('Anulado')

    matricula = models.ForeignKey(
        Matricula,
        on_delete=models.CASCADE,
        related_name='detalles',
        verbose_name=_('Matrícula')
    )
    seccion = models.ForeignKey(
        Seccion,
        on_delete=models.PROTECT,
        related_name='inscripciones',
        verbose_name=_('Sección')
    )
    estado = models.CharField(
        max_length=15,
        choices=EstadoDetalle.choices,
        default=EstadoDetalle.INSCRITO,
        verbose_name=_('Estado de Inscripción')
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Detalle de Matrícula')
        verbose_name_plural = _('Detalles de Matrícula')
        unique_together = ('matricula', 'seccion')

    def __str__(self):
        return f"{self.matricula.estudiante.codigo} -> {self.seccion}"

    @property
    def estudiante(self):
        return self.matricula.estudiante

    @property
    def periodo(self):
        return self.matricula.periodo

    @property
    def curso(self):
        return self.seccion.curso
