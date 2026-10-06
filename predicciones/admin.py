from django.contrib import admin
from .models import InstantaneaPredictiva, VersionModelo, PrediccionEstudiante

@admin.register(InstantaneaPredictiva)
class InstantaneaPredictivaAdmin(admin.ModelAdmin):
    list_display = ('detalle_matricula', 'fecha_corte', 'nota1', 'porcentaje_asistencia', 'total_faltas', 'resultado_real_desaprobado', 'es_sintetico')
    list_filter = ('es_sintetico', 'resultado_real_desaprobado', 'fecha_corte')
    search_fields = ('detalle_matricula__matricula__estudiante__apellidos', 'detalle_matricula__seccion__curso__nombre')

@admin.register(VersionModelo)
class VersionModeloAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'algoritmo', 'version', 'activo', 'es_sintetico', 'fecha_entrenamiento')
    list_filter = ('activo', 'algoritmo', 'es_sintetico')
    search_fields = ('nombre', 'version')

@admin.register(PrediccionEstudiante)
class PrediccionEstudianteAdmin(admin.ModelAdmin):
    list_display = ('instantanea', 'version_modelo', 'probabilidad_riesgo', 'nivel_riesgo', 'calibrado', 'fecha_prediccion')
    list_filter = ('nivel_riesgo', 'version_modelo', 'calibrado')
    search_fields = ('instantanea__detalle_matricula__matricula__estudiante__apellidos',)
