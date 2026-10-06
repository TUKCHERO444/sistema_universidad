from django.contrib import admin
from .models import Carrera, Curso, Periodo, Docente, Estudiante, Seccion

@admin.register(Carrera)
class CarreraAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'activo', 'fecha_creacion')
    search_fields = ('codigo', 'nombre')
    list_filter = ('activo',)

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'carrera', 'ciclo', 'creditos', 'activo')
    search_fields = ('codigo', 'nombre')
    list_filter = ('carrera', 'ciclo', 'activo')

@admin.register(Periodo)
class PeriodoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'fecha_inicio', 'fecha_fin', 'estado', 'activo')
    list_filter = ('estado', 'activo')

@admin.register(Docente)
class DocenteAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'apellidos', 'nombres', 'dni', 'correo', 'especialidad', 'activo')
    search_fields = ('codigo', 'apellidos', 'nombres', 'dni', 'correo')
    list_filter = ('activo',)

@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'apellidos', 'nombres', 'dni', 'carrera', 'estado')
    search_fields = ('codigo', 'apellidos', 'nombres', 'dni', 'correo')
    list_filter = ('carrera', 'estado')

@admin.register(Seccion)
class SeccionAdmin(admin.ModelAdmin):
    list_display = ('periodo', 'curso', 'codigo_seccion', 'docente', 'capacidad_maxima', 'fecha_corte_predictivo', 'activo')
    search_fields = ('curso__nombre', 'curso__codigo', 'docente__apellidos', 'docente__nombres')
    list_filter = ('periodo', 'curso__carrera', 'activo')
