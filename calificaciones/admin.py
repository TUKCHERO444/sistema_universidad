from django.contrib import admin
from .models import Calificacion, HistorialCalificacion

class HistorialCalificacionInline(admin.TabularInline):
    model = HistorialCalificacion
    extra = 0
    readonly_fields = ('evaluacion', 'nota_anterior', 'nota_nueva', 'motivo_cambio', 'modificado_por', 'fecha_cambio')

@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display = ('detalle_matricula', 'nota1', 'nota2', 'nota3', 'promedio_final', 'estado_aprobacion', 'ultima_modificacion')
    list_filter = ('estado_aprobacion', 'detalle_matricula__seccion__periodo')
    search_fields = ('detalle_matricula__matricula__estudiante__apellidos', 'detalle_matricula__seccion__curso__nombre')
    inlines = [HistorialCalificacionInline]

@admin.register(HistorialCalificacion)
class HistorialCalificacionAdmin(admin.ModelAdmin):
    list_display = ('calificacion', 'evaluacion', 'nota_anterior', 'nota_nueva', 'motivo_cambio', 'modificado_por', 'fecha_cambio')
    readonly_fields = ('calificacion', 'evaluacion', 'nota_anterior', 'nota_nueva', 'motivo_cambio', 'modificado_por', 'fecha_cambio')
