from django.core.management.base import BaseCommand
from predicciones.ml_service import PrediccionMLService

class Command(BaseCommand):
    help = 'Ejecuta la inferencia de riesgo académico por lote utilizando el modelo activo'

    def handle(self, *args, **options):
        self.stdout.write("Ejecutando inferencia por lote...")
        res = PrediccionMLService.generar_predicciones_lote()
        if res.get('exito'):
            self.stdout.write(self.style.SUCCESS(f"Predicciones generadas exitosamente: {res.get('predicciones_generadas')} casos con el modelo {res.get('version_utilizada')}."))
        else:
            self.stdout.write(self.style.ERROR(f"Error: {res.get('mensaje')}"))
