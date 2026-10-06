# Sistema Web de Gestión Académica Universitaria con Análisis de Datos y Predicción de Riesgo Académico

Desarrollado en **Python** y **Django 5.2 LTS** para el seguimiento integral de estudiantes, docentes, matrículas, asistencia, calificaciones vigesimales, analítica institucional con **Plotly & Pandas**, y un modelo predictivo evaluado con **Scikit-Learn** para la alerta temprana de desaprobación académica.

---

## 1. Arquitectura del Sistema

El sistema implementa una arquitectura modular con separación de responsabilidades:

```
sysuniversidad/
├── core/                   # Configuración global, settings, WSGI, URLs raíz
├── cuentas/                # Usuario personalizado (AbstractUser), roles, auditoría, auth
├── academico/              # Carreras, Cursos, Periodos, Docentes, Estudiantes, Secciones
├── matriculas/             # Matrículas, DetalleMatricula, transacciones atómicas, control de vacantes
├── asistencia/             # Sesiones de clase, toma de asistencia matriz, reglas de cálculo
├── calificaciones/         # Evaluaciones N1, N2, N3, promedio Decimal ROUND_HALF_UP, historial
├── analitica/              # Estadísticas descriptivas, gráficos interactivos Plotly, alertas normativas
├── predicciones/           # Instantáneas al corte, Pipeline ML cronológico, calibración, inferencia
├── reportes/               # Exportación de actas y sábanas en PDF (ReportLab) y Excel (openpyxl)
├── static/                 # CSS Anti-AI, JS, Bootstrap 5 y Plotly locales (100% offline)
├── templates/              # Plantillas HTML modulares por aplicación y rol
├── requirements.txt        # Dependencias de Python
└── manage.py
```

---

## 2. Reglas de Negocio Académicas

### Calificaciones
* **Escala:** Vigesimal de `0.00` a `20.00`.
* **Cálculo:** Promedio aritmético exacto con `Decimal` y redondeo simétrico a 2 decimales (`ROUND_HALF_UP`).
* **Aprobación:** Promedio final $\ge 13.00$.
* **Validez:** Solo se genera promedio si las tres notas están presentes. Una nota vacía significa pendiente; `0.00` es una nota válida.

### Control de Asistencia
* **Estados:** Presente (`P`), Tardanza (`T`), Falta (`F`), Justificada (`J`).
* **Fórmula:**
  $$\text{Porcentaje} = \frac{\text{Presentes} + \text{Tardanzas}}{\text{Total Sesiones Válidas} - \text{Justificadas}} \times 100$$
* **Regla:** Justificaciones se excluyen del denominador. Solo sesiones cerradas dentro del periodo cuentan en el historial.

### Matrículas y Vacantes
* Control estricto de concurrencia y sobrecupos con bloqueos pesimistas (`select_for_update`) bajo transacciones atómicas.
* Bloqueo de duplicados (imposible inscribir dos secciones del mismo curso en el mismo periodo).
* Anulación con motivo formal auditado, liberando la vacante inmediatamente.

---

## 3. Modelo Predictivo de Riesgo (Machine Learning)

* **Objetivo:** Estimar la probabilidad de desaprobar un curso ($\text{Promedio Final} < 13.00$) utilizando únicamente datos conocidos al corte de la primera evaluación (después de N1 y antes de N2).
* **Fuga de Datos (Zero Data Leakage):** Se prohíbe el uso de N2, N3, promedio final, notas futuras o identificadores personales (DNI, nombres).
* **Instantánea Inmutable (`InstantaneaPredictiva`):** Foto inmutable de lo conocido al corte (Nota 1, % asistencia al corte, faltas, tardanzas, promedio de periodos cerrados previos, desaprobados previos, indicador de estudiante nuevo).
* **Algoritmos Evaluados:**
  1. `DummyClassifier` (Línea base).
  2. `LogisticRegression` (Regresión logística estándar y calibrada).
  3. `DecisionTreeClassifier` (Árbol con profundidad máxima controlada).
* **Evaluación Cronológica:** Partición estricta por semestres (Periodos 2024-1 y 2024-2 en entrenamiento, 2025-1 en prueba cronológica).

---

## 4. Requisitos de Instalación en Windows

### A. Requisitos Previos
* **Python 3.12 (64-bit)**
* **MariaDB / MySQL** o **SQLite** (incluido por defecto para desarrollo ágil y presentaciones offline).

> [!NOTE]
> **Compatibilidad MariaDB / XAMPP**:
> Django 5.2 requiere MariaDB 10.5+. La versión estándar de XAMPP incluye MariaDB 10.4.32.
> Para utilizar MariaDB 10.5+ independiente sin alterar bases existentes de XAMPP:
> 1. Instalar MariaDB Community Server 11.x en el puerto `3307`.
> 2. Configurar en `.env`:
>    ```ini
>    DB_ENGINE=mysql
>    DB_NAME=sysuniversidad_db
>    DB_USER=root
>    DB_PASSWORD=tu_password
>    DB_HOST=127.0.0.1
>    DB_PORT=3307
>    ```
> Si se desea ejecutar de inmediato sin configurar un servidor MySQL externo, dejar `DB_ENGINE=sqlite` en el archivo `.env`.

### B. Pasos de Instalación
1. Clonar o ingresar al directorio del proyecto:
   ```powershell
   cd c:\xampp\htdocs\sysuniversidad
   ```
2. Crear y activar el entorno virtual con Python 3.12:
   ```powershell
   py -3.12 -m venv venv
   .\venv\Scripts\activate
   ```
3. Instalar dependencias:
   ```powershell
   pip install -r requirements.txt
   ```
4. Aplicar migraciones:
   ```powershell
   python manage.py migrate
   ```
5. Inicializar roles y poblar el sistema con datos multi-periodo y modelos entrenados:
   ```powershell
   python manage.py setup_roles
   python manage.py poblar_sistema
   ```
6. Iniciar el servidor local de Django:
   ```powershell
   python manage.py runserver
   ```
7. Abrir en el navegador: [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 5. Credenciales de Demostración

| Rol | Usuario | Contraseña | Descripción |
|---|---|---|---|
| **Administrador** | `admin` | `admin123` | Control total, gestión de modelos ML, usuarios y reportes |
| **Docente** | `docente1` | `admin123` | Gestión de notas, asistencia y alertas de sus secciones |
| **Docente** | `docente2` | `admin123` | Gestión de secciones asignadas |
| **Estudiante** | `estudiante1` | `admin123` | Portal de notas, asistencia y evolución académica |
| **Estudiante** | `estudiante2` | `admin123` | Portal del estudiante |

---

## 6. Comandos de Gestión Disponibles

* `python manage.py setup_roles`: Crea grupos de permisos y usuario administrador.
* `python manage.py poblar_sistema`: Genera todo el ecosistema académico sintético y entrena modelos.
* `python manage.py generar_instantaneas`: Construye los snapshots al corte predictivo.
* `python manage.py entrenar_modelo`: Ejecuta el Pipeline ML reproducible y evalúa modelos.
* `python manage.py evaluar_modelo`: Muestra el reporte JSON de métricas y calibración del modelo activo.
* `python manage.py predecir_riesgo`: Ejecuta inferencia por lote sobre estudiantes activos.
* `python manage.py test`: Ejecuta la suite de pruebas unitarias automatizadas.
