from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

class Usuario(AbstractUser):
    class Rol(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrador')
        DOCENTE = 'DOCENTE', _('Docente')
        ESTUDIANTE = 'ESTUDIANTE', _('Estudiante')

    dni_validator = RegexValidator(
        regex=r'^\d{8}$',
        message=_('El DNI debe contener exactamente 8 dígitos numéricos.')
    )
    telefono_validator = RegexValidator(
        regex=r'^9\d{8}$',
        message=_('El celular debe tener 9 dígitos e iniciar con 9.')
    )

    rol = models.CharField(
        max_length=15,
        choices=Rol.choices,
        default=Rol.ADMIN,
        verbose_name=_('Rol en el Sistema')
    )
    dni = models.CharField(
        max_length=8,
        unique=True,
        null=True,
        blank=True,
        validators=[dni_validator],
        verbose_name=_('DNI')
    )
    telefono = models.CharField(
        max_length=9,
        blank=True,
        null=True,
        validators=[telefono_validator],
        verbose_name=_('Teléfono Celular')
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name=_('Foto de Perfil')
    )
    intentos_fallidos = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Intentos Fallidos de Inicio')
    )
    bloqueado_hasta = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Bloqueado Hasta')
    )

    class Meta:
        verbose_name = _('Usuario')
        verbose_name_plural = _('Usuarios')
        ordering = ['username']

    def __str__(self):
        nombre_completo = f"{self.first_name} {self.last_name}".strip()
        return f"{nombre_completo or self.username} ({self.get_rol_display()})"

    @property
    def es_admin(self):
        return self.rol == self.Rol.ADMIN or self.is_superuser

    @property
    def es_docente(self):
        return self.rol == self.Rol.DOCENTE

    @property
    def es_estudiante(self):
        return self.rol == self.Rol.ESTUDIANTE


class RegistroAuditoria(models.Model):
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='auditorias',
        verbose_name=_('Usuario')
    )
    modulo = models.CharField(max_length=50, verbose_name=_('Módulo'))
    accion = models.CharField(max_length=50, verbose_name=_('Acción'))
    descripcion = models.TextField(verbose_name=_('Descripción del Evento'))
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name=_('Dirección IP'))
    fecha_hora = models.DateTimeField(auto_now_add=True, verbose_name=_('Fecha y Hora'))

    class Meta:
        verbose_name = _('Registro de Auditoría')
        verbose_name_plural = _('Registros de Auditoría')
        ordering = ['-fecha_hora']

    def __str__(self):
        return f"[{self.fecha_hora.strftime('%Y-%m-%d %H:%M')}] {self.usuario} - {self.modulo}: {self.accion}"
