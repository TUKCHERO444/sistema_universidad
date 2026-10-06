from django.db import models
from django.utils.translation import gettext_lazy as _


class Permiso(models.Model):
    codigo = models.CharField(max_length=100, unique=True, verbose_name=_('Código'))
    nombre = models.CharField(max_length=100, verbose_name=_('Nombre'))
    descripcion = models.CharField(max_length=250, blank=True, null=True, verbose_name=_('Descripción'))

    class Meta:
        verbose_name = _('Permiso')
        verbose_name_plural = _('Permisos')
        ordering = ['codigo']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True, verbose_name=_('Nombre'))
    descripcion = models.CharField(max_length=250, blank=True, null=True, verbose_name=_('Descripción'))

    class Meta:
        verbose_name = _('Rol')
        verbose_name_plural = _('Roles')
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class RolPermiso(models.Model):
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, related_name='permisos', verbose_name=_('Rol'))
    permiso = models.ForeignKey(Permiso, on_delete=models.CASCADE, related_name='roles', verbose_name=_('Permiso'))

    class Meta:
        verbose_name = _('Rol-Permiso')
        verbose_name_plural = _('Roles-Permisos')
        unique_together = ('rol', 'permiso')

    def __str__(self):
        return f"{self.rol.nombre} - {self.permiso.nombre}"
