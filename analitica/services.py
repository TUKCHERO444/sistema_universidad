import pandas as pd
import numpy as np
import plotly
import plotly.express as px
import plotly.graph_objects as go
import json
from decimal import Decimal
from django.db.models import Avg, Count, Q
from django.utils import timezone

from matriculas.models import Matricula, DetalleMatricula
from calificaciones.models import Calificacion
from asistencia.models import Asistencia, SesionClase
from academico.models import Carrera, Curso, Periodo, Seccion, Estudiante
from predicciones.models import PrediccionEstudiante, VersionModelo

class AnaliticaService:
    @staticmethod
    def obtener_alertas_por_reglas(periodo_id=None, seccion_id=None, docente=None):
        """
        Calcula alertas tempranas estrictamente basadas en REGLAS DETERMINISTAS:
        - Alerta 1: Asistencia crítica (< 70% en sesiones válidas cerradas).
        - Alerta 2: Nota 1 desaprobatoria (< 10.50 en la primera evaluación).
        - Alerta 3: Inasistencia reiterada (>= 3 faltas consecutivas o acumuladas).
        """
        detalles = DetalleMatricula.objects.filter(
            matricula__estado=Matricula.EstadoMatricula.REGISTRADA,
            estado=DetalleMatricula.EstadoDetalle.INSCRITO
        ).select_related(
            'matricula__estudiante',
            'seccion__curso',
            'seccion__docente',
            'seccion__periodo',
            'calificacion'
        )

        if periodo_id:
            detalles = detalles.filter(seccion__periodo_id=periodo_id)
        if seccion_id:
            detalles = detalles.filter(seccion_id=seccion_id)
        if docente:
            detalles = detalles.filter(seccion__docente=docente)

        alertas = []
        for det in detalles:
            estudiante = det.matricula.estudiante
            seccion = det.seccion
            calif = getattr(det, 'calificacion', None)

            # 1. Regla: Nota 1 desaprobada
            if calif and calif.nota1 is not None and calif.nota1 < Decimal('10.50'):
                alertas.append({
                    'tipo': 'REGLA_NOTA',
                    'categoria': 'Rendimiento Académico',
                    'nivel': 'PELIGRO',
                    'estudiante': estudiante,
                    'seccion': seccion,
                    'curso': seccion.curso,
                    'mensaje': f"Nota 1 deficiente ({calif.nota1})",
                    'detalle': "El estudiante obtuvo una calificación inferior a 10.50 en la primera evaluación.",
                    'accion_sugerida': "Convocar a tutoría de refuerzo antes de la Evaluación 2."
                })

            # 2. Regla: Asistencia crítica
            asists = Asistencia.objects.filter(detalle_matricula=det, sesion__cerrada=True)
            total_ses = asists.count()
            if total_ses >= 3:
                faltas = asists.filter(estado=Asistencia.EstadoAsistencia.FALTA).count()
                justificadas = asists.filter(estado=Asistencia.EstadoAsistencia.JUSTIFICADA).count()
                presentes = asists.filter(estado=Asistencia.EstadoAsistencia.PRESENTE).count()
                tardanzas = asists.filter(estado=Asistencia.EstadoAsistencia.TARDANZA).count()

                denominador = total_ses - justificadas
                if denominador > 0:
                    pct = (presentes + tardanzas) / denominador * 100
                    if pct < 70.0:
                        alertas.append({
                            'tipo': 'REGLA_ASISTENCIA',
                            'categoria': 'Inasistencia Crítica',
                            'nivel': 'PELIGRO' if pct < 60.0 else 'ADVERTENCIA',
                            'estudiante': estudiante,
                            'seccion': seccion,
                            'curso': seccion.curso,
                            'mensaje': f"Asistencia al {pct:.1f}% ({faltas} faltas de {denominador} sesiones válidas)",
                            'detalle': "La asistencia se encuentra por debajo del umbral institucional del 70%.",
                            'accion_sugerida': "Emitir citación formal y verificar justificaciones médicas/laborales."
                        })
                    elif faltas >= 3:
                        alertas.append({
                            'tipo': 'REGLA_FALTAS_ACUMULADAS',
                            'categoria': 'Faltas Reiteradas',
                            'nivel': 'ADVERTENCIA',
                            'estudiante': estudiante,
                            'seccion': seccion,
                            'curso': seccion.curso,
                            'mensaje': f"{faltas} inasistencias acumuladas",
                            'detalle': "El estudiante acumula 3 o más faltas en la asignatura.",
                            'accion_sugerida': "Contactar al estudiante para indagar motivo de ausencia."
                        })

        return alertas

    @staticmethod
    def generar_grafico_matriculas_por_carrera(periodo_id=None):
        """Distribución de estudiantes matriculados por carrera."""
        qs = DetalleMatricula.objects.filter(
            matricula__estado=Matricula.EstadoMatricula.REGISTRADA,
            estado=DetalleMatricula.EstadoDetalle.INSCRITO
        )
        if periodo_id:
            qs = qs.filter(seccion__periodo_id=periodo_id)

        data = qs.values('seccion__curso__carrera__nombre').annotate(total=Count('id')).order_by('-total')
        if not data:
            return None

        carreras = [d['seccion__curso__carrera__nombre'] for d in data]
        totales = [d['total'] for d in data]

        fig = go.Figure(data=[
            go.Bar(
                x=totales,
                y=carreras,
                orientation='h',
                marker=dict(
                    color='#1e3a8a',
                    line=dict(color='#0f172a', width=1)
                ),
                text=totales,
                textposition='auto'
            )
        ])
        fig.update_layout(
            title="Inscripciones por Programa Académico",
            xaxis_title="Cantidad de Inscripciones",
            yaxis_title="",
            margin=dict(l=20, r=20, t=40, b=20),
            height=320,
            template="plotly_white"
        )
        return json.loads(fig.to_json())

    @staticmethod
    def generar_grafico_distribucion_notas(periodo_id=None, curso_id=None):
        """Histograma de distribución de notas finales."""
        qs = Calificacion.objects.filter(
            detalle_matricula__matricula__estado=Matricula.EstadoMatricula.REGISTRADA,
            promedio_final__isnull=False
        )
        if periodo_id:
            qs = qs.filter(detalle_matricula__seccion__periodo_id=periodo_id)
        if curso_id:
            qs = qs.filter(detalle_matricula__seccion__curso_id=curso_id)

        notas = [float(c.promedio_final) for c in qs]
        if not notas:
            return None

        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=notas,
            xbins=dict(start=0, end=20, size=2),
            marker_color='#0284c7',
            opacity=0.85
        ))
        fig.add_vline(x=13.0, line_dash="dash", line_color="#dc2626", annotation_text="Aprobación (13.00)")
        fig.update_layout(
            title="Distribución de Promedios Finales",
            xaxis_title="Calificación (Escala 0 - 20)",
            yaxis_title="Cantidad de Estudiantes",
            margin=dict(l=20, r=20, t=40, b=20),
            height=320,
            template="plotly_white"
        )
        return json.loads(fig.to_json())

    @staticmethod
    def generar_grafico_aprobacion_secciones(periodo_id=None, docente=None):
        """Rendimiento de aprobados vs desaprobados vs pendientes por sección."""
        qs = Seccion.objects.all().select_related('curso', 'docente', 'periodo')
        if periodo_id:
            qs = qs.filter(periodo_id=periodo_id)
        if docente:
            qs = qs.filter(docente=docente)

        secciones_labels = []
        aprobados = []
        desaprobados = []
        pendientes = []

        for sec in qs[:12]:
            detalles = DetalleMatricula.objects.filter(seccion=sec, matricula__estado=Matricula.EstadoMatricula.REGISTRADA)
            ap = detalles.filter(calificacion__estado_aprobacion=Calificacion.EstadoAprobacion.APROBADO).count()
            des = detalles.filter(calificacion__estado_aprobacion=Calificacion.EstadoAprobacion.DESAPROBADO).count()
            pend = detalles.filter(calificacion__estado_aprobacion=Calificacion.EstadoAprobacion.PENDIENTE).count()

            if (ap + des + pend) > 0:
                secciones_labels.append(f"{sec.curso.codigo} - Sec {sec.codigo_seccion}")
                aprobados.append(ap)
                desaprobados.append(des)
                pendientes.append(pend)

        if not secciones_labels:
            return None

        fig = go.Figure(data=[
            go.Bar(name='Aprobados (>=13)', x=secciones_labels, y=aprobados, marker_color='#059669'),
            go.Bar(name='Desaprobados (<13)', x=secciones_labels, y=desaprobados, marker_color='#dc2626'),
            go.Bar(name='Pendientes', x=secciones_labels, y=pendientes, marker_color='#94a3b8')
        ])
        fig.update_layout(
            barmode='stack',
            title="Estado Académico por Sección",
            xaxis_title="Sección",
            yaxis_title="Estudiantes",
            margin=dict(l=20, r=20, t=40, b=20),
            height=320,
            template="plotly_white"
        )
        return json.loads(fig.to_json())

    @staticmethod
    def generar_grafico_evolucion_estudiante(estudiante_id):
        """Evolución académica histórica del estudiante por periodo."""
        matriculas = Matricula.objects.filter(
            estudiante_id=estudiante_id,
            estado=Matricula.EstadoMatricula.REGISTRADA
        ).select_related('periodo').order_by('periodo__fecha_inicio')

        periodos_nombres = []
        promedios_periodo = []

        for mat in matriculas:
            califs = Calificacion.objects.filter(
                detalle_matricula__matricula=mat,
                promedio_final__isnull=False
            )
            if califs.exists():
                prom = float(califs.aggregate(Avg('promedio_final'))['promedio_final__avg'])
                periodos_nombres.append(mat.periodo.codigo)
                promedios_periodo.append(round(prom, 2))

        if not periodos_nombres:
            return None

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=periodos_nombres,
            y=promedios_periodo,
            mode='lines+markers+text',
            text=[f"{p:.2f}" for p in promedios_periodo],
            textposition="top center",
            line=dict(color='#1e3a8a', width=3),
            marker=dict(size=8, color='#0284c7')
        ))
        fig.add_hline(y=13.0, line_dash="dash", line_color="#059669", annotation_text="Línea de Aprobación (13.00)")
        fig.update_layout(
            title="Evolución del Promedio Ponderado por Periodo",
            yaxis=dict(range=[0, 20]),
            margin=dict(l=20, r=20, t=40, b=20),
            height=300,
            template="plotly_white"
        )
        return json.loads(fig.to_json())
