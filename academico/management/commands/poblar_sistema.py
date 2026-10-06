import random
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction

from cuentas.models import Usuario
from academico.models import Carrera, Curso, Periodo, Docente, Estudiante, Seccion
from matriculas.models import Matricula, DetalleMatricula
from calificaciones.models import Calificacion
from asistencia.models import SesionClase, Asistencia
from predicciones.ml_service import PrediccionMLService
from predicciones.models import VersionModelo

class Command(BaseCommand):
    help = 'Puebla la base de datos con un ecosistema académico multi-periodo y modelos predictivos'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Iniciando generación de datos sintéticos reproducibles para demostración..."))

        random.seed(42)

        with transaction.atomic():
            # 1. Carreras
            carreras_data = [
                {'codigo': 'ING-SIS', 'nombre': 'Ingeniería de Sistemas e Informática', 'desc': 'Formación en software, computación, arquitectura y ciencia de datos.'},
                {'codigo': 'MED-HUM', 'nombre': 'Medicina Humana', 'desc': 'Ciencias de la salud, medicina clínica y preventiva.'},
                {'codigo': 'ADM-EMP', 'nombre': 'Administración de Empresas', 'desc': 'Gestión estratégica, finanzas, operaciones y negocios globales.'},
                {'codigo': 'DER-POL', 'nombre': 'Derecho y Ciencias Políticas', 'desc': 'Estudios jurídicos, derecho procesal, civil y corporativo.'},
            ]
            carreras_dict = {}
            for c in carreras_data:
                obj, _ = Carrera.objects.get_or_create(
                    codigo=c['codigo'],
                    defaults={'nombre': c['nombre'], 'descripcion': c['desc'], 'activo': True}
                )
                carreras_dict[c['codigo']] = obj

            # 2. Cursos
            cursos_data = [
                # Sistemas
                ('CS-101', 'Fundamentos de Programación', 'ING-SIS', 1, 4),
                ('CS-102', 'Cálculo Diferencial e Integral', 'ING-SIS', 1, 4),
                ('CS-201', 'Estructuras de Datos y Algoritmos', 'ING-SIS', 2, 4),
                ('CS-202', 'Base de Datos y Modelado Relacional', 'ING-SIS', 2, 3),
                ('CS-301', 'Ingeniería de Software & Arquitectura', 'ING-SIS', 3, 4),
                ('CS-302', 'Inteligencia Artificial y Machine Learning', 'ING-SIS', 3, 4),
                # Medicina
                ('MED-101', 'Anatomía Humana I', 'MED-HUM', 1, 5),
                ('MED-102', 'Biología Celular y Genética', 'MED-HUM', 1, 4),
                ('MED-201', 'Fisiología Médica', 'MED-HUM', 2, 5),
                ('MED-202', 'Bioquímica Médica', 'MED-HUM', 2, 4),
                # Administración
                ('ADM-101', 'Fundamentos de Administración', 'ADM-EMP', 1, 3),
                ('ADM-102', 'Contabilidad Financiera', 'ADM-EMP', 1, 4),
                ('ADM-201', 'Microeconomía para los Negocios', 'ADM-EMP', 2, 4),
                ('ADM-202', 'Marketing Estratégico', 'ADM-EMP', 2, 3),
                # Derecho
                ('DER-101', 'Introducción a las Ciencias Jurídicas', 'DER-POL', 1, 3),
                ('DER-102', 'Derecho Constitucional', 'DER-POL', 1, 4),
                ('DER-201', 'Derecho Civil: Personas y Acto Jurídico', 'DER-POL', 2, 4),
                ('DER-202', 'Derecho Penal General', 'DER-POL', 2, 4),
            ]
            cursos_list = []
            for cod, nom, car_cod, ciclo, cred in cursos_data:
                curso_obj, _ = Curso.objects.get_or_create(
                    codigo=cod,
                    carrera=carreras_dict[car_cod],
                    defaults={'nombre': nom, 'ciclo': ciclo, 'creditos': cred, 'activo': True}
                )
                cursos_list.append(curso_obj)

            # 3. Periodos Académicos
            periodos_data = [
                {'cod': '2024-1', 'nom': 'Semestre 2024-I', 'ini': date(2024, 3, 15), 'fin': date(2024, 7, 20), 'mini': date(2024, 2, 15), 'mfin': date(2024, 3, 10), 'estado': Periodo.EstadoPeriodo.CERRADO, 'activo': False},
                {'cod': '2024-2', 'nom': 'Semestre 2024-II', 'ini': date(2024, 8, 15), 'fin': date(2024, 12, 20), 'mini': date(2024, 7, 15), 'mfin': date(2024, 8, 10), 'estado': Periodo.EstadoPeriodo.CERRADO, 'activo': False},
                {'cod': '2025-1', 'nom': 'Semestre 2025-I', 'ini': date(2025, 3, 15), 'fin': date(2025, 7, 20), 'mini': date(2025, 2, 15), 'mfin': date(2025, 3, 10), 'estado': Periodo.EstadoPeriodo.CERRADO, 'activo': False},
                {'cod': '2025-2', 'nom': 'Semestre 2025-II (Vigente)', 'ini': date(2025, 8, 15), 'fin': date(2025, 12, 20), 'mini': date(2025, 7, 15), 'mfin': date(2025, 12, 10), 'estado': Periodo.EstadoPeriodo.ABIERTO, 'activo': True},
            ]
            periodos_dict = {}
            for p in periodos_data:
                p_obj, _ = Periodo.objects.get_or_create(
                    codigo=p['cod'],
                    defaults={
                        'nombre': p['nom'],
                        'fecha_inicio': p['ini'],
                        'fecha_fin': p['fin'],
                        'matricula_inicio': p['mini'],
                        'matricula_fin': p['mfin'],
                        'estado': p['estado'],
                        'activo': p['activo']
                    }
                )
                periodos_dict[p['cod']] = p_obj

            # 4. Docentes
            nombres_doc = [
                ('Carlos', 'Mendoza Varga', 'carlos.mendoza@universidad.edu.pe', 'Inteligencia Artificial y Algoritmos'),
                ('María', 'Ríos Salazar', 'maria.rios@universidad.edu.pe', 'Arquitectura de Software y BD'),
                ('Jorge', 'Flores Quispe', 'jorge.flores@universidad.edu.pe', 'Medicina Interna y Fisiología'),
                ('Ana', 'Gutiérrez Morales', 'ana.gutierrez@universidad.edu.pe', 'Genética Médica'),
                ('Ricardo', 'Paredes Castillo', 'ricardo.paredes@universidad.edu.pe', 'Finanzas y Gestión de Proyectos'),
                ('Elena', 'Vargas Torres', 'elena.vargas@universidad.edu.pe', 'Marketing y Emprendimiento'),
                ('Víctor', 'Cárdenas Silva', 'victor.cardenas@universidad.edu.pe', 'Derecho Constitucional y Penal'),
                ('Patricia', 'Huamán Díaz', 'patricia.huaman@universidad.edu.pe', 'Derecho Civil y Procesal'),
            ]
            docentes_list = []
            for i, (nom, ape, email, esp) in enumerate(nombres_doc, start=1):
                cod_doc = f"DOC-{i:03d}"
                username = f"docente{i}"
                u, _ = Usuario.objects.get_or_create(
                    username=username,
                    defaults={
                        'first_name': nom,
                        'last_name': ape,
                        'email': email,
                        'dni': f"4000000{i}",
                        'rol': Usuario.Rol.DOCENTE
                    }
                )
                u.set_password('admin123')
                u.save()

                d_obj, _ = Docente.objects.get_or_create(
                    codigo=cod_doc,
                    usuario=u,
                    defaults={
                        'dni': f"4000000{i}",
                        'nombres': nom,
                        'apellidos': ape,
                        'correo': email,
                        'especialidad': esp,
                        'activo': True
                    }
                )
                docentes_list.append(d_obj)

            # 5. Estudiantes (60 estudiantes distribuidos)
            apellidos_pool = ['Gómez', 'Quispe', 'Rojas', 'Mamani', 'Díaz', 'Castillo', 'Torres', 'Flores', 'Vega', 'Morales', 'Paredes', 'Silva', 'Ramos', 'Huamán', 'Espinoza', 'Vásquez', 'Campos', 'Herrera', 'Medina', 'Cruz']
            nombres_pool = ['Aldair', 'Luciana', 'Diego', 'Camila', 'Mateo', 'Valeria', 'Sebastián', 'Gabriela', 'Alejandro', 'Fiorella', 'Renzo', 'Sofía', 'Daniel', 'Andrea', 'Gabriel', 'Natalia', 'Joaquín', 'Paola', 'Gonzalo', 'Mariana']

            estudiantes_list = []
            carreras_keys = list(carreras_dict.keys())

            for i in range(1, 61):
                nom = nombres_pool[i % len(nombres_pool)]
                ape = f"{apellidos_pool[i % len(apellidos_pool)]} {apellidos_pool[(i+3) % len(apellidos_pool)]}"
                cod_est = f"EST-2024-{i:03d}"
                username = f"estudiante{i}"
                car = carreras_dict[carreras_keys[i % len(carreras_keys)]]

                u, _ = Usuario.objects.get_or_create(
                    username=username,
                    defaults={
                        'first_name': nom,
                        'last_name': ape,
                        'email': f"{username}@estudiante.universidad.edu.pe",
                        'dni': f"700000{i:02d}",
                        'rol': Usuario.Rol.ESTUDIANTE
                    }
                )
                u.set_password('admin123')
                u.save()

                e_obj, _ = Estudiante.objects.get_or_create(
                    codigo=cod_est,
                    usuario=u,
                    defaults={
                        'dni': f"700000{i:02d}",
                        'nombres': nom,
                        'apellidos': ape,
                        'correo': f"{username}@estudiante.universidad.edu.pe",
                        'telefono': f"987654{i:03d}",
                        'fecha_nacimiento': date(2003, (i % 12) + 1, (i % 28) + 1),
                        'carrera': car,
                        'estado': Estudiante.EstadoEstudiante.ACTIVO
                    }
                )
                estudiantes_list.append(e_obj)

            # 6. Secciones para todos los periodos
            secciones_creadas = []
            for p_cod, per in periodos_dict.items():
                corte_fecha = per.fecha_inicio + timedelta(days=45)
                for cur in cursos_list:
                    # Asignar un docente según especialidad
                    doc = docentes_list[cur.id % len(docentes_list)]
                    sec, _ = Seccion.objects.get_or_create(
                        curso=cur,
                        periodo=per,
                        codigo_seccion='01',
                        defaults={
                            'docente': doc,
                            'capacidad_maxima': 35,
                            'fecha_corte_predictivo': corte_fecha,
                            'activo': True
                        }
                    )
                    secciones_creadas.append(sec)

            # 7. Matrículas, Asistencia y Calificaciones multi-periodo
            admin_user = Usuario.objects.filter(is_superuser=True).first()
            detalles_totales = []

            for p_cod, per in periodos_dict.items():
                es_cerrado = (per.estado == Periodo.EstadoPeriodo.CERRADO)
                secciones_periodo = [s for s in secciones_creadas if s.periodo_id == per.id]

                for idx, est in enumerate(estudiantes_list):
                    secciones_est = [s for s in secciones_periodo if s.curso.carrera_id == est.carrera_id][:3]
                    if not secciones_est:
                        continue

                    tot_cred = sum(s.curso.creditos for s in secciones_est)
                    cod_mat = f"MAT-{per.codigo}-{idx+1:04d}"

                    mat, _ = Matricula.objects.get_or_create(
                        codigo=cod_mat,
                        estudiante=est,
                        periodo=per,
                        defaults={
                            'total_creditos': tot_cred,
                            'estado': Matricula.EstadoMatricula.REGISTRADA,
                            'usuario_registro': admin_user
                        }
                    )

                    for sec in secciones_est:
                        det, _ = DetalleMatricula.objects.get_or_create(
                            matricula=mat,
                            seccion=sec,
                            defaults={'estado': DetalleMatricula.EstadoDetalle.INSCRITO}
                        )
                        detalles_totales.append(det)

                        # Generar sesiones de clase (8 sesiones por sección)
                        fecha_cursor = per.fecha_inicio + timedelta(days=7)
                        for s_num in range(1, 9):
                            ses, _ = SesionClase.objects.get_or_create(
                                seccion=sec,
                                fecha=fecha_cursor,
                                hora_inicio=timezone.datetime.strptime('08:00', '%H:%M').time(),
                                defaults={
                                    'hora_fin': timezone.datetime.strptime('10:00', '%H:%M').time(),
                                    'tema': f'Unidad {s_num}: Contenidos de la clase {s_num}',
                                    'cerrada': True,
                                    'cerrada_por': admin_user,
                                    'creado_por': admin_user
                                }
                            )

                            # Asistencia probabilística coherente
                            # Si es estudiante propenso a desaprobar, más faltas
                            riesgo_base = (est.id % 4 == 0) # 25% de estudiantes tienen mayor riesgo
                            if riesgo_base:
                                estado_asist = random.choices(['PRESENTE', 'TARDANZA', 'FALTA', 'JUSTIFICADA'], weights=[0.50, 0.15, 0.30, 0.05])[0]
                            else:
                                estado_asist = random.choices(['PRESENTE', 'TARDANZA', 'FALTA', 'JUSTIFICADA'], weights=[0.85, 0.10, 0.03, 0.02])[0]

                            Asistencia.objects.get_or_create(
                                sesion=ses,
                                detalle_matricula=det,
                                defaults={'estado': estado_asist, 'registrado_por': admin_user}
                            )
                            fecha_cursor += timedelta(days=7)

                        # Calificaciones
                        # Generamos notas con Decimal
                        if riesgo_base:
                            n1 = Decimal(str(round(random.uniform(5.0, 11.5), 2)))
                            n2 = Decimal(str(round(random.uniform(6.0, 12.0), 2)))
                            n3 = Decimal(str(round(random.uniform(5.0, 12.5), 2)))
                        else:
                            n1 = Decimal(str(round(random.uniform(11.0, 19.5), 2)))
                            n2 = Decimal(str(round(random.uniform(12.0, 19.0), 2)))
                            n3 = Decimal(str(round(random.uniform(12.5, 20.0), 2)))

                        if es_cerrado:
                            # Periodo cerrado: Las 3 notas están asignadas y promediadas
                            calif, _ = Calificacion.objects.get_or_create(
                                detalle_matricula=det,
                                defaults={'nota1': n1, 'nota2': n2, 'nota3': n3, 'registrado_por': admin_user}
                            )
                            calif.save() # Ejecuta cálculo con ROUND_HALF_UP
                        else:
                            # Periodo activo actual (2025-2): Solo Nota 1 o Nota 1+2 (al corte)
                            calif, _ = Calificacion.objects.get_or_create(
                                detalle_matricula=det,
                                defaults={'nota1': n1, 'nota2': None, 'nota3': None, 'registrado_por': admin_user}
                            )
                            calif.save()

        self.stdout.write(self.style.SUCCESS("Datos académicos multi-periodo generados exitosamente."))
        self.stdout.write("Generando instantáneas predictivas y ejecutando entrenamiento del Pipeline ML...")

        # 8. Generación de Instantáneas Inmutables
        creados = PrediccionMLService.construir_todas_las_instantaneas()
        self.stdout.write(f"Instantáneas creadas: {creados}")

        # 9. Entrenamiento y Evaluación Cronológica de Modelos
        res_train = PrediccionMLService.entrenar_y_evaluar_modelos(usuario=admin_user, es_sintetico=True)
        if res_train.get('exito'):
            self.stdout.write(self.style.SUCCESS(f"Modelos evaluados con éxito. Modelo activado: {res_train.get('modelo_activo')}"))
            # 10. Inferencias por lote para periodo vigente
            res_pred = PrediccionMLService.generar_predicciones_lote()
            self.stdout.write(self.style.SUCCESS(f"Predicciones generadas para el periodo vigente: {res_pred.get('predicciones_generadas')} casos."))
        else:
            self.stdout.write(self.style.WARNING(f"Resultado de entrenamiento: {res_train}"))

        self.stdout.write(self.style.SUCCESS("¡Población y setup del sistema completados al 100%!"))
