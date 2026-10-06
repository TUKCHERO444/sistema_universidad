from django.db import models
from django.utils.translation import gettext_lazy as _
from academico.models import Seccion, Periodo


class Aula(models.Model):
    class TipoAula(models.TextChoices):
        AULA = 'AULA', _('Aula')
        LABORATORIO = 'LABORATORIO', _('Laboratorio')
        TALLER = 'TALLER', _('Taller')
        AUDITORIO = 'AUDITORIO', _('Auditorio')

    codigo = models.CharField(max_length=20, unique=True, verbose_name=_('Código'))
    nombre = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Nombre'))
    pabellon = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Pabellón'))
    piso = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name=_('Piso'))
    capacidad = models.PositiveSmallIntegerField(verbose_name=_('Capacidad'))
    tipo = models.CharField(max_length=15, choices=TipoAula.choices, default=TipoAula.AULA, verbose_name=_('Tipo'))
    estado = models.BooleanField(default=True, verbose_name=_('Estado'))

    class Meta:
        verbose_name = _('Aula')
        verbose_name_plural = _('Aulas')
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre or self.pabellon or 'Sin nombre'}"


class CalendarioAcademico(models.Model):
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, related_name='eventos', verbose_name=_('Periodo Académico'))
    nombre = models.CharField(max_length=150, verbose_name=_('Nombre del Evento'))
    descripcion = models.TextField(blank=True, null=True, verbose_name=_('Descripción'))
    fecha_inicio = models.DateTimeField(verbose_name=_('Fecha de Inicio'))
    fecha_fin = models.DateTimeField(blank=True, null=True, verbose_name=_('Fecha de Fin'))

    class Meta:
        verbose_name = _('Evento de Calendario')
        verbose_name_plural = _('Eventos de Calendario')
        ordering = ['fecha_inicio']

    def __str__(self):
        return f"{self.nombre} ({self.periodo.codigo})"


class Horario(models.Model):
    class DiaSemana(models.TextChoices):
        LUNES = 'LUNES', _('Lunes')
        MARTES = 'MARTES', _('Martes')
        MIERCOLES = 'MIERCOLES', _('Miércoles')
        JUEVES = 'JUEVES', _('Jueves')
        VIERNES = 'VIERNES', _('Viernes')
        SABADO = 'SABADO', _('Sábado')
        DOMINGO = 'DOMINGO', _('Domingo')

    seccion = models.ForeignKey(Seccion, on_delete=models.CASCADE, related_name='horarios', verbose_name=_('Sección'))
    aula = models.ForeignKey(Aula, on_delete=models.SET_NULL, blank=True, null=True, related_name='horarios', verbose_name=_('Aula'))
    dia_semana = models.CharField(max_length=10, choices=DiaSemana.choices, verbose_name=_('Día de la Semana'))
    hora_inicio = models.TimeField(verbose_name=_('Hora de Inicio'))
    hora_fin = models.TimeField(verbose_name=_('Hora de Fin'))

    class Meta:
        verbose_name = _('Horario')
        verbose_name_plural = _('Horarios')
        ordering = ['dia_semana', 'hora_inicio']

    def __str__(self):
        return f"{self.seccion} - {self.get_dia_semana_display()} {self.hora_inicio}-{self.hora_fin}"
