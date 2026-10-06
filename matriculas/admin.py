from django.contrib import admin
from .models import Matricula, DetalleMatricula

class DetalleMatriculaInline(admin.TabularInline):
    model = DetalleMatricula
    extra = 0
    readonly_fields = ('fecha_registro',)

@admin.register(Matricula)
class MatriculaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'estudiante', 'periodo', 'total_creditos', 'estado', 'fecha_registro')
    list_filter = ('periodo', 'estado')
    search_fields = ('codigo', 'estudiante__apellidos', 'estudiante__nombres', 'estudiante__codigo')
    inlines = [DetalleMatriculaInline]

@admin.register(DetalleMatricula)
class DetalleMatriculaAdmin(admin.ModelAdmin):
    list_display = ('matricula', 'seccion', 'estado', 'fecha_registro')
    list_filter = ('estado', 'seccion__periodo')
    search_fields = ('matricula__codigo', 'matricula__estudiante__apellidos', 'seccion__curso__nombre')
