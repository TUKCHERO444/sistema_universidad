from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from cuentas.models import Usuario


class Facultad(models.Model):
    codigo = models.CharField(max_length=20, unique=True, verbose_name=_('Código'))
    nombre = models.CharField(max_length=150, verbose_name=_('Nombre'))
    estado = models.BooleanField(default=True, verbose_name=_('Estado'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Facultad')
        verbose_name_plural = _('Facultades')
        ordering = ['nombre']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Carrera(models.Model):
    codigo = models.CharField(max_length=10, unique=True, verbose_name=_('Código'))
    nombre = models.CharField(max_length=150, unique=True, verbose_name=_('Nombre de la Carrera'))
    descripcion = models.TextField(blank=True, null=True, verbose_name=_('Descripción'))
    facultad = models.ForeignKey(Facultad, on_delete=models.PROTECT, related_name='carreras', verbose_name=_('Facultad'), null=True, blank=True)
    duracion_ciclos = models.PositiveSmallIntegerField(default=10, verbose_name=_('Duración en Ciclos'))
    grado_academico = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('Grado Académico'))
    titulo_profesional = models.CharField(max_length=150, blank=True, null=True, verbose_name=_('Título Profesional'))
    activo = models.BooleanField(default=True, verbose_name=_('Activo'))
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Carrera')
        verbose_name_plural = _('Carreras')
        ordering = ['nombre']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class PlanEstudio(models.Model):
    class EstadoPlan(models.TextChoices):
        VIGENTE = 'VIGENTE', _('Vigente')
        NO_VIGENTE = 'NO_VIGENTE', _('No Vigente')

    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE, related_name='planes_estudio', verbose_name=_('Carrera'))
    codigo = models.CharField(max_length=30, unique=True, verbose_name=_('Código del Plan'))
    nombre = models.CharField(max_length=150, verbose_name=_('Nombre del Plan'))
    year_inicio = models.PositiveSmallIntegerField(verbose_name=_('Año de Inicio'))
    total_creditos = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name=_('Total de Créditos'))
    estado = models.CharField(max_length=12, choices=EstadoPlan.choices, default=EstadoPlan.VIGENTE, verbose_name=_('Estado'))

    class Meta:
        verbose_name = _('Plan de Estudio')
        verbose_name_plural = _('Planes de Estudio')
        ordering = ['-year_inicio']

    def __str__(self):
        return f"{self.codigo} - {self.nombre} ({self.year_inicio})"


class PlanCurso(models.Model):
    class TipoCurso(models.TextChoices):
        OBLIGATORIO = 'OBLIGATORIO', _('Obligatorio')
        ELECTIVO = 'ELECTIVO', _('Electivo')

    plan = models.ForeignKey(PlanEstudio, on_delete=models.CASCADE, related_name='cursos', verbose_name=_('Plan de Estudio'))
    curso = models.ForeignKey('Curso', on_delete=models.CASCADE, related_name='planes', verbose_name=_('Curso'))
    ciclo = models.PositiveSmallIntegerField(verbose_name=_('Ciclo'))
    creditos = models.PositiveSmallIntegerField(verbose_name=_('Créditos'))
    tipo = models.CharField(max_length=12, choices=TipoCurso.choices, default=TipoCurso.OBLIGATORIO, verbose_name=_('Tipo de Curso'))

    class Meta:
        verbose_name = _('Curso de Plan de Estudio')
        verbose_name_plural = _('Cursos de Planes de Estudio')
        ordering = ['ciclo', 'curso']
        unique_together = ('plan', 'curso')

    def __str__(self):
        return f"{self.plan.codigo} - {self.curso.nombre} (Ciclo {self.ciclo})"


class Prerrequisito(models.Model):
    plan_curso = models.ForeignKey(PlanCurso, on_delete=models.CASCADE, related_name='prerrequisitos', verbose_name=_('Curso del Plan'))
    curso_prerrequisito = models.ForeignKey('Curso', on_delete=models.CASCADE, related_name='es_prerrequisito_de', verbose_name=_('Curso Prerrequisito'))

    class Meta:
        verbose_name = _('Prerrequisito')
        verbose_name_plural = _('Prerrequisitos')
        unique_together = ('plan_curso', 'curso_prerrequisito')

    def __str__(self):
        return f"{self.plan_curso.curso.nombre} requiere {self.curso_prerrequisito.nombre}"


class Curso(models.Model):
    codigo = models.CharField(max_length=15, unique=True, verbose_name=_('Código de Curso'))
    nombre = models.CharField(max_length=150, verbose_name=_('Nombre de la Asignatura'))
    carrera = models.ForeignKey(Carrera, on_delete=models.PROTECT, related_name='cursos', verbose_name=_('Carrera'))
    ciclo = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        verbose_name=_('Ciclo')
    )
    creditos = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        default=3,
        verbose_name=_('Créditos')
    )
    activo = models.BooleanField(default=True, verbose_name=_('Activo'))
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Curso')
        verbose_name_plural = _('Cursos')
        ordering = ['carrera', 'ciclo', 'nombre']
        unique_together = ('codigo', 'carrera')

    def __str__(self):
        return f"{self.codigo} - {self.nombre} (Ciclo {self.ciclo})"


class Periodo(models.Model):
    class EstadoPeriodo(models.TextChoices):
        PLANIFICADO = 'PLANIFICADO', _('Planificado')
        MATRICULA = 'MATRICULA', _('Matrícula')
        EN_CURSO = 'EN_CURSO', _('En Curso')
        CERRADO = 'CERRADO', _('Cerrado')

    codigo = models.CharField(
        max_length=10,
        unique=True,
        verbose_name=_('Código (ej. 2025-1)'),
        help_text=_('Formato recomendado: AAAA-1, AAAA-2')
    )
    nombre = models.CharField(max_length=50, verbose_name=_('Nombre Descriptivo'))
    fecha_inicio = models.DateField(verbose_name=_('Fecha de Inicio de Clases'))
    fecha_fin = models.DateField(verbose_name=_('Fecha de Fin de Clases'))
    matricula_inicio = models.DateField(verbose_name=_('Inicio de Matrícula'))
    matricula_fin = models.DateField(verbose_name=_('Fin de Matrícula'))
    estado = models.CharField(
        max_length=11,
        choices=EstadoPeriodo.choices,
        default=EstadoPeriodo.PLANIFICADO,
        verbose_name=_('Estado Académico')
    )
    activo = models.BooleanField(
        default=False,
        verbose_name=_('Periodo Vigente/Actual'),
        help_text=_('Solo un periodo puede ser el principal activo por defecto')
    )

    class Meta:
        verbose_name = _('Periodo Académico')
        verbose_name_plural = _('Periodos Académicos')
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"Periodo {self.codigo} ({self.get_estado_display()})"

    def clean(self):
        if self.fecha_inicio and self.fecha_fin and self.fecha_inicio >= self.fecha_fin:
            raise ValidationError({'fecha_fin': _('La fecha de fin debe ser posterior a la fecha de inicio.')})
        if self.matricula_inicio and self.matricula_fin and self.matricula_inicio > self.matricula_fin:
            raise ValidationError({'matricula_fin': _('El fin de matrícula debe ser posterior al inicio.')})
        if self.matricula_fin and self.fecha_fin and self.matricula_fin > self.fecha_fin:
            raise ValidationError({'matricula_fin': _('El periodo de matrícula no puede extenderse más allá del fin del semestre.')})

    def esta_en_intervalo_matricula(self, fecha=None):
        if not fecha:
            fecha = timezone.now().date()
        return self.matricula_inicio <= fecha <= self.matricula_fin and self.estado == self.EstadoPeriodo.MATRICULA

    @property
    def esta_cerrado(self):
        return self.estado == self.EstadoPeriodo.CERRADO


class Docente(models.Model):
    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='perfil_docente',
        verbose_name=_('Cuenta de Usuario')
    )
    codigo = models.CharField(max_length=15, unique=True, verbose_name=_('Código Docente'))
    dni = models.CharField(
        max_length=8,
        unique=True,
        validators=[RegexValidator(r'^\d{8}$', _('DNI debe tener 8 dígitos'))],
        verbose_name=_('DNI')
    )
    nombres = models.CharField(max_length=100, verbose_name=_('Nombres'))
    apellidos = models.CharField(max_length=100, verbose_name=_('Apellidos'))
    correo = models.EmailField(unique=True, verbose_name=_('Correo Institucional'))
    telefono = models.CharField(max_length=9, blank=True, null=True, verbose_name=_('Celular'))
    especialidad = models.CharField(max_length=150, verbose_name=_('Especialidad'))
    activo = models.BooleanField(default=True, verbose_name=_('Activo'))
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Docente')
        verbose_name_plural = _('Docentes')
        ordering = ['apellidos', 'nombres']

    def __str__(self):
        return f"{self.apellidos}, {self.nombres} ({self.codigo})"

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"


class Estudiante(models.Model):
    class EstadoEstudiante(models.TextChoices):
        ACTIVO = 'ACTIVO', _('Activo')
        INACTIVO = 'INACTIVO', _('Inactivo')
        RESERVA = 'RESERVA', _('Reserva')
        SUSPENDIDO = 'SUSPENDIDO', _('Suspendido')
        EGRESADO = 'EGRESADO', _('Egresado')
        RETIRADO = 'RETIRADO', _('Retirado')

    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='perfil_estudiante',
        verbose_name=_('Cuenta de Usuario')
    )
    codigo = models.CharField(max_length=15, unique=True, verbose_name=_('Código Estudiantil'))
    dni = models.CharField(
        max_length=8,
        unique=True,
        validators=[RegexValidator(r'^\d{8}$', _('DNI debe tener 8 dígitos'))],
        verbose_name=_('DNI')
    )
    nombres = models.CharField(max_length=100, verbose_name=_('Nombres'))
    apellidos = models.CharField(max_length=100, verbose_name=_('Apellidos'))
    correo = models.EmailField(unique=True, verbose_name=_('Correo Institucional'))
    telefono = models.CharField(max_length=9, blank=True, null=True, verbose_name=_('Celular'))
    fecha_nacimiento = models.DateField(verbose_name=_('Fecha de Nacimiento'))
    carrera = models.ForeignKey(Carrera, on_delete=models.PROTECT, related_name='estudiantes', verbose_name=_('Carrera'))
    estado = models.CharField(
        max_length=15,
        choices=EstadoEstudiante.choices,
        default=EstadoEstudiante.ACTIVO,
        verbose_name=_('Estado Académico')
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Estudiante')
        verbose_name_plural = _('Estudiantes')
        ordering = ['apellidos', 'nombres']

    def __str__(self):
        return f"{self.apellidos}, {self.nombres} ({self.codigo})"

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"


class Seccion(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.PROTECT, related_name='secciones', verbose_name=_('Curso'))
    periodo = models.ForeignKey(Periodo, on_delete=models.PROTECT, related_name='secciones', verbose_name=_('Periodo'))
    docente = models.ForeignKey(Docente, on_delete=models.PROTECT, related_name='secciones', verbose_name=_('Docente Asignado'))
    codigo_seccion = models.CharField(max_length=10, verbose_name=_('Código de Sección (ej. 01, A)'))
    capacidad_maxima = models.PositiveSmallIntegerField(
        default=30,
        validators=[MinValueValidator(1), MaxValueValidator(150)],
        verbose_name=_('Capacidad Máxima')
    )
    fecha_corte_predictivo = models.DateField(
        verbose_name=_('Fecha de Corte Predictivo'),
        help_text=_('Fecha posterior a la primera evaluación y previa a la segunda para snapshot de ML')
    )
    activo = models.BooleanField(default=True, verbose_name=_('Activo'))
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Sección')
        verbose_name_plural = _('Secciones')
        ordering = ['periodo', 'curso', 'codigo_seccion']
        unique_together = ('curso', 'periodo', 'codigo_seccion')

    def __str__(self):
        return f"{self.curso.nombre} - Sec {self.codigo_seccion} ({self.periodo.codigo}) - {self.docente.nombre_completo}"

    @property
    def vacantes_ocupadas(self):
        return self.inscripciones.filter(matricula__estado='REGISTRADA', estado='INSCRITO').count()

    @property
    def vacantes_disponibles(self):
        return max(0, self.capacidad_maxima - self.vacantes_ocupadas)

    @property
    def tiene_vacantes(self):
        return self.vacantes_disponibles > 0

    def clean(self):
        if self.fecha_corte_predictivo and self.periodo:
            if self.fecha_corte_predictivo < self.periodo.fecha_inicio or self.fecha_corte_predictivo > self.periodo.fecha_fin:
                raise ValidationError({
                    'fecha_corte_predictivo': _('La fecha de corte predictivo debe encontrarse dentro del rango del periodo académico.')
                })
