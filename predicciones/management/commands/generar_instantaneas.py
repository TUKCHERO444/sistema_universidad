from django.core.management.base import BaseCommand
from predicciones.ml_service import PrediccionMLService

class Command(BaseCommand):
    help = 'Construye las instantáneas predictivas inmutables a la fecha de corte de cada sección'

    def handle(self, *args, **options):
        self.stdout.write("Construyendo snapshots inmutables al corte...")
        total = PrediccionMLService.construir_todas_las_instantaneas()
        self.stdout.write(self.style.SUCCESS(f"Se procesaron {total} instantáneas predictivas."))
