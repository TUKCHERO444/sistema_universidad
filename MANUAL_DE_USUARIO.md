# MANUAL DE USUARIO DEL SISTEMA DE GESTIÓN ACADÉMICA Y PREDICCIÓN DE RIESGO

## 1. INTRODUCCIÓN

El presente manual describe el funcionamiento operativo de la plataforma universitaria, detallando los flujos de trabajo, permisos y pantallas disponibles para cada uno de los tres roles del sistema:

* **Administrador:** Gestión integral de programas, asignaturas, periodos, secciones, matrículas, auditoría, entrenamiento y evaluación de modelos de Machine Learning y emisión de reportes generales.
* **Docente:** Registro de asistencia diaria, ingreso de notas en planilla vigesimal, revisión de alertas normativas y seguimiento confidencial de riesgo de sus secciones.
* **Estudiante:** Consulta de matrícula activa, revisión de asistencias por clase, boleta de calificaciones, gráfico de evolución del promedio ponderado y descarga de constancias en PDF.

---

## 2. ACCESO AL SISTEMA Y CREDENCIALES

Para ingresar a la plataforma:
1. Abra el navegador web e ingrese a la dirección: `http://127.0.0.1:8000/cuentas/login/`
2. Ingrese su nombre de usuario o correo institucional y su contraseña.
3. Presione el botón "Ingresar al Sistema".

### Credenciales de Demostración Configuradas:

| Rol | Usuario | Contraseña | Perfil y Alcance |
|---|---|---|---|
| Administrador | `admin` | `admin123` | Control total del sistema y configuración de ML |
| Docente | `docente1` | `admin123` | Docente de Ingeniería de Sistemas (CS-101, etc.) |
| Docente | `docente2` | `admin123` | Docente de Ingeniería de Software |
| Docente | `docente3` | `admin123` | Docente de Medicina Humana |
| Estudiante | `estudiante1` | `admin123` | Estudiante de Ingeniería de Sistemas |
| Estudiante | `estudiante2` | `admin123` | Estudiante de Medicina Humana |

> **Seguridad de Acceso:** El sistema cuenta con limitación de intentos fallidos. Si se introducen credenciales erróneas en 5 oportunidades consecutivas, la cuenta será bloqueada temporalmente por 15 minutos con registro en la bitácora de auditoría.

---

## 3. MANUAL DEL ADMINISTRADOR

El Administrador cuenta con acceso a todos los módulos y herramientas técnicas del sistema mediante el menú lateral izquierdo.

### 3.1 Panel Institucional (Dashboard)
* **Indicadores Globales:** Muestra el total de estudiantes activos, matrículas del periodo vigente, cuerpo docente y catálogo de asignaturas.
* **Alertas de Mayor Riesgo (ML):** Cuadro de alerta temprana con los estudiantes que presentan probabilidad alta de desaprobar según el modelo predictivo activo.
* **Últimas Matrículas:** Registro de las operaciones de matrícula más recientes.

### 3.2 Gestión Académica

#### A. Carreras Profesionales
* **Ruta:** Menú lateral -> Académico -> Carreras
* **Acciones:**
  * Visualizar programas académicos y cantidad de cursos y estudiantes vinculados.
  * Presionar "+ Nueva Carrera" para registrar código, nombre y descripción.
  * Editar o desactivar carreras existentes sin alterar el historial.

#### B. Catálogo de Cursos
* **Ruta:** Menú lateral -> Académico -> Cursos
* **Acciones:**
  * Filtrar asignaturas por carrera o término de búsqueda.
  * Presionar "+ Nuevo Curso" para registrar código de curso (ej. CS-101), nombre, carrera, ciclo (1 al 12) y valor en créditos (1 al 10).

#### C. Periodos Académicos
* **Ruta:** Menú lateral -> Académico -> Periodos
* **Acciones:**
  * Crear semestres académicos especificando código (ej. 2025-1), fechas de inicio y fin de clases, e intervalo de fechas de matrícula permitidas.
  * Marcar el periodo como "Vigente Principal" o cerrarlo cuando concluya el semestre.
  * **Regla:** En periodos con estado `CERRADO`, el sistema bloquea cualquier modificación de matrículas, asistencias o notas.

#### D. Plana Docente y Padrón de Estudiantes
* **Ruta:** Menú lateral -> Académico -> Docentes / Estudiantes
* **Acciones:**
  * Registrar nuevos docentes o estudiantes con DNI (8 dígitos), nombres, apellidos, correo institucional y carrera.
  * Al guardar un nuevo registro, el sistema genera de forma automática la cuenta de usuario correspondiente para que el usuario pueda iniciar sesión.

#### E. Programación de Secciones
* **Ruta:** Menú lateral -> Académico -> Secciones
* **Acciones:**
  * Programar grupos de clase asociando el curso, periodo, docente asignado, código de sección (01, A, etc.) y capacidad máxima de vacantes.
  * Definir la **Fecha de Corte Predictivo**, la cual debe ubicarse después de la primera evaluación y antes de la segunda, para la generación inmutable del snapshot de Machine Learning.

### 3.3 Gestión de Matrículas
* **Ruta:** Menú lateral -> Operaciones -> Matrículas
* **Proceso de Registro de Nueva Matrícula:**
  1. Presione "+ Nueva Matrícula".
  2. Seleccione el estudiante activo y el periodo académico abierto.
  3. Presione "Cargar Asignaturas". El sistema mostrará las secciones disponibles para la carrera del estudiante.
  4. Marque las casillas de las secciones deseadas. El sistema calculará en tiempo real el total de créditos seleccionados y verificará la disponibilidad de vacantes.
  5. Presione "Confirmar y Procesar Matrícula". La operación se ejecutará bajo transacción atómica con reserva segura de vacantes.
* **Anulación de Matrícula:**
  * En la vista de detalle de la matrícula, presione "Anular Matrícula".
  * Ingrese el motivo formal obligatorio (ej. Retiro de semestre, cambio de sede).
  * Al confirmar, las vacantes ocupadas quedarán liberadas de inmediato para otros alumnos y el evento quedará registrado en la bitácora de auditoría.

### 3.4 Inteligencia Predictiva (Machine Learning)
* **Ruta:** Menú lateral -> Inteligencia & Analítica -> Predicciones ML
* **Acciones Disponibles:**
  1. **Ejecutar Pipeline ML (Train/Eval):** Ejecuta la extracción de instantáneas al corte, división cronológica de conjuntos (entrenamiento en periodos anteriores y prueba en periodos posteriores), comparación de algoritmos (`DummyClassifier`, `LogisticRegression` y `DecisionTreeClassifier`) y selección del mejor modelo con métricas de Recall y F1.
  2. **Recalcular Inferencia Lote:** Ejecuta el modelo activo sobre todas las inscripciones del periodo vigente, estimando probabilidades de riesgo y clasificándolas en Bajo, Medio o Alto.
  3. **Activar Modelo:** Permite al administrador seleccionar qué versión evaluada gobernará las inferencias institucionales.
  4. **Factores & Guía:** Muestra la descomposición detallada de variables observadas al corte (Nota 1, porcentaje de asistencia, faltas, historial previo) y recomendaciones pedagógicas.

### 3.5 Bitácora de Auditoría
* **Ruta:** Menú lateral -> Administración -> Auditoría
* **Funcionalidad:** Monitoreo inmutable de todas las acciones sensibles realizadas en la plataforma (creación de usuarios, registro y anulación de matrículas, modificaciones de notas y descargas de reportes), incluyendo fecha, hora, usuario responsable y dirección IP.

---

## 4. MANUAL DEL DOCENTE

El Docente dispone de un entorno optimizado para gestionar sus grupos asignados y realizar el seguimiento pedagógico de sus alumnos.

### 4.1 Panel del Docente
* Muestra el resumen de secciones a su cargo en el periodo actual, el total de alumnos matriculados y las alertas de riesgo detectadas por el modelo predictivo.

### 4.2 Registro de Asistencia
* **Ruta:** Menú lateral -> Docencia -> Asistencia
* **Flujo de Trabajo:**
  1. Seleccione la sección deseada y presione "Toma de Asistencia".
  2. Para aperturar una nueva clase, ingrese la fecha, hora de inicio, hora de fin y el tema tratado, y presione "Crear y Abrir Registro de Asistencia".
  3. En la matriz de alumnos, asigne para cada estudiante una de las cuatro opciones:
     * **P (Presente):** Cuenta como asistencia.
     * **T (Tardanza):** Cuenta como asistencia.
     * **F (Falta):** Cuenta como inasistencia (ausencia).
     * **J (Justificada):** Se excluye del denominador para no perjudicar injustamente el porcentaje del alumno.
  4. Puede utilizar el botón "Marcar Todos Presentes" para agilizar el registro y luego modificar las excepciones.
  5. Presione "Guardar y Validar Asistencia". Cuando todos los alumnos tengan estado asignado, la sesión se marcará como cerrada y se consolidará en el récord oficial.

### 4.3 Planilla de Calificaciones
* **Ruta:** Menú lateral -> Docencia -> Calificaciones
* **Flujo de Trabajo:**
  1. Ingrese a la sección deseada para abrir el Acta de Calificaciones.
  2. Ingrese las calificaciones obtenidas en la escala vigesimal (0.00 a 20.00):
     * **Eval 1 (N1):** Primera evaluación parcial.
     * **Eval 2 (N2):** Segunda evaluación parcial.
     * **Eval 3 (N3):** Evaluación final / continua.
  3. A medida que digita las notas, la interfaz calcula en tiempo real el promedio aritmético exacto y muestra la condición proyectada:
     * Si el promedio es $\ge 13.00 \Rightarrow$ `Aprobado` (verde).
     * Si el promedio es $< 13.00 \Rightarrow$ `Desaprobado` (rojo).
     * Si falta alguna nota $\Rightarrow$ `Pendiente` (gris).
  4. Ingrese el motivo del registro o cambio (ej. "Ingreso de Evaluación 1") y presione "Guardar Calificaciones".
  5. El servidor aplicará el redondeo oficial `ROUND_HALF_UP` a 2 decimales y registrará la trazabilidad del cambio.

### 4.4 Alertas de Rendimiento y Riesgo ML
* **Ruta:** Menú lateral -> Docencia -> Alertas Académicas / Riesgo Académico (ML)
* **Diferenciación:**
  * **Alertas Normativas:** Señalizaciones deterministas cuando un alumno tiene menos del 70% de asistencia o menos de 10.50 en la primera nota.
  * **Predicción de Riesgo ML:** Estimación estadística que combina notas, asistencia y trayectoria previa para alertar sobre posible desaprobación antes de la segunda evaluación. Incluye orientaciones de tutoría y refuerzo académico sugeridas.

### 4.5 Emisión de Actas Oficiales
* **Ruta:** Menú lateral -> Docencia -> Reportes
* **Formatos:**
  * **Descargar PDF:** Genera el acta formal de evaluación con encabezado institucional, firma y padrón.
  * **Descargar Excel:** Exporta la sábana de notas en formato XLSX protegida contra inyección de fórmulas.

---

## 5. MANUAL DEL ESTUDIANTE

El Estudiante cuenta con un portal de autoservicio informativo, de consulta y descarga de constancias.

### 5.1 Portal del Estudiante (Inicio)
* Presenta la ficha de la matrícula vigente en el periodo actual, el total de créditos inscritos y la tabla de asignaturas con sus docentes, notas registradas (N1, N2, N3), promedio final y estado académico.

### 5.2 Mis Asignaturas y Mis Matrículas
* **Ruta:** Menú lateral -> Portal del Estudiante -> Mis Cursos / Mis Matrículas
* Permite revisar el historial de todas las matrículas realizadas en la universidad y el detalle de asignaturas por ciclo.

### 5.3 Control de Asistencia Personal
* **Ruta:** Menú lateral -> Portal del Estudiante -> Mi Asistencia
* **Información Visualizada:**
  * Porcentaje consolidado de asistencia por cada curso.
  * Desglose exacto de sesiones realizadas, asistencias presentes, tardanzas, inasistencias y faltas justificadas.
  * Cronograma de clases con fecha, horario y tema tratado en cada sesión.

### 5.4 Boleta Oficial de Calificaciones
* **Ruta:** Menú lateral -> Portal del Estudiante -> Mis Calificaciones
* Permite seleccionar el periodo académico que se desea consultar y visualizar el récord de notas.
* **Descarga de Boleta PDF:** Al presionar el botón "Descargar Boleta PDF", se genera el documento oficial con las notas obtenidas en el semestre seleccionado.

### 5.5 Evolución Académica
* **Ruta:** Menú lateral -> Portal del Estudiante -> Mi Evolución
* Muestra el gráfico interactivo de trayectoria académica, visualizando el promedio ponderado obtenido a lo largo de los semestres consecutivos y su posición respecto a la línea de aprobación institucional (13.00).

---

## 6. PREGUNTAS FRECUENTES Y REGLAS CLAVE

1. **¿Qué ocurre si un alumno no tiene una nota ingresada?**
   El sistema no calcula un promedio provisional con notas incompletas; el promedio permanece en estado `Pendiente`. La nota `0.00` es una calificación válida y sí computa en el promedio.

2. **¿Cómo se calculan las justificaciones de asistencia?**
   Las faltas justificadas (`J`) se restan del total de sesiones consideradas en el denominador. Por ejemplo, si un curso tuvo 10 clases y el alumno tiene 1 falta justificada, el porcentaje se calculará sobre 9 sesiones válidas.

3. **¿Puede un alumno matricularse en dos secciones del mismo curso?**
   No. El sistema valida la no duplicidad de asignaturas por periodo y rechaza la operación antes de guardar.

4. **¿Las predicciones de Machine Learning alteran las calificaciones de los alumnos?**
   No. Las predicciones son de carácter estrictamente informativo y pedagógico para docentes y administradores, con el fin de brindar apoyo oportuno antes del examen final. No modifican registros académicos ni generan sanciones.
