from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import SesionClase, Asistencia, HistorialAsistencia
from matriculas.models import DetalleMatricula
from cuentas.services import registrar_auditoria

class AsistenciaService:
    @staticmethod
    def calcular_resumen_asistencia(detalle_matricula_id):
        """
        Calcula las métricas de asistencia acumulada para una inscripción:
        - Solo considera sesiones CERRADAS.
        - Presente y Tardanza cuentan como asistencia.
        - Falta cuenta como ausencia.
        - Justificación se excluye del denominador.
        - Si no hay sesiones válidas evaluadas, retorna None (Sin datos).
        """
        asistencias = Asistencia.objects.filter(
            detalle_matricula_id=detalle_matricula_id,
            sesion__cerrada=True
        ).select_related('sesion')

        total_sesiones = asistencias.count()
        if total_sesiones == 0:
            return {
                'total_sesiones': 0,
                'presentes': 0,
                'tardanzas': 0,
                'faltas': 0,
                'justificadas': 0,
                'denominador_valido': 0,
                'porcentaje': None,
                'porcentaje_str': "Sin datos"
            }

        presentes = asistencias.filter(estado=Asistencia.EstadoAsistencia.PRESENTE).count()
        tardanzas = asistencias.filter(estado=Asistencia.EstadoAsistencia.TARDANZA).count()
        faltas = asistencias.filter(estado=Asistencia.EstadoAsistencia.FALTA).count()
        justificadas = asistencias.filter(estado=Asistencia.EstadoAsistencia.JUSTIFICADA).count()

        denominador = total_sesiones - justificadas
        if denominador <= 0:
            return {
                'total_sesiones': total_sesiones,
                'presentes': presentes,
                'tardanzas': tardanzas,
                'faltas': faltas,
                'justificadas': justificadas,
                'denominador_valido': 0,
                'porcentaje': None,
                'porcentaje_str': "Sin datos"
            }

        numerador = presentes + tardanzas
        porcentaje = (Decimal(numerador) / Decimal(denominador) * Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        return {
            'total_sesiones': total_sesiones,
            'presentes': presentes,
            'tardanzas': tardanzas,
            'faltas': faltas,
            'justificadas': justificadas,
            'denominador_valido': denominador,
            'porcentaje': porcentaje,
            'porcentaje_str': f"{porcentaje}%"
        }

    @classmethod
    @transaction.atomic
    def registrar_o_actualizar_asistencias(cls, sesion_id, asistencias_dict, usuario, request=None):
        """
        asistencias_dict = { detalle_matricula_id: {'estado': 'PRESENTE', 'observacion': ''} }
        """
        sesion = SesionClase.objects.select_for_update().get(id=sesion_id)
        if sesion.seccion.periodo.esta_cerrado:
            raise ValidationError("No se pueden modificar asistencias en un periodo académico cerrado.")

        inscritos_ids = set(DetalleMatricula.objects.filter(
            seccion=sesion.seccion,
            estado=DetalleMatricula.EstadoDetalle.INSCRITO
        ).values_list('id', flat=True))

        for det_id, data in asistencias_dict.items():
            det_id_int = int(det_id)
            if det_id_int not in inscritos_ids:
                continue

            nuevo_estado = data.get('estado')
            nueva_obs = data.get('observacion', '')

            asistencia_obj, created = Asistencia.objects.get_or_create(
                sesion=sesion,
                detalle_matricula_id=det_id_int,
                defaults={
                    'estado': nuevo_estado,
                    'observacion': nueva_obs,
                    'registrado_por': usuario
                }
            )

            if not created and asistencia_obj.estado != nuevo_estado:
                # Guardar en historial de cambios
                HistorialAsistencia.objects.create(
                    asistencia=asistencia_obj,
                    estado_anterior=asistencia_obj.estado,
                    estado_nuevo=nuevo_estado,
                    motivo_cambio=f"Actualización manual por {usuario.username}. Obs: {nueva_obs}",
                    modificado_por=usuario
                )
                asistencia_obj.estado = nuevo_estado
                asistencia_obj.observacion = nueva_obs
                asistencia_obj.save()

        # Verificar si todos los estudiantes inscritos ya tienen registro para cerrar la sesión si aplica
        total_asistencias_registradas = Asistencia.objects.filter(sesion=sesion).count()
        if total_asistencias_registradas >= len(inscritos_ids) and len(inscritos_ids) > 0:
            sesion.cerrada = True
            sesion.cerrada_por = usuario
            sesion.fecha_cierre = timezone.now()
            sesion.save()

        registrar_auditoria(
            usuario=usuario,
            modulo='Asistencia',
            accion='REGISTRAR_MATRIZ',
            descripcion=f"Asistencias registradas/actualizadas para sesión {sesion}",
            request=request
        )

        return sesion
