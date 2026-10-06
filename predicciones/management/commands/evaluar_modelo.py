from django.core.management.base import BaseCommand
from predicciones.models import VersionModelo
import json

class Command(BaseCommand):
    help = 'Muestra el reporte detallado de evaluación y calibración del modelo activo'

    def handle(self, *args, **options):
        modelo = VersionModelo.objects.filter(activo=True).first()
        if not modelo:
            self.stdout.write(self.style.WARNING("No hay ningún modelo activo en el sistema."))
            return

        self.stdout.write(self.style.SUCCESS(f"=== MODELO ACTIVO: {modelo.nombre} ({modelo.version}) ==="))
        self.stdout.write(f"Algoritmo: {modelo.get_algoritmo_display()}")
        self.stdout.write(f"Fecha de Entrenamiento: {modelo.fecha_entrenamiento}")
        self.stdout.write(f"Es Sintético: {modelo.es_sintetico}")
        self.stdout.write("\n--- Métricas de Evaluación (Conjunto de Prueba Cronológico) ---")
        self.stdout.write(json.dumps(modelo.metricas_evaluacion, indent=2))
