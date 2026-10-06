from django.contrib import admin
from .models import SesionClase, Asistencia, HistorialAsistencia

class AsistenciaInline(admin.TabularInline):
    model = Asistencia
    extra = 0

@admin.register(SesionClase)
class SesionClaseAdmin(admin.ModelAdmin):
    list_display = ('seccion', 'fecha', 'hora_inicio', 'hora_fin', 'tema', 'cerrada', 'fecha_cierre')
    list_filter = ('cerrada', 'seccion__periodo')
    search_fields = ('seccion__curso__nombre', 'tema')
    inlines = [AsistenciaInline]

@admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ('sesion', 'detalle_matricula', 'estado', 'observacion', 'fecha_registro')
    list_filter = ('estado', 'sesion__seccion__periodo')
    search_fields = ('detalle_matricula__matricula__estudiante__apellidos', 'observacion')

@admin.register(HistorialAsistencia)
class HistorialAsistenciaAdmin(admin.ModelAdmin):
    list_display = ('asistencia', 'estado_anterior', 'estado_nuevo', 'modificado_por', 'fecha_cambio')
    readonly_fields = ('asistencia', 'estado_anterior', 'estado_nuevo', 'motivo_cambio', 'modificado_por', 'fecha_cambio')
