from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Calificacion, HistorialCalificacion
from cuentas.services import registrar_auditoria

class CalificacionService:
    @classmethod
    @transaction.atomic
    def actualizar_notas(cls, calificacion_id, nota1, nota2, nota3, usuario, motivo="Actualización de registro", request=None):
        """
        Actualiza las notas de una calificación registrando historial para cada cambio.
        """
        calificacion = Calificacion.objects.select_for_update().get(id=calificacion_id)
        periodo = calificacion.detalle_matricula.seccion.periodo
        
        if periodo.esta_cerrado:
            raise ValidationError("No se pueden modificar calificaciones en un periodo académico cerrado.")

        evaluaciones = [
            ('Evaluación 1 (N1)', calificacion.nota1, nota1),
            ('Evaluación 2 (N2)', calificacion.nota2, nota2),
            ('Evaluación 3 (N3)', calificacion.nota3, nota3)
        ]

        def normalizar_nota(n):
            if n is None or str(n).strip() == '':
                return None
            val = Decimal(str(n).strip())
            if val < Decimal('0.00') or val > Decimal('20.00'):
                raise ValidationError(f"La nota {val} está fuera del rango permitido (0.00 a 20.00).")
            return val

        n1_parsed = normalizar_nota(nota1)
        n2_parsed = normalizar_nota(nota2)
        n3_parsed = normalizar_nota(nota3)

        cambios = [
            ('Evaluación 1 (N1)', calificacion.nota1, n1_parsed),
            ('Evaluación 2 (N2)', calificacion.nota2, n2_parsed),
            ('Evaluación 3 (N3)', calificacion.nota3, n3_parsed),
        ]

        for eval_nombre, valor_antiguo, valor_nuevo in cambios:
            if valor_antiguo != valor_nuevo:
                HistorialCalificacion.objects.create(
                    calificacion=calificacion,
                    evaluacion=eval_nombre,
                    nota_anterior=valor_antiguo,
                    nota_nueva=valor_nuevo,
                    motivo_cambio=motivo,
                    modificado_por=usuario
                )

        calificacion.nota1 = n1_parsed
        calificacion.nota2 = n2_parsed
        calificacion.nota3 = n3_parsed
        calificacion.registrado_por = usuario
        calificacion.save()

        registrar_auditoria(
            usuario=usuario,
            modulo='Calificaciones',
            accion='ACTUALIZAR',
            descripcion=f"Calificaciones actualizadas para {calificacion.detalle_matricula}. Promedio Final: {calificacion.promedio_final}",
            request=request
        )

        return calificacion
