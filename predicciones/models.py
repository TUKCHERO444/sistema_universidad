from django.db import models
from django.utils.translation import gettext_lazy as _
from matriculas.models import DetalleMatricula
from cuentas.models import Usuario

class InstantaneaPredictiva(models.Model):
    """
    Registro inmutable de los datos académicos disponibles exactamente en la fecha de corte.
    Garantiza reproducibilidad e impide data leakage o sesgo retrospectivo.
    """
    detalle_matricula = models.OneToOneField(
        DetalleMatricula,
        on_delete=models.CASCADE,
        related_name='instantanea_predictiva',
        verbose_name=_('Inscripción Estudiante-Curso-Periodo')
    )
    fecha_corte = models.DateField(verbose_name=_('Fecha de Corte Utilizada'))
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name=_('Fecha de Creación del Snapshot'))

    # Características observadas al corte (Sin información futura)
    nota1 = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Nota 1 al Corte')
    )
    porcentaje_asistencia = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('% Asistencia al Corte')
    )
    total_faltas = models.PositiveSmallIntegerField(default=0, verbose_name=_('Faltas Acumuladas'))
    total_tardanzas = models.PositiveSmallIntegerField(default=0, verbose_name=_('Tardanzas Acumuladas'))
    sesiones_consideradas = models.PositiveSmallIntegerField(default=0, verbose_name=_('Sesiones Válidas al Corte'))
    promedio_historico_anterior = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Promedio Histórico Anterior')
    )
    cursos_desaprobados_anteriores = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_('Cursos Desaprobados Previos')
    )
    sin_historial_previo = models.BooleanField(
        default=False,
        verbose_name=_('Indicador: Estudiante Sin Historial Previo')
    )

    # Variable objetivo real (Solo para entrenar y evaluar con inscripciones históricas cerradas)
    # 1: Desaprobado (Promedio < 13.00), 0: Aprobado (Promedio >= 13.00)
    resultado_real_desaprobado = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        choices=[(1, _('Desaprobado (<13.00)')), (0, _('Aprobado (>=13.00)'))],
        verbose_name=_('Resultado Real (Target)')
    )
    promedio_final_real = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_('Promedio Final Real')
    )
    es_sintetico = models.BooleanField(default=False, verbose_name=_('Es Dato Sintético de Demostración'))

    class Meta:
        verbose_name = _('Instantánea Predictiva')
        verbose_name_plural = _('Instantáneas Predictivas')
        ordering = ['-fecha_corte']

    def __str__(self):
        return f"Snapshot {self.detalle_matricula} [Corte: {self.fecha_corte}]"


class VersionModelo(models.Model):
    class AlgoritmoChoice(models.TextChoices):
        DUMMY = 'DUMMY', _('DummyClassifier (Línea Base)')
        LOGISTIC_REGRESSION = 'LOGISTIC', _('Regresión Logística')
        DECISION_TREE = 'DECISION_TREE', _('Árbol de Decisión (Profundidad Controlada)')

    nombre = models.CharField(max_length=150, verbose_name=_('Nombre del Modelo'))
    algoritmo = models.CharField(max_length=25, choices=AlgoritmoChoice.choices, verbose_name=_('Algoritmo'))
    version = models.CharField(max_length=30, unique=True, verbose_name=_('Versión (ej. v1.0-logreg)'))
    archivo_modelo = models.CharField(max_length=255, verbose_name=_('Ruta del Artefacto'))
    metricas_evaluacion = models.JSONField(default=dict, verbose_name=_('Métricas de Evaluación'))
    umbral_decision = models.FloatField(default=0.50, verbose_name=_('Umbral de Decisión'))
    variables_utilizadas = models.JSONField(default=list, verbose_name=_('Variables Utilizadas'))
    activo = models.BooleanField(
        default=False,
        verbose_name=_('Modelo Activo para Predicciones'),
        help_text=_('Solo un modelo evaluado y aprobado puede estar activo institucionalmente.')
    )
    es_sintetico = models.BooleanField(
        default=False,
        verbose_name=_('Entrenado con Datos Sintéticos'),
        help_text=_('Los modelos sintéticos son para demostración y no deben gobernar decisiones reales.')
    )
    fecha_entrenamiento = models.DateTimeField(auto_now_add=True, verbose_name=_('Fecha de Entrenamiento'))
    entrenado_por = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Entrenado por')
    )

    class Meta:
        verbose_name = _('Versión de Modelo Predictivo')
        verbose_name_plural = _('Versiones de Modelos Predictivos')
        ordering = ['-fecha_entrenamiento']

    def __str__(self):
        estado = "ACTIVO" if self.activo else "INACTIVO"
        return f"{self.nombre} ({self.version}) - [{estado}]"


class PrediccionEstudiante(models.Model):
    class NivelRiesgo(models.TextChoices):
        BAJO = 'BAJO', _('Bajo Riesgo')
        MEDIO = 'MEDIO', _('Riesgo Medio')
        ALTO = 'ALTO', _('Alto Riesgo')
        INSUFICIENTE = 'INSUFICIENTE', _('Datos Insuficientes')

    instantanea = models.ForeignKey(
        InstantaneaPredictiva,
        on_delete=models.CASCADE,
        related_name='predicciones',
        verbose_name=_('Instantánea')
    )
    version_modelo = models.ForeignKey(
        VersionModelo,
        on_delete=models.PROTECT,
        related_name='predicciones_generadas',
        verbose_name=_('Versión de Modelo')
    )
    probabilidad_riesgo = models.DecimalField(
        max_digits=5,
        decimal_places=4,
        verbose_name=_('Probabilidad Estimada de Desaprobación')
    )
    nivel_riesgo = models.CharField(
        max_length=20,
        choices=NivelRiesgo.choices,
        verbose_name=_('Nivel de Riesgo')
    )
    calibrado = models.BooleanField(default=False, verbose_name=_('Calibración Evaluada'))
    factores_riesgo = models.JSONField(default=dict, verbose_name=_('Factores Observados'))
    orientacion_academica = models.TextField(blank=True, null=True, verbose_name=_('Orientación de Apoyo Académico'))
    fecha_prediccion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Predicción de Riesgo Académico')
        verbose_name_plural = _('Predicciones de Riesgo Académico')
        unique_together = ('instantanea', 'version_modelo')
        ordering = ['-probabilidad_riesgo']

    def __str__(self):
        return f"{self.instantanea.detalle_matricula} | Riesgo: {self.probabilidad_riesgo * 100:.1f}% ({self.get_nivel_riesgo_display()})"
