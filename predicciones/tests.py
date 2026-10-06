from django.test import TestCase
from decimal import Decimal
from datetime import date
from academico.models import Carrera, Curso, Periodo, Docente, Estudiante, Seccion
from matriculas.models import Matricula, DetalleMatricula
from calificaciones.models import Calificacion
from asistencia.models import SesionClase, Asistencia
from predicciones.models import InstantaneaPredictiva, VersionModelo
from predicciones.ml_service import PrediccionMLService
from cuentas.models import Usuario

class PrediccionesMLTestCase(TestCase):
    def setUp(self):
        self.carrera = Carrera.objects.create(codigo="MED", nombre="Medicina")
        self.curso = Curso.objects.create(codigo="MED101", nombre="Anatomia", carrera=self.carrera, ciclo=1, creditos=5)
        
        # Periodo 1 (Cerrado - histórico)
        self.periodo1 = Periodo.objects.create(
            codigo="2024-1", nombre="2024-I",
            fecha_inicio=date(2024, 3, 1), fecha_fin=date(2024, 7, 30),
            matricula_inicio=date(2024, 2, 1), matricula_fin=date(2024, 3, 1),
            estado=Periodo.EstadoPeriodo.CERRADO, activo=False
        )

        # Periodo 2 (Vigente)
        self.periodo2 = Periodo.objects.create(
            codigo="2024-2", nombre="2024-II",
            fecha_inicio=date(2024, 8, 1), fecha_fin=date(2024, 12, 30),
            matricula_inicio=date(2024, 7, 1), matricula_fin=date(2024, 8, 1),
            estado=Periodo.EstadoPeriodo.ABIERTO, activo=True
        )

        self.user_doc = Usuario.objects.create_user(username="doc_med", rol=Usuario.Rol.DOCENTE)
        self.docente = Docente.objects.create(codigo="D30", usuario=self.user_doc, dni="44556677", nombres="Doc", apellidos="Med", correo="dmed@uni.edu")

        self.seccion1 = Seccion.objects.create(curso=self.curso, periodo=self.periodo1, docente=self.docente, codigo_seccion="01", capacidad_maxima=30, fecha_corte_predictivo=date(2024, 4, 15))
        self.seccion2 = Seccion.objects.create(curso=self.curso, periodo=self.periodo2, docente=self.docente, codigo_seccion="01", capacidad_maxima=30, fecha_corte_predictivo=date(2024, 9, 15))

        self.user_est = Usuario.objects.create_user(username="est_med", rol=Usuario.Rol.ESTUDIANTE)
        self.est = Estudiante.objects.create(codigo="E30", usuario=self.user_est, dni="88990011", nombres="Est", apellidos="Med", correo="emed@uni.edu", fecha_nacimiento=date(2003, 1, 1), carrera=self.carrera)

    def test_instantanea_predictiva_no_contiene_data_leakage(self):
        # Crear matrícula y notas
        mat = Matricula.objects.create(codigo="MAT-P1-01", estudiante=self.est, periodo=self.periodo1, total_creditos=5)
        det = DetalleMatricula.objects.create(matricula=mat, seccion=self.seccion1)
        
        # Asignar calificaciones: N1, N2, N3 y promedio final
        calif = Calificacion.objects.create(
            detalle_matricula=det,
            nota1=Decimal('08.50'),
            nota2=Decimal('10.00'),
            nota3=Decimal('11.00')
        )

        # Crear asistencias antes y después de la fecha de corte (2024-04-15)
        ses_antes = SesionClase.objects.create(seccion=self.seccion1, fecha=date(2024, 4, 10), hora_inicio="08:00", hora_fin="10:00", cerrada=True)
        Asistencia.objects.create(sesion=ses_antes, detalle_matricula=det, estado=Asistencia.EstadoAsistencia.FALTA)

        ses_despues = SesionClase.objects.create(seccion=self.seccion1, fecha=date(2024, 5, 10), hora_inicio="08:00", hora_fin="10:00", cerrada=True)
        Asistencia.objects.create(sesion=ses_despues, detalle_matricula=det, estado=Asistencia.EstadoAsistencia.PRESENTE)

        # Generar snapshot
        snapshot = PrediccionMLService.generar_instantanea_para_inscripcion(det, forzar=True)

        # 1. Nota 1 debe ser exactamente lo conocido
        self.assertEqual(snapshot.nota1, Decimal('08.50'))
        
        # 2. Asistencia al corte solo debe contar la sesión antes del corte (1 sesión: FALTA -> 0%)
        self.assertEqual(snapshot.sesiones_consideradas, 1)
        self.assertEqual(snapshot.total_faltas, 1)
        self.assertEqual(snapshot.porcentaje_asistencia, Decimal('0.00'))

        # 3. Variable target debe ser 1 (Desaprobado: promedio 9.83 < 13.00)
        self.assertEqual(snapshot.resultado_real_desaprobado, 1)
