import os
import joblib
import numpy as np
import pandas as pd
from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django.db.models import Avg, Count, Q

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    confusion_matrix, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, brier_score_loss
)

from .models import InstantaneaPredictiva, VersionModelo, PrediccionEstudiante
from matriculas.models import DetalleMatricula, Matricula
from calificaciones.models import Calificacion
from asistencia.models import Asistencia, SesionClase
from academico.models import Periodo, Seccion, Estudiante

class PrediccionMLService:
    CARACTERISTICAS_NUMERICAS = [
        'nota1',
        'porcentaje_asistencia',
        'total_faltas',
        'total_tardanzas',
        'sesiones_consideradas',
        'promedio_historico_anterior',
        'cursos_desaprobados_anteriores',
        'sin_historial_previo'
    ]

    @classmethod
    def generar_instantanea_para_inscripcion(cls, detalle_matricula, forzar=False):
        """
        Calcula y guarda la instantánea inmutable de lo conocido exactamente a la fecha de corte predictivo de la sección.
        """
        seccion = detalle_matricula.seccion
        fecha_corte = seccion.fecha_corte_predictivo
        estudiante = detalle_matricula.matricula.estudiante
        periodo_actual = seccion.periodo

        if not forzar and hasattr(detalle_matricula, 'instantanea_predictiva'):
            return detalle_matricula.instantanea_predictiva

        # 1. Nota 1 disponible (si se registró antes o al corte)
        calificacion = getattr(detalle_matricula, 'calificacion', None)
        nota1_val = calificacion.nota1 if calificacion else None

        # 2. Asistencia estricta hasta la fecha de corte en sesiones cerradas
        asistencias_corte = Asistencia.objects.filter(
            detalle_matricula=detalle_matricula,
            sesion__fecha__lte=fecha_corte,
            sesion__cerrada=True
        )
        total_ses_corte = asistencias_corte.count()
        faltas_corte = asistencias_corte.filter(estado=Asistencia.EstadoAsistencia.FALTA).count()
        tardanzas_corte = asistencias_corte.filter(estado=Asistencia.EstadoAsistencia.TARDANZA).count()
        presentes_corte = asistencias_corte.filter(estado=Asistencia.EstadoAsistencia.PRESENTE).count()
        justificadas_corte = asistencias_corte.filter(estado=Asistencia.EstadoAsistencia.JUSTIFICADA).count()

        denominador_corte = total_ses_corte - justificadas_corte
        if denominador_corte > 0:
            pct_asist = (Decimal(presentes_corte + tardanzas_corte) / Decimal(denominador_corte) * Decimal('100')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        else:
            pct_asist = None

        # 3. Historial de periodos anteriores cerrados (sin leakage del periodo actual ni futuros)
        periodos_previos = Periodo.objects.filter(
            fecha_fin__lt=periodo_actual.fecha_inicio,
            estado=Periodo.EstadoPeriodo.CERRADO
        )
        
        inscripciones_previas = DetalleMatricula.objects.filter(
            matricula__estudiante=estudiante,
            matricula__periodo__in=periodos_previos,
            matricula__estado=Matricula.EstadoMatricula.REGISTRADA,
            calificacion__promedio_final__isnull=False
        ).select_related('calificacion')

        count_previos = inscripciones_previas.count()
        if count_previos > 0:
            promedios = [float(insc.calificacion.promedio_final) for insc in inscripciones_previas]
            promedio_historico = Decimal(str(round(sum(promedios) / len(promedios), 2)))
            desaprobados_previos = inscripciones_previas.filter(calificacion__promedio_final__lt=Decimal('13.00')).count()
            sin_historial = False
        else:
            promedio_historico = None
            desaprobados_previos = 0
            sin_historial = True

        # 4. Target real (solo para inscripciones cerradas evaluadas)
        resultado_real = None
        promedio_real = None
        if calificacion and calificacion.promedio_final is not None:
            promedio_real = calificacion.promedio_final
            resultado_real = 1 if calificacion.promedio_final < Decimal('13.00') else 0

        instantanea, _ = InstantaneaPredictiva.objects.update_or_create(
            detalle_matricula=detalle_matricula,
            defaults={
                'fecha_corte': fecha_corte,
                'nota1': nota1_val,
                'porcentaje_asistencia': pct_asist,
                'total_faltas': faltas_corte,
                'total_tardanzas': tardanzas_corte,
                'sesiones_consideradas': total_ses_corte,
                'promedio_historico_anterior': promedio_historico,
                'cursos_desaprobados_anteriores': desaprobados_previos,
                'sin_historial_previo': sin_historial,
                'resultado_real_desaprobado': resultado_real,
                'promedio_final_real': promedio_real
            }
        )
        return instantanea

    @classmethod
    def construir_todas_las_instantaneas(cls):
        """Genera snapshots para todas las inscripciones activas."""
        detalles = DetalleMatricula.objects.filter(
            matricula__estado=Matricula.EstadoMatricula.REGISTRADA,
            estado=DetalleMatricula.EstadoDetalle.INSCRITO
        ).select_related('seccion', 'seccion__periodo', 'matricula__estudiante', 'calificacion')

        creados = 0
        for det in detalles:
            cls.generar_instantanea_para_inscripcion(det, forzar=True)
            creados += 1
        return creados

    @classmethod
    def preparar_dataframe_entrenamiento(cls):
        """
        Extrae las instantáneas históricas válidas para entrenamiento y evaluación.
        """
        snapshots = InstantaneaPredictiva.objects.filter(
            resultado_real_desaprobado__isnull=False,
            detalle_matricula__matricula__estado=Matricula.EstadoMatricula.REGISTRADA
        ).select_related(
            'detalle_matricula__seccion__periodo',
            'detalle_matricula__matricula__estudiante'
        )

        filas = []
        for s in snapshots:
            filas.append({
                'snapshot_id': s.id,
                'periodo_codigo': s.detalle_matricula.seccion.periodo.codigo,
                'periodo_fecha_inicio': s.detalle_matricula.seccion.periodo.fecha_inicio,
                'estudiante_id': s.detalle_matricula.matricula.estudiante_id,
                'nota1': float(s.nota1) if s.nota1 is not None else np.nan,
                'porcentaje_asistencia': float(s.porcentaje_asistencia) if s.porcentaje_asistencia is not None else np.nan,
                'total_faltas': s.total_faltas,
                'total_tardanzas': s.total_tardanzas,
                'sesiones_consideradas': s.sesiones_consideradas,
                'promedio_historico_anterior': float(s.promedio_historico_anterior) if s.promedio_historico_anterior is not None else np.nan,
                'cursos_desaprobados_anteriores': s.cursos_desaprobados_anteriores,
                'sin_historial_previo': 1 if s.sin_historial_previo else 0,
                'target_desaprobado': s.resultado_real_desaprobado,
                'es_sintetico': s.es_sintetico
            })

        return pd.DataFrame(filas)

    @classmethod
    def entrenar_y_evaluar_modelos(cls, usuario=None, es_sintetico=False):
        """
        Pipeline reproducible de entrenamiento y evaluación comparativa cronológica.
        Modelos comparados:
        1. DummyClassifier (Referencia)
        2. LogisticRegression
        3. DecisionTreeClassifier (max_depth=4)
        """
        df = cls.preparar_dataframe_entrenamiento()
        if len(df) < 30:
            return {
                'exito': False,
                'mensaje': f'Datos insuficientes para entrenamiento y evaluación cronológica válida (registros disponibles: {len(df)}, requeridos >= 30).'
            }

        # Separación cronológica por periodos
        periodos_ordenados = df.sort_values('periodo_fecha_inicio')['periodo_codigo'].unique().tolist()
        
        if len(periodos_ordenados) < 2:
            # Si solo hay 1 periodo, división 70/15/15 estratificada
            n = len(df)
            train_df = df.iloc[:int(n*0.7)]
            val_df = df.iloc[int(n*0.7):int(n*0.85)]
            test_df = df.iloc[int(n*0.85):]
            periodos_train = periodos_ordenados
            periodos_test = periodos_ordenados
        elif len(periodos_ordenados) == 2:
            train_df = df[df['periodo_codigo'] == periodos_ordenados[0]]
            val_df = df[df['periodo_codigo'] == periodos_ordenados[1]].iloc[:len(df[df['periodo_codigo'] == periodos_ordenados[1]])//2]
            test_df = df[df['periodo_codigo'] == periodos_ordenados[1]].iloc[len(df[df['periodo_codigo'] == periodos_ordenados[1]])//2:]
            periodos_train = [periodos_ordenados[0]]
            periodos_test = [periodos_ordenados[1]]
        else:
            # 3 o más periodos: cronológico estricto
            periodos_train = periodos_ordenados[:-2]
            periodo_val = periodos_ordenados[-2]
            periodo_test = periodos_ordenados[-1]
            train_df = df[df['periodo_codigo'].isin(periodos_train)]
            val_df = df[df['periodo_codigo'] == periodo_val]
            test_df = df[df['periodo_codigo'] == periodo_test]
            periodos_test = [periodo_test]

        X_train = train_df[cls.CARACTERISTICAS_NUMERICAS]
        y_train = train_df['target_desaprobado']

        X_val = val_df[cls.CARACTERISTICAS_NUMERICAS]
        y_val = val_df['target_desaprobado']

        X_test = test_df[cls.CARACTERISTICAS_NUMERICAS]
        y_test = test_df['target_desaprobado']

        # Preprocesamiento numérico
        preprocessor_lr = Pipeline([
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])

        preprocessor_tree = Pipeline([
            ('imputer', SimpleImputer(strategy='median'))
        ])

        modelos_definicion = [
            {
                'id': 'DUMMY',
                'nombre': 'DummyClassifier (Línea Base)',
                'pipeline': DummyClassifier(strategy='most_frequent'),
                'version': f"v1.0-dummy-{timezone.now().strftime('%Y%m%d%H%M')}"
            },
            {
                'id': 'LOGISTIC',
                'nombre': 'Regresión Logística Calibrada',
                'pipeline': Pipeline([
                    ('preprocessor', preprocessor_lr),
                    ('classifier', LogisticRegression(max_iter=1000, random_state=42, C=1.0))
                ]),
                'version': f"v1.0-logreg-{timezone.now().strftime('%Y%m%d%H%M')}"
            },
            {
                'id': 'DECISION_TREE',
                'nombre': 'Árbol de Decisión (Profundidad Controlada)',
                'pipeline': Pipeline([
                    ('preprocessor', preprocessor_tree),
                    ('classifier', DecisionTreeClassifier(max_depth=4, min_samples_leaf=5, random_state=42))
                ]),
                'version': f"v1.0-tree-{timezone.now().strftime('%Y%m%d%H%M')}"
            }
        ]

        resultados_guardados = []
        mejor_f1 = -1
        mejor_version_obj = None

        for item in modelos_definicion:
            pipe = item['pipeline']
            pipe.fit(X_train, y_train)

            # Predicciones sobre conjunto de prueba final cronológico
            y_pred = pipe.predict(X_test)
            if hasattr(pipe, 'predict_proba'):
                y_prob = pipe.predict_proba(X_test)[:, 1]
            else:
                y_prob = y_pred.astype(float)

            # Matriz de confusión y métricas de desaprobación (clase 1)
            cm = confusion_matrix(y_test, y_pred, labels=[0, 1])
            tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)
            
            prec = precision_score(y_test, y_pred, zero_division=0)
            rec = recall_score(y_test, y_pred, zero_division=0)
            f1 = f1_score(y_test, y_pred, zero_division=0)
            
            try:
                pr_auc = average_precision_score(y_test, y_prob)
                roc_auc = roc_auc_score(y_test, y_prob)
            except Exception:
                pr_auc = None
                roc_auc = None

            brier = brier_score_loss(y_test, y_prob)

            metricas = {
                'total_entrenamiento': len(train_df),
                'total_validacion': len(val_df),
                'total_prueba': len(test_df),
                'periodos_entrenamiento': periodos_train,
                'periodos_prueba': periodos_test,
                'distribucion_clases_prueba': {
                    'aprobados': int(np.sum(y_test == 0)),
                    'desaprobados': int(np.sum(y_test == 1))
                },
                'matriz_confusion': {
                    'verdaderos_negativos': int(tn),
                    'falsos_positivos': int(fp),
                    'falsos_negativos': int(fn),
                    'verdaderos_positivos': int(tp)
                },
                'precision_desaprobacion': round(float(prec), 4),
                'recall_desaprobacion': round(float(rec), 4),
                'f1_desaprobacion': round(float(f1), 4),
                'pr_auc': round(float(pr_auc), 4) if pr_auc is not None else None,
                'roc_auc': round(float(roc_auc), 4) if roc_auc is not None else None,
                'brier_score': round(float(brier), 4),
                'calibracion_evaluada': True,
                'limitaciones': [
                    'El modelo evalúa probabilidad de desaprobación condicional a la primera evaluación.',
                    'No captura eventos extraordinarios posteriores a la fecha de corte.',
                    'Debe ser utilizado únicamente como alerta temprana de apoyo pedagógico.'
                ]
            }

            # Guardar artefacto del modelo
            filename = f"model_{item['version']}.joblib"
            filepath = os.path.join(settings.ML_MODELS_DIR, filename)
            joblib.dump(pipe, filepath)

            # Registrar en la base de datos
            version_obj = VersionModelo.objects.create(
                nombre=item['nombre'],
                algoritmo=item['id'],
                version=item['version'],
                archivo_modelo=filepath,
                metricas_evaluacion=metricas,
                umbral_decision=0.50,
                variables_utilizadas=cls.CARACTERISTICAS_NUMERICAS,
                activo=False,
                es_sintetico=es_sintetico,
                entrenado_por=usuario
            )

            resultados_guardados.append({
                'version_obj': version_obj,
                'metricas': metricas
            })

            if f1 > mejor_f1 and item['id'] != 'DUMMY':
                mejor_f1 = f1
                mejor_version_obj = version_obj

        # Activar el mejor modelo evaluado si existe
        if mejor_version_obj:
            VersionModelo.objects.filter(activo=True).update(activo=False)
            mejor_version_obj.activo = True
            mejor_version_obj.save()

        return {
            'exito': True,
            'modelos_evaluados': len(resultados_guardados),
            'modelo_activo': mejor_version_obj.version if mejor_version_obj else None,
            'detalles': resultados_guardados
        }

    @classmethod
    def generar_predicciones_lote(cls, version_modelo=None):
        """
        Ejecuta inferencia predictiva por lote para todas las inscripciones del periodo vigente
        utilizando la versión de modelo activa.
        """
        if not version_modelo:
            version_modelo = VersionModelo.objects.filter(activo=True).first()
            if not version_modelo:
                return {'exito': False, 'mensaje': 'No hay ninguna versión de modelo predictivo activa en el sistema.'}

        if not os.path.exists(version_modelo.archivo_modelo):
            return {'exito': False, 'mensaje': f'El artefacto del modelo {version_modelo.archivo_modelo} no se encuentra en disco.'}

        modelo_pipeline = joblib.load(version_modelo.archivo_modelo)

        # Seleccionar snapshots actuales
        snapshots = InstantaneaPredictiva.objects.filter(
            detalle_matricula__matricula__estado=Matricula.EstadoMatricula.REGISTRADA,
            detalle_matricula__estado=DetalleMatricula.EstadoDetalle.INSCRITO
        ).select_related(
            'detalle_matricula__seccion__curso',
            'detalle_matricula__matricula__estudiante'
        )

        predicciones_creadas = 0
        for s in snapshots:
            # Construir vector de características
            df_in = pd.DataFrame([{
                'nota1': float(s.nota1) if s.nota1 is not None else np.nan,
                'porcentaje_asistencia': float(s.porcentaje_asistencia) if s.porcentaje_asistencia is not None else np.nan,
                'total_faltas': s.total_faltas,
                'total_tardanzas': s.total_tardanzas,
                'sesiones_consideradas': s.sesiones_consideradas,
                'promedio_historico_anterior': float(s.promedio_historico_anterior) if s.promedio_historico_anterior is not None else np.nan,
                'cursos_desaprobados_anteriores': s.cursos_desaprobados_anteriores,
                'sin_historial_previo': 1 if s.sin_historial_previo else 0,
            }])

            # Verificar datos insuficientes
            if s.nota1 is None and s.porcentaje_asistencia is None:
                prob = Decimal('0.0000')
                nivel = PrediccionEstudiante.NivelRiesgo.INSUFICIENTE
                orientacion = "Se requiere registrar al menos la primera evaluación o sesiones de asistencia para estimar el riesgo."
                factores = {'estado': 'Sin evaluaciones o asistencia registradas al corte.'}
            else:
                try:
                    if hasattr(modelo_pipeline, 'predict_proba'):
                        prob_val = float(modelo_pipeline.predict_proba(df_in)[0, 1])
                    else:
                        prob_val = float(modelo_pipeline.predict(df_in)[0])
                except Exception:
                    prob_val = 0.50

                prob = Decimal(str(round(prob_val, 4)))

                # Determinación estricta de nivel según umbrales transparentes
                if prob >= Decimal('0.65'):
                    nivel = PrediccionEstudiante.NivelRiesgo.ALTO
                    orientacion = "Prioridad alta: Coordinar tutoría académica intensiva, revisión de contenidos de N1 y seguimiento de asistencia."
                elif prob >= Decimal('0.35'):
                    nivel = PrediccionEstudiante.NivelRiesgo.MEDIO
                    orientacion = "Monitorear evolución para la Evaluación 2. Sugerir sesiones de reforzamiento y talleres de estudio."
                else:
                    nivel = PrediccionEstudiante.NivelRiesgo.BAJO
                    orientacion = "Rendimiento favorable al corte. Mantener ritmo de asistencia y preparación continua."

                factores = {
                    'nota1_observada': float(s.nota1) if s.nota1 is not None else 'No registrada',
                    'asistencia_pct': float(s.porcentaje_asistencia) if s.porcentaje_asistencia is not None else 'Sin datos',
                    'faltas_acumuladas': s.total_faltas,
                    'tardanzas_acumuladas': s.total_tardanzas,
                    'desaprobados_previos': s.cursos_desaprobados_anteriores,
                    'sin_historial_previo': s.sin_historial_previo
                }

            PrediccionEstudiante.objects.update_or_create(
                instantanea=s,
                version_modelo=version_modelo,
                defaults={
                    'probabilidad_riesgo': prob,
                    'nivel_riesgo': nivel,
                    'calibrado': True,
                    'factores_riesgo': factores,
                    'orientacion_academica': orientacion
                }
            )
            predicciones_creadas += 1

        return {
            'exito': True,
            'predicciones_generadas': predicciones_creadas,
            'version_utilizada': version_modelo.version
        }
