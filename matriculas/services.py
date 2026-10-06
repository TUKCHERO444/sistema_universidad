from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Matricula, DetalleMatricula
from academico.models import Estudiante, Periodo, Seccion
from calificaciones.models import Calificacion
from cuentas.services import registrar_auditoria

class MatriculaService:
    @staticmethod
    def validar_pre_matricula(estudiante_id, periodo_id, secciones_ids):
        """
        Valida las condiciones antes de confirmar la matrícula y retorna el resumen.
        """
        estudiante = Estudiante.objects.select_related('carrera').get(id=estudiante_id)
        periodo = Periodo.objects.get(id=periodo_id)

        if estudiante.estado != Estudiante.EstadoEstudiante.ACTIVO:
            raise ValidationError(f"El estudiante {estudiante.nombre_completo} no se encuentra en estado ACTIVO.")

        if not periodo.esta_en_intervalo_matricula():
            raise ValidationError(f"El periodo {periodo.codigo} no se encuentra abierto o está fuera del intervalo de matrícula.")

        # Verificar si ya cuenta con matrícula activa
        matricula_existente = Matricula.objects.filter(
            estudiante=estudiante,
            periodo=periodo,
            estado=Matricula.EstadoMatricula.REGISTRADA
        ).first()
        if matricula_existente:
            raise ValidationError(f"El estudiante ya cuenta con una matrícula activa ({matricula_existente.codigo}) en el periodo {periodo.codigo}.")

        if not secciones_ids:
            raise ValidationError("Debe seleccionar al menos una sección para matricular.")

        secciones = Seccion.objects.filter(id__in=secciones_ids).select_related('curso', 'curso__carrera', 'docente')
        if len(secciones) != len(secciones_ids):
            raise ValidationError("Una o más secciones seleccionadas no son válidas.")

        # Validar coherencia de periodo
        for sec in secciones:
            if sec.periodo_id != periodo.id:
                raise ValidationError(f"La sección {sec} no pertenece al periodo {periodo.codigo}.")
            if sec.curso.carrera_id != estudiante.carrera_id:
                raise ValidationError(f"El curso {sec.curso.nombre} no corresponde a la carrera del estudiante ({estudiante.carrera.nombre}).")

        # Validar cursos duplicados
        cursos_ids = [sec.curso_id for sec in secciones]
        if len(cursos_ids) != len(set(cursos_ids)):
            raise ValidationError("No se permite matricular más de una sección del mismo curso en el mismo periodo.")

        # Validar vacantes disponibles
        resumen_secciones = []
        total_creditos = 0
        for sec in secciones:
            total_creditos += sec.curso.creditos
            resumen_secciones.append({
                'seccion': sec,
                'curso': sec.curso,
                'docente': sec.docente,
                'creditos': sec.curso.creditos,
                'vacantes_disponibles': sec.vacantes_disponibles,
                'tiene_vacante': sec.tiene_vacantes
            })

        return {
            'estudiante': estudiante,
            'periodo': periodo,
            'secciones': resumen_secciones,
            'total_creditos': total_creditos,
            'todas_con_vacante': all(item['tiene_vacante'] for item in resumen_secciones)
        }

    @classmethod
    @transaction.atomic
    def registrar_matricula(cls, estudiante_id, periodo_id, secciones_ids, usuario_registro, request=None):
        """
        Ejecuta el registro de matrícula bajo una transacción atómica con bloqueos de concurrencia.
        """
        pre = cls.validar_pre_matricula(estudiante_id, periodo_id, secciones_ids)
        estudiante = pre['estudiante']
        periodo = pre['periodo']

        # Bloqueo pesimista sobre las secciones seleccionadas para evitar sobrecupos concurrentes
        secciones_bloqueadas = Seccion.objects.select_for_update().filter(id__in=secciones_ids)
        for sec in secciones_bloqueadas:
            if sec.vacantes_disponibles <= 0:
                raise ValidationError(f"Lo sentimos, la sección {sec} ya no cuenta con vacantes disponibles.")

        # Generar código único de matrícula
        contador = Matricula.objects.filter(periodo=periodo).count() + 1
        codigo_matricula = f"MAT-{periodo.codigo}-{contador:05d}"

        matricula = Matricula.objects.create(
            codigo=codigo_matricula,
            estudiante=estudiante,
            periodo=periodo,
            total_creditos=pre['total_creditos'],
            estado=Matricula.EstadoMatricula.REGISTRADA,
            usuario_registro=usuario_registro
        )

        for sec in secciones_bloqueadas:
            detalle = DetalleMatricula.objects.create(
                matricula=matricula,
                seccion=sec,
                estado=DetalleMatricula.EstadoDetalle.INSCRITO
            )
            # Inicializar registro de calificaciones
            Calificacion.objects.create(
                detalle_matricula=detalle,
                registrado_por=usuario_registro
            )

        registrar_auditoria(
            usuario=usuario_registro,
            modulo='Matrículas',
            accion='CREAR',
            descripcion=f"Matrícula registrada {codigo_matricula} para {estudiante.nombre_completo} ({pre['total_creditos']} créditos)",
            request=request
        )

        return matricula

    @classmethod
    @transaction.atomic
    def anular_matricula(cls, matricula_id, motivo, usuario_anulacion, request=None):
        """
        Anula una matrícula registrada, liberando las vacantes y conservando el historial.
        """
        matricula = Matricula.objects.select_for_update().get(id=matricula_id)
        if matricula.estado == Matricula.EstadoMatricula.ANULADA:
            raise ValidationError("La matrícula ya se encuentra anulada.")

        if matricula.periodo.esta_cerrado:
            raise ValidationError("No se puede anular matrículas de un periodo académico cerrado.")

        matricula.estado = Matricula.EstadoMatricula.ANULADA
        matricula.motivo_anulacion = motivo
        matricula.usuario_anulacion = usuario_anulacion
        matricula.fecha_anulacion = timezone.now()
        matricula.save()

        # Actualizar detalles a ANULADO
        matricula.detalles.filter(estado=DetalleMatricula.EstadoDetalle.INSCRITO).update(
            estado=DetalleMatricula.EstadoDetalle.ANULADO
        )

        registrar_auditoria(
            usuario=usuario_anulacion,
            modulo='Matrículas',
            accion='ANULAR',
            descripcion=f"Matrícula {matricula.codigo} anulada. Motivo: {motivo}",
            request=request
        )

        return matricula
