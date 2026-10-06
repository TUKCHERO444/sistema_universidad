from django.core.management.base import BaseCommand
from predicciones.ml_service import PrediccionMLService

class Command(BaseCommand):
    help = 'Entrena y evalúa cronológicamente los modelos predictivos de riesgo académico'

    def handle(self, *args, **options):
        self.stdout.write("Ejecutando pipeline reproducible de entrenamiento y evaluación...")
        res = PrediccionMLService.entrenar_y_evaluar_modelos(es_sintetico=True)
        if res.get('exito'):
            self.stdout.write(self.style.SUCCESS(f"Entrenamiento exitoso. Modelos evaluados: {res.get('modelos_evaluados')}. Modelo Activo: {res.get('modelo_activo')}"))
        else:
            self.stdout.write(self.style.ERROR(f"Error: {res.get('mensaje')}"))
