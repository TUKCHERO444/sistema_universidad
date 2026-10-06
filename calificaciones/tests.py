from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from calificaciones.models import Calificacion, HistorialCalificacion
from calificaciones.services import CalificacionService
from academico.models import Carrera, Curso, Periodo, Docente, Estudiante, Seccion
from matriculas.models import Matricula, DetalleMatricula
from cuentas.models import Usuario

class CalificacionCalculoTestCase(TestCase):
    def setUp(self):
        self.carrera = Carrera.objects.create(codigo="SIS", nombre="Sistemas")
        self.curso = Curso.objects.create(codigo="CS101", nombre="Programacion", carrera=self.carrera, ciclo=1, creditos=4)
        self.periodo = Periodo.objects.create(
            codigo="2025-1", nombre="2025-I",
            fecha_inicio="2025-03-01", fecha_fin="2025-07-30",
            matricula_inicio="2025-02-01", matricula_fin="2025-03-01",
            estado=Periodo.EstadoPeriodo.ABIERTO, activo=True
        )
        self.user_doc = Usuario.objects.create_user(username="doc1", rol=Usuario.Rol.DOCENTE)
        self.docente = Docente.objects.create(codigo="D1", usuario=self.user_doc, dni="12345678", nombres="Doc", apellidos="Uno", correo="d1@uni.edu")
        self.seccion = Seccion.objects.create(curso=self.curso, periodo=self.periodo, docente=self.docente, codigo_seccion="01", capacidad_maxima=30, fecha_corte_predictivo="2025-04-15")
        
        self.user_est = Usuario.objects.create_user(username="est1", rol=Usuario.Rol.ESTUDIANTE)
        self.estudiante = Estudiante.objects.create(codigo="E1", usuario=self.user_est, dni="87654321", nombres="Est", apellidos="Uno", correo="e1@uni.edu", fecha_nacimiento="2003-01-01", carrera=self.carrera)
        
        self.matricula = Matricula.objects.create(codigo="MAT-01", estudiante=self.estudiante, periodo=self.periodo, total_creditos=4)
        self.detalle = DetalleMatricula.objects.create(matricula=self.matricula, seccion=self.seccion)

    def test_promedio_aritmetico_decimal_round_half_up(self):
        # Caso 1: (13 + 13 + 12) / 3 = 38 / 3 = 12.6666... -> 12.67 (Desaprobado < 13.00)
        calif = Calificacion.objects.create(
            detalle_matricula=self.detalle,
            nota1=Decimal('13.00'),
            nota2=Decimal('13.00'),
            nota3=Decimal('12.00')
        )
        self.assertEqual(calif.promedio_final, Decimal('12.67'))
        self.assertEqual(calif.estado_aprobacion, Calificacion.EstadoAprobacion.DESAPROBADO)

        # Caso 2: (13 + 13 + 13) / 3 = 13.00 -> 13.00 (Aprobado >= 13.00)
        calif.nota3 = Decimal('13.00')
        calif.save()
        self.assertEqual(calif.promedio_final, Decimal('13.00'))
        self.assertEqual(calif.estado_aprobacion, Calificacion.EstadoAprobacion.APROBADO)

        # Caso 3: (10.50 + 14.25 + 15.80) / 3 = 40.55 / 3 = 13.51666... -> 13.52 (Aprobado)
        calif.nota1 = Decimal('10.50')
        calif.nota2 = Decimal('14.25')
        calif.nota3 = Decimal('15.80')
        calif.save()
        self.assertEqual(calif.promedio_final, Decimal('13.52'))
        self.assertEqual(calif.estado_aprobacion, Calificacion.EstadoAprobacion.APROBADO)

    def test_nota_faltante_es_pendiente(self):
        # Si falta una nota, el promedio debe ser None y estado PENDIENTE
        calif = Calificacion.objects.create(
            detalle_matricula=self.detalle,
            nota1=Decimal('15.00'),
            nota2=Decimal('14.00'),
            nota3=None
        )
        self.assertIsNone(calif.promedio_final)
        self.assertEqual(calif.estado_aprobacion, Calificacion.EstadoAprobacion.PENDIENTE)

    def test_cero_es_nota_valida(self):
        # 0.00 es una nota válida (no es None) -> (0 + 15 + 15) / 3 = 30 / 3 = 10.00 (Desaprobado)
        calif = Calificacion.objects.create(
            detalle_matricula=self.detalle,
            nota1=Decimal('0.00'),
            nota2=Decimal('15.00'),
            nota3=Decimal('15.00')
        )
        self.assertEqual(calif.promedio_final, Decimal('10.00'))
        self.assertEqual(calif.estado_aprobacion, Calificacion.EstadoAprobacion.DESAPROBADO)
