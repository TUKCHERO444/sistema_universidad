from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from datetime import date, time
from asistencia.models import SesionClase, Asistencia
from asistencia.services import AsistenciaService
from academico.models import Carrera, Curso, Periodo, Docente, Estudiante, Seccion
from matriculas.models import Matricula, DetalleMatricula
from cuentas.models import Usuario

class AsistenciaCalculoTestCase(TestCase):
    def setUp(self):
        self.carrera = Carrera.objects.create(codigo="DER", nombre="Derecho")
        self.curso = Curso.objects.create(codigo="DER101", nombre="Intro Derecho", carrera=self.carrera, ciclo=1, creditos=3)
        self.periodo = Periodo.objects.create(
            codigo="2025-1", nombre="2025-I",
            fecha_inicio=date(2025, 3, 1), fecha_fin=date(2025, 7, 30),
            matricula_inicio=date(2025, 2, 1), matricula_fin=date(2025, 3, 1),
            estado=Periodo.EstadoPeriodo.ABIERTO, activo=True
        )
        self.user_doc = Usuario.objects.create_user(username="doc_der", rol=Usuario.Rol.DOCENTE)
        self.docente = Docente.objects.create(codigo="D10", usuario=self.user_doc, dni="22334455", nombres="Doc", apellidos="Der", correo="dder@uni.edu")
        self.seccion = Seccion.objects.create(curso=self.curso, periodo=self.periodo, docente=self.docente, codigo_seccion="01", capacidad_maxima=30, fecha_corte_predictivo=date(2025, 4, 15))
        
        self.user_est = Usuario.objects.create_user(username="est_der", rol=Usuario.Rol.ESTUDIANTE)
        self.estudiante = Estudiante.objects.create(codigo="E10", usuario=self.user_est, dni="66778899", nombres="Est", apellidos="Der", correo="eder@uni.edu", fecha_nacimiento=date(2003, 1, 1), carrera=self.carrera)
        
        self.matricula = Matricula.objects.create(codigo="MAT-DER-01", estudiante=self.estudiante, periodo=self.periodo, total_creditos=3)
        self.detalle = DetalleMatricula.objects.create(matricula=self.matricula, seccion=self.seccion)

    def test_calculo_porcentaje_asistencia_justificada_excluida(self):
        # 4 sesiones:
        # Sesión 1: PRESENTE
        # Sesión 2: TARDANZA (cuenta como asistencia)
        # Sesión 3: FALTA (ausencia)
        # Sesión 4: JUSTIFICADA (se excluye del denominador)
        # Total válidas = 4 - 1 = 3. Asistencias = 1(P) + 1(T) = 2.
        # Porcentaje = 2 / 3 * 100 = 66.666... -> 66.67%
        
        for i in range(1, 5):
            ses = SesionClase.objects.create(
                seccion=self.seccion,
                fecha=date(2025, 3, i),
                hora_inicio=time(8, 0),
                hora_fin=time(10, 0),
                cerrada=True
            )
            estados = [Asistencia.EstadoAsistencia.PRESENTE, Asistencia.EstadoAsistencia.TARDANZA, Asistencia.EstadoAsistencia.FALTA, Asistencia.EstadoAsistencia.JUSTIFICADA]
            Asistencia.objects.create(sesion=ses, detalle_matricula=self.detalle, estado=estados[i-1])

        resumen = AsistenciaService.calcular_resumen_asistencia(self.detalle.id)
        self.assertEqual(resumen['total_sesiones'], 4)
        self.assertEqual(resumen['presentes'], 1)
        self.assertEqual(resumen['tardanzas'], 1)
        self.assertEqual(resumen['faltas'], 1)
        self.assertEqual(resumen['justificadas'], 1)
        self.assertEqual(resumen['denominador_valido'], 3)
        self.assertEqual(resumen['porcentaje'], Decimal('66.67'))

    def test_sesion_no_cerrada_no_se_cuenta(self):
        # Sesión abierta (cerrada=False) no debe entrar en el cálculo oficial
        ses_abierta = SesionClase.objects.create(
            seccion=self.seccion,
            fecha=date(2025, 3, 10),
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
            cerrada=False
        )
        Asistencia.objects.create(sesion=ses_abierta, detalle_matricula=self.detalle, estado=Asistencia.EstadoAsistencia.FALTA)

        resumen = AsistenciaService.calcular_resumen_asistencia(self.detalle.id)
        self.assertIsNone(resumen['porcentaje'])
        self.assertEqual(resumen['porcentaje_str'], "Sin datos")
