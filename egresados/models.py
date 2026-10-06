from django.db import models
from django.utils.translation import gettext_lazy as _
from academico.models import Estudiante


class Egreso(models.Model):
    estudiante = models.OneToOneField(Estudiante, on_delete=models.CASCADE, related_name='egreso', verbose_name=_('Estudiante'))
    fecha_egreso = models.DateField(verbose_name=_('Fecha de Egreso'))
    creditos_aprobados = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name=_('Créditos Aprobados'))
    promedio_general = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name=_('Promedio General'))
    observacion = models.TextField(blank=True, null=True, verbose_name=_('Observación'))

    class Meta:
        verbose_name = _('Egreso')
        verbose_name_plural = _('Egresos')
        ordering = ['-fecha_egreso']

    def __str__(self):
        return f"Egreso - {self.estudiante} ({self.fecha_egreso})"


class GradoAcademico(models.Model):
    class TipoGrado(models.TextChoices):
        BACHILLER = 'BACHILLER', _('Bachiller')
        MAESTRO = 'MAESTRO', _('Maestro')
        DOCTOR = 'DOCTOR', _('Doctor')

    egreso = models.ForeignKey(Egreso, on_delete=models.CASCADE, related_name='grados', verbose_name=_('Egreso'))
    tipo = models.CharField(max_length=10, choices=TipoGrado.choices, verbose_name=_('Tipo de Grado'))
    nombre = models.CharField(max_length=200, verbose_name=_('Nombre del Grado'))
    fecha_otorgamiento = models.DateField(blank=True, null=True, verbose_name=_('Fecha de Otorgamiento'))
    numero_registro = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Número de Registro'))

    class Meta:
        verbose_name = _('Grado Académico')
        verbose_name_plural = _('Grados Académicos')
        ordering = ['-fecha_otorgamiento']

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.nombre}"


class Titulacion(models.Model):
    class EstadoTitulacion(models.TextChoices):
        EN_PROCESO = 'EN_PROCESO', _('En Proceso')
        APROBADO = 'APROBADO', _('Aprobado')
        OTORGADO = 'OTORGADO', _('Otorgado')

    egreso = models.ForeignKey(Egreso, on_delete=models.CASCADE, related_name='titulaciones', verbose_name=_('Egreso'))
    titulo = models.CharField(max_length=200, verbose_name=_('Título'))
    modalidad = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Modalidad de Titulación'))
    fecha_sustentacion = models.DateField(blank=True, null=True, verbose_name=_('Fecha de Sustentación'))
    fecha_otorgamiento = models.DateField(blank=True, null=True, verbose_name=_('Fecha de Otorgamiento'))
    numero_registro = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Número de Registro'))
    estado = models.CharField(max_length=10, choices=EstadoTitulacion.choices, default=EstadoTitulacion.EN_PROCESO, verbose_name=_('Estado'))

    class Meta:
        verbose_name = _('Titulación')
        verbose_name_plural = _('Titulaciones')
        ordering = ['-fecha_sustentacion']

    def __str__(self):
        return f"{self.titulo} - {self.get_estado_display()}"
