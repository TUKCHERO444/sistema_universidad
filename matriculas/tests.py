from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import date
from matriculas.models import Matricula, DetalleMatricula
from matriculas.services import MatriculaService
from academico.models import Carrera, Curso, Periodo, Docente, Estudiante, Seccion
from cuentas.models import Usuario

class MatriculaReglasNegocioTestCase(TestCase):
    def setUp(self):
        self.carrera = Carrera.objects.create(codigo="ADM", nombre="Administracion")
        self.curso1 = Curso.objects.create(codigo="ADM101", nombre="Admin I", carrera=self.carrera, ciclo=1, creditos=3)
        self.periodo = Periodo.objects.create(
            codigo="2025-1", nombre="2025-I",
            fecha_inicio=date.today(), fecha_fin=date.today() + date.resolution * 120,
            matricula_inicio=date.today() - date.resolution * 5, matricula_fin=date.today() + date.resolution * 5,
            estado=Periodo.EstadoPeriodo.ABIERTO, activo=True
        )
        self.user_doc = Usuario.objects.create_user(username="doc_adm", rol=Usuario.Rol.DOCENTE)
        self.docente = Docente.objects.create(codigo="D20", usuario=self.user_doc, dni="33445566", nombres="Doc", apellidos="Adm", correo="dadm@uni.edu")
        
        self.seccion_a = Seccion.objects.create(curso=self.curso1, periodo=self.periodo, docente=self.docente, codigo_seccion="A", capacidad_maxima=1, fecha_corte_predictivo=date.today() + date.resolution * 30)
        self.seccion_b = Seccion.objects.create(curso=self.curso1, periodo=self.periodo, docente=self.docente, codigo_seccion="B", capacidad_maxima=20, fecha_corte_predictivo=date.today() + date.resolution * 30)

        self.user_est1 = Usuario.objects.create_user(username="est_adm1", rol=Usuario.Rol.ESTUDIANTE)
        self.est1 = Estudiante.objects.create(codigo="E20", usuario=self.user_est1, dni="77889900", nombres="Est", apellidos="Uno", correo="e20@uni.edu", fecha_nacimiento=date(2003, 1, 1), carrera=self.carrera)

        self.user_est2 = Usuario.objects.create_user(username="est_adm2", rol=Usuario.Rol.ESTUDIANTE)
        self.est2 = Estudiante.objects.create(codigo="E21", usuario=self.user_est2, dni="77889901", nombres="Est", apellidos="Dos", correo="e21@uni.edu", fecha_nacimiento=date(2003, 1, 1), carrera=self.carrera)

        self.user_admin = Usuario.objects.create_user(username="admin_test", rol=Usuario.Rol.ADMIN, is_superuser=True)

    def test_impedir_duplicado_mismo_curso_mismo_periodo(self):
        # Intentar inscribirse en dos secciones del mismo curso
        with self.assertRaises(ValidationError):
            MatriculaService.registrar_matricula(
                estudiante_id=self.est1.id,
                periodo_id=self.periodo.id,
                secciones_ids=[self.seccion_a.id, self.seccion_b.id],
                usuario_registro=self.user_admin
            )

    def test_control_capacidad_maxima_y_sobrecupo(self):
        # Estudiante 1 ocupa la única vacante de sección A
        mat1 = MatriculaService.registrar_matricula(
            estudiante_id=self.est1.id,
            periodo_id=self.periodo.id,
            secciones_ids=[self.seccion_a.id],
            usuario_registro=self.user_admin
        )
        self.assertEqual(mat1.estado, Matricula.EstadoMatricula.REGISTRADA)
        self.assertEqual(self.seccion_a.vacantes_disponibles, 0)

        # Estudiante 2 intenta inscribirse en sección A sin vacante
        with self.assertRaises(ValidationError):
            MatriculaService.registrar_matricula(
                estudiante_id=self.est2.id,
                periodo_id=self.periodo.id,
                secciones_ids=[self.seccion_a.id],
                usuario_registro=self.user_admin
            )

    def test_anulacion_libera_vacante(self):
        mat1 = MatriculaService.registrar_matricula(
            estudiante_id=self.est1.id,
            periodo_id=self.periodo.id,
            secciones_ids=[self.seccion_a.id],
            usuario_registro=self.user_admin
        )
        self.assertEqual(self.seccion_a.vacantes_disponibles, 0)

        # Anular la matrícula
        MatriculaService.anular_matricula(mat1.id, motivo="Retiro del semestre", usuario_anulacion=self.user_admin)
        self.assertEqual(self.seccion_a.vacantes_disponibles, 1)
