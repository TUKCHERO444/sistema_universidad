from django.db import models
from django.utils.translation import gettext_lazy as _
from academico.models import Carrera


class ModalidadIngreso(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name=_('Nombre'))
    descripcion = models.TextField(blank=True, null=True, verbose_name=_('Descripción'))
    estado = models.BooleanField(default=True, verbose_name=_('Estado'))

    class Meta:
        verbose_name = _('Modalidad de Ingreso')
        verbose_name_plural = _('Modalidades de Ingreso')
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class ProcesoAdmision(models.Model):
    class EstadoProceso(models.TextChoices):
        PLANIFICADO = 'PLANIFICADO', _('Planificado')
        ABIERTO = 'ABIERTO', _('Abierto')
        CERRADO = 'CERRADO', _('Cerrado')

    nombre = models.CharField(max_length=150, verbose_name=_('Nombre del Proceso'))
    year = models.PositiveSmallIntegerField(verbose_name=_('Año'))
    periodo = models.CharField(max_length=30, blank=True, null=True, verbose_name=_('Periodo'))
    fecha_inicio = models.DateField(verbose_name=_('Fecha de Inicio'))
    fecha_fin = models.DateField(verbose_name=_('Fecha de Fin'))
    estado = models.CharField(max_length=15, choices=EstadoProceso.choices, default=EstadoProceso.PLANIFICADO, verbose_name=_('Estado'))

    class Meta:
        verbose_name = _('Proceso de Admisión')
        verbose_name_plural = _('Procesos de Admisión')
        ordering = ['-year', '-fecha_inicio']

    def __str__(self):
        return f"{self.nombre} {self.year}"


class Postulacion(models.Model):
    class EstadoPostulacion(models.TextChoices):
        REGISTRADA = 'REGISTRADA', _('Registrada')
        EN_EVALUACION = 'EN_EVALUACION', _('En Evaluación')
        ADMITIDA = 'ADMITIDA', _('Admitida')
        NO_ADMITIDA = 'NO_ADMITIDA', _('No Admitida')
        ANULADA = 'ANULADA', _('Anulada')

    proceso = models.ForeignKey(ProcesoAdmision, on_delete=models.CASCADE, related_name='postulaciones', verbose_name=_('Proceso de Admisión'))
    carrera = models.ForeignKey(Carrera, on_delete=models.PROTECT, related_name='postulaciones', verbose_name=_('Carrera'))
    modalidad = models.ForeignKey(ModalidadIngreso, on_delete=models.PROTECT, related_name='postulaciones', verbose_name=_('Modalidad de Ingreso'))
    fecha_postulacion = models.DateTimeField(auto_now_add=True, verbose_name=_('Fecha de Postulación'))
    estado = models.CharField(max_length=15, choices=EstadoPostulacion.choices, default=EstadoPostulacion.REGISTRADA, verbose_name=_('Estado'))

    class Meta:
        verbose_name = _('Postulación')
        verbose_name_plural = _('Postulaciones')
        ordering = ['-fecha_postulacion']

    def __str__(self):
        return f"Postulación #{self.id} - {self.carrera.nombre} ({self.estado})"


class EvaluacionAdmision(models.Model):
    postulacion = models.ForeignKey(Postulacion, on_delete=models.CASCADE, related_name='evaluaciones', verbose_name=_('Postulación'))
    nombre = models.CharField(max_length=100, verbose_name=_('Nombre de la Evaluación'))
    fecha = models.DateTimeField(blank=True, null=True, verbose_name=_('Fecha de Evaluación'))
    puntaje = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, verbose_name=_('Puntaje Obtenido'))
    puntaje_maximo = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, verbose_name=_('Puntaje Máximo'))
    observacion = models.CharField(max_length=250, blank=True, null=True, verbose_name=_('Observación'))

    class Meta:
        verbose_name = _('Evaluación de Admisión')
        verbose_name_plural = _('Evaluaciones de Admisión')
        ordering = ['fecha']

    def __str__(self):
        return f"{self.nombre} - {self.puntaje}/{self.puntaje_maximo}"


class ResultadoAdmision(models.Model):
    class Resultado(models.TextChoices):
        ADMITIDO = 'ADMITIDO', _('Admitido')
        NO_ADMITIDO = 'NO_ADMITIDO', _('No Admitido')

    postulacion = models.OneToOneField(Postulacion, on_delete=models.CASCADE, related_name='resultado', verbose_name=_('Postulación'))
    puntaje_final = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, verbose_name=_('Puntaje Final'))
    resultado = models.CharField(max_length=15, choices=Resultado.choices, verbose_name=_('Resultado'))
    fecha_resultado = models.DateTimeField(auto_now_add=True, verbose_name=_('Fecha del Resultado'))

    class Meta:
        verbose_name = _('Resultado de Admisión')
        verbose_name_plural = _('Resultados de Admisión')
        ordering = ['-fecha_resultado']

    def __str__(self):
        return f"{self.postulacion} - {self.get_resultado_display()}"
