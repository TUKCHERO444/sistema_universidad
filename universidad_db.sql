-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 29-09-2026 a las 16:06:29
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `universidad_db`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `asistencias`
--

CREATE TABLE `asistencias` (
  `id_asistencia` int(11) NOT NULL,
  `id_sesion` int(11) NOT NULL,
  `id_estudiante` int(11) NOT NULL,
  `estado` enum('PRESENTE','TARDANZA','FALTA','JUSTIFICADA') NOT NULL,
  `observacion` varchar(250) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `auditoria`
--

CREATE TABLE `auditoria` (
  `id_auditoria` bigint(20) NOT NULL,
  `id_usuario` int(11) DEFAULT NULL,
  `tabla_afectada` varchar(100) NOT NULL,
  `id_registro` varchar(100) DEFAULT NULL,
  `accion` enum('INSERT','UPDATE','DELETE','LOGIN','LOGOUT') NOT NULL,
  `descripcion` text DEFAULT NULL,
  `ip` varchar(45) DEFAULT NULL,
  `fecha` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `aulas`
--

CREATE TABLE `aulas` (
  `id_aula` int(11) NOT NULL,
  `codigo` varchar(20) NOT NULL,
  `nombre` varchar(100) DEFAULT NULL,
  `pabellon` varchar(100) DEFAULT NULL,
  `piso` tinyint(4) DEFAULT NULL,
  `capacidad` smallint(5) UNSIGNED NOT NULL,
  `tipo` enum('AULA','LABORATORIO','TALLER','AUDITORIO') NOT NULL DEFAULT 'AULA',
  `estado` tinyint(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `calendario_academico`
--

CREATE TABLE `calendario_academico` (
  `id_evento` int(11) NOT NULL,
  `id_periodo` int(11) NOT NULL,
  `nombre` varchar(150) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `fecha_inicio` datetime NOT NULL,
  `fecha_fin` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `carreras`
--

CREATE TABLE `carreras` (
  `id_carrera` int(11) NOT NULL,
  `id_facultad` int(11) NOT NULL,
  `codigo` varchar(20) NOT NULL,
  `nombre` varchar(150) NOT NULL,
  `duracion_ciclos` tinyint(3) UNSIGNED NOT NULL DEFAULT 10,
  `grado_academico` varchar(100) DEFAULT NULL,
  `titulo_profesional` varchar(150) DEFAULT NULL,
  `estado` tinyint(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `comprobantes`
--

CREATE TABLE `comprobantes` (
  `id_comprobante` int(11) NOT NULL,
  `id_pago` int(11) NOT NULL,
  `tipo` enum('BOLETA','FACTURA','RECIBO') NOT NULL,
  `serie` varchar(10) DEFAULT NULL,
  `numero` varchar(20) DEFAULT NULL,
  `fecha_emision` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `conceptos_pago`
--

CREATE TABLE `conceptos_pago` (
  `id_concepto` int(11) NOT NULL,
  `codigo` varchar(20) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `estado` tinyint(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `cuentas_cobrar`
--

CREATE TABLE `cuentas_cobrar` (
  `id_cuenta` int(11) NOT NULL,
  `id_estudiante` int(11) NOT NULL,
  `id_periodo` int(11) DEFAULT NULL,
  `id_concepto` int(11) NOT NULL,
  `monto` decimal(10,2) NOT NULL,
  `descuento` decimal(10,2) NOT NULL DEFAULT 0.00,
  `fecha_emision` date NOT NULL,
  `fecha_vencimiento` date DEFAULT NULL,
  `estado` enum('PENDIENTE','PARCIAL','PAGADO','ANULADO') NOT NULL DEFAULT 'PENDIENTE'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `cursos`
--

CREATE TABLE `cursos` (
  `id_curso` int(11) NOT NULL,
  `codigo` varchar(20) NOT NULL,
  `nombre` varchar(150) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `horas_teoria` tinyint(3) UNSIGNED DEFAULT 0,
  `horas_practica` tinyint(3) UNSIGNED DEFAULT 0,
  `estado` tinyint(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `detalle_matriculas`
--

CREATE TABLE `detalle_matriculas` (
  `id_detalle_matricula` int(11) NOT NULL,
  `id_matricula` int(11) NOT NULL,
  `id_seccion` int(11) NOT NULL,
  `fecha_registro` datetime DEFAULT current_timestamp(),
  `estado` enum('MATRICULADO','RETIRADO','APROBADO','DESAPROBADO') NOT NULL DEFAULT 'MATRICULADO'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `docentes`
--

CREATE TABLE `docentes` (
  `id_docente` int(11) NOT NULL,
  `id_persona` int(11) NOT NULL,
  `codigo_docente` varchar(20) NOT NULL,
  `fecha_ingreso` date DEFAULT NULL,
  `estado` enum('ACTIVO','INACTIVO') NOT NULL DEFAULT 'ACTIVO'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `docente_especialidades`
--

CREATE TABLE `docente_especialidades` (
  `id_docente` int(11) NOT NULL,
  `id_especialidad` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `egresos`
--

CREATE TABLE `egresos` (
  `id_egreso` int(11) NOT NULL,
  `id_estudiante` int(11) NOT NULL,
  `fecha_egreso` date NOT NULL,
  `creditos_aprobados` smallint(5) UNSIGNED DEFAULT NULL,
  `promedio_general` decimal(5,2) DEFAULT NULL,
  `observacion` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `especialidades`
--

CREATE TABLE `especialidades` (
  `id_especialidad` int(11) NOT NULL,
  `nombre` varchar(150) NOT NULL,
  `descripcion` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `estudiantes`
--

CREATE TABLE `estudiantes` (
  `id_estudiante` int(11) NOT NULL,
  `id_persona` int(11) NOT NULL,
  `codigo_estudiante` varchar(20) NOT NULL,
  `fecha_ingreso` date NOT NULL,
  `estado` enum('ACTIVO','INACTIVO','RESERVA','SUSPENDIDO','EGRESADO','RETIRADO') NOT NULL DEFAULT 'ACTIVO'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `estudiante_carreras`
--

CREATE TABLE `estudiante_carreras` (
  `id_estudiante_carrera` int(11) NOT NULL,
  `id_estudiante` int(11) NOT NULL,
  `id_carrera` int(11) NOT NULL,
  `id_plan` int(11) NOT NULL,
  `fecha_inicio` date NOT NULL,
  `fecha_fin` date DEFAULT NULL,
  `estado` enum('ACTIVA','FINALIZADA','CAMBIO','RETIRADA') NOT NULL DEFAULT 'ACTIVA'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `evaluaciones`
--

CREATE TABLE `evaluaciones` (
  `id_evaluacion` int(11) NOT NULL,
  `id_seccion` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `tipo` enum('PRACTICA','EXAMEN','TAREA','PROYECTO','PARTICIPACION','OTRO') NOT NULL,
  `porcentaje` decimal(5,2) NOT NULL,
  `fecha` date DEFAULT NULL,
  `nota_maxima` decimal(5,2) NOT NULL DEFAULT 20.00
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `evaluaciones_admision`
--

CREATE TABLE `evaluaciones_admision` (
  `id_evaluacion_admision` int(11) NOT NULL,
  `id_postulacion` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `fecha` datetime DEFAULT NULL,
  `puntaje` decimal(7,2) DEFAULT NULL,
  `puntaje_maximo` decimal(7,2) DEFAULT NULL,
  `observacion` varchar(250) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `facultades`
--

CREATE TABLE `facultades` (
  `id_facultad` int(11) NOT NULL,
  `codigo` varchar(20) NOT NULL,
  `nombre` varchar(150) NOT NULL,
  `estado` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `grados_academicos`
--

CREATE TABLE `grados_academicos` (
  `id_grado` int(11) NOT NULL,
  `id_egreso` int(11) NOT NULL,
  `tipo` enum('BACHILLER','MAESTRO','DOCTOR') NOT NULL,
  `nombre` varchar(200) NOT NULL,
  `fecha_otorgamiento` date DEFAULT NULL,
  `numero_registro` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `horarios`
--

CREATE TABLE `horarios` (
  `id_horario` int(11) NOT NULL,
  `id_seccion` int(11) NOT NULL,
  `id_aula` int(11) DEFAULT NULL,
  `dia_semana` enum('LUNES','MARTES','MIERCOLES','JUEVES','VIERNES','SABADO','DOMINGO') NOT NULL,
  `hora_inicio` time NOT NULL,
  `hora_fin` time NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `matriculas`
--

CREATE TABLE `matriculas` (
  `id_matricula` int(11) NOT NULL,
  `id_estudiante` int(11) NOT NULL,
  `id_periodo` int(11) NOT NULL,
  `fecha_matricula` datetime NOT NULL DEFAULT current_timestamp(),
  `total_creditos` smallint(5) UNSIGNED NOT NULL DEFAULT 0,
  `estado` enum('PENDIENTE','CONFIRMADA','ANULADA','RESERVADA') NOT NULL DEFAULT 'PENDIENTE'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `modalidades_ingreso`
--

CREATE TABLE `modalidades_ingreso` (
  `id_modalidad` int(11) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `estado` tinyint(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `notas`
--

CREATE TABLE `notas` (
  `id_nota` int(11) NOT NULL,
  `id_evaluacion` int(11) NOT NULL,
  `id_estudiante` int(11) NOT NULL,
  `nota` decimal(5,2) DEFAULT NULL,
  `observacion` varchar(250) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `pagos`
--

CREATE TABLE `pagos` (
  `id_pago` int(11) NOT NULL,
  `id_cuenta` int(11) NOT NULL,
  `monto` decimal(10,2) NOT NULL,
  `fecha_pago` datetime NOT NULL DEFAULT current_timestamp(),
  `metodo` enum('EFECTIVO','TARJETA','TRANSFERENCIA','BANCO','OTRO') NOT NULL,
  `numero_operacion` varchar(100) DEFAULT NULL,
  `estado` enum('REGISTRADO','ANULADO') NOT NULL DEFAULT 'REGISTRADO'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `periodos_academicos`
--

CREATE TABLE `periodos_academicos` (
  `id_periodo` int(11) NOT NULL,
  `codigo` varchar(20) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `year` year(4) NOT NULL,
  `numero_periodo` tinyint(3) UNSIGNED NOT NULL,
  `fecha_inicio` date NOT NULL,
  `fecha_fin` date NOT NULL,
  `fecha_inicio_matricula` date DEFAULT NULL,
  `fecha_fin_matricula` date DEFAULT NULL,
  `estado` enum('PLANIFICADO','MATRICULA','EN_CURSO','CERRADO') NOT NULL DEFAULT 'PLANIFICADO'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `permisos`
--

CREATE TABLE `permisos` (
  `id_permiso` int(11) NOT NULL,
  `codigo` varchar(100) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `descripcion` varchar(250) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `personas`
--

CREATE TABLE `personas` (
  `id_persona` int(11) NOT NULL,
  `tipo_documento` enum('DNI','CE','PASAPORTE','OTRO') NOT NULL,
  `numero_documento` varchar(20) NOT NULL,
  `nombres` varchar(100) NOT NULL,
  `apellido_paterno` varchar(70) NOT NULL,
  `apellido_materno` varchar(70) DEFAULT NULL,
  `fecha_nacimiento` date DEFAULT NULL,
  `sexo` enum('M','F','OTRO') DEFAULT NULL,
  `email` varchar(150) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `direccion` varchar(250) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `planes_estudio`
--

CREATE TABLE `planes_estudio` (
  `id_plan` int(11) NOT NULL,
  `id_carrera` int(11) NOT NULL,
  `codigo` varchar(30) NOT NULL,
  `nombre` varchar(150) NOT NULL,
  `year_inicio` year(4) NOT NULL,
  `total_creditos` smallint(5) UNSIGNED DEFAULT NULL,
  `estado` enum('VIGENTE','NO_VIGENTE') NOT NULL DEFAULT 'VIGENTE'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `plan_cursos`
--

CREATE TABLE `plan_cursos` (
  `id_plan_curso` int(11) NOT NULL,
  `id_plan` int(11) NOT NULL,
  `id_curso` int(11) NOT NULL,
  `ciclo` tinyint(3) UNSIGNED NOT NULL,
  `creditos` tinyint(3) UNSIGNED NOT NULL,
  `tipo` enum('OBLIGATORIO','ELECTIVO') NOT NULL DEFAULT 'OBLIGATORIO'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `postulaciones`
--

CREATE TABLE `postulaciones` (
  `id_postulacion` int(11) NOT NULL,
  `id_persona` int(11) NOT NULL,
  `id_proceso` int(11) NOT NULL,
  `id_carrera` int(11) NOT NULL,
  `id_modalidad` int(11) NOT NULL,
  `fecha_postulacion` datetime NOT NULL DEFAULT current_timestamp(),
  `estado` enum('REGISTRADA','EN_EVALUACION','ADMITIDA','NO_ADMITIDA','ANULADA') NOT NULL DEFAULT 'REGISTRADA'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `prerrequisitos`
--

CREATE TABLE `prerrequisitos` (
  `id_prerrequisito` int(11) NOT NULL,
  `id_plan_curso` int(11) NOT NULL,
  `id_curso_prerrequisito` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `procesos_admision`
--

CREATE TABLE `procesos_admision` (
  `id_proceso` int(11) NOT NULL,
  `nombre` varchar(150) NOT NULL,
  `year` year(4) NOT NULL,
  `periodo` varchar(30) DEFAULT NULL,
  `fecha_inicio` date NOT NULL,
  `fecha_fin` date NOT NULL,
  `estado` enum('PLANIFICADO','ABIERTO','CERRADO') NOT NULL DEFAULT 'PLANIFICADO'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `resultados_admision`
--

CREATE TABLE `resultados_admision` (
  `id_resultado` int(11) NOT NULL,
  `id_postulacion` int(11) NOT NULL,
  `puntaje_final` decimal(7,2) DEFAULT NULL,
  `resultado` enum('ADMITIDO','NO_ADMITIDO') NOT NULL,
  `fecha_resultado` datetime DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `resultados_finales`
--

CREATE TABLE `resultados_finales` (
  `id_resultado_final` int(11) NOT NULL,
  `id_detalle_matricula` int(11) NOT NULL,
  `promedio_final` decimal(5,2) DEFAULT NULL,
  `estado` enum('CURSANDO','APROBADO','DESAPROBADO','RETIRADO') NOT NULL DEFAULT 'CURSANDO',
  `fecha_cierre` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `roles`
--

CREATE TABLE `roles` (
  `id_rol` int(11) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `descripcion` varchar(250) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `rol_permisos`
--

CREATE TABLE `rol_permisos` (
  `id_rol` int(11) NOT NULL,
  `id_permiso` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `secciones`
--

CREATE TABLE `secciones` (
  `id_seccion` int(11) NOT NULL,
  `id_curso` int(11) NOT NULL,
  `id_periodo` int(11) NOT NULL,
  `codigo` varchar(20) NOT NULL,
  `capacidad` smallint(5) UNSIGNED NOT NULL,
  `estado` enum('ABIERTA','CERRADA','CANCELADA') NOT NULL DEFAULT 'ABIERTA'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `seccion_docentes`
--

CREATE TABLE `seccion_docentes` (
  `id_seccion` int(11) NOT NULL,
  `id_docente` int(11) NOT NULL,
  `tipo` enum('TITULAR','APOYO') NOT NULL DEFAULT 'TITULAR'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `seguimiento_tramites`
--

CREATE TABLE `seguimiento_tramites` (
  `id_seguimiento` int(11) NOT NULL,
  `id_solicitud` int(11) NOT NULL,
  `fecha` datetime NOT NULL DEFAULT current_timestamp(),
  `estado` varchar(50) NOT NULL,
  `observacion` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `sesiones_clase`
--

CREATE TABLE `sesiones_clase` (
  `id_sesion` int(11) NOT NULL,
  `id_seccion` int(11) NOT NULL,
  `fecha` date NOT NULL,
  `hora_inicio` time DEFAULT NULL,
  `hora_fin` time DEFAULT NULL,
  `tema` varchar(250) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `solicitudes_tramite`
--

CREATE TABLE `solicitudes_tramite` (
  `id_solicitud` int(11) NOT NULL,
  `id_estudiante` int(11) NOT NULL,
  `id_tipo_tramite` int(11) NOT NULL,
  `fecha_solicitud` datetime NOT NULL DEFAULT current_timestamp(),
  `motivo` text DEFAULT NULL,
  `estado` enum('PENDIENTE','EN_REVISION','APROBADA','RECHAZADA','CANCELADA') NOT NULL DEFAULT 'PENDIENTE'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `tipos_tramite`
--

CREATE TABLE `tipos_tramite` (
  `id_tipo_tramite` int(11) NOT NULL,
  `nombre` varchar(150) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `costo` decimal(10,2) NOT NULL DEFAULT 0.00,
  `estado` tinyint(1) NOT NULL DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `titulaciones`
--

CREATE TABLE `titulaciones` (
  `id_titulacion` int(11) NOT NULL,
  `id_egreso` int(11) NOT NULL,
  `titulo` varchar(200) NOT NULL,
  `modalidad` varchar(100) DEFAULT NULL,
  `fecha_sustentacion` date DEFAULT NULL,
  `fecha_otorgamiento` date DEFAULT NULL,
  `numero_registro` varchar(100) DEFAULT NULL,
  `estado` enum('EN_PROCESO','APROBADO','OTORGADO') NOT NULL DEFAULT 'EN_PROCESO'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id_usuario` int(11) NOT NULL,
  `id_persona` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `estado` tinyint(1) NOT NULL DEFAULT 1,
  `ultimo_acceso` datetime DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuario_roles`
--

CREATE TABLE `usuario_roles` (
  `id_usuario` int(11) NOT NULL,
  `id_rol` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `asistencias`
--
ALTER TABLE `asistencias`
  ADD PRIMARY KEY (`id_asistencia`),
  ADD UNIQUE KEY `uk_asistencia_estudiante` (`id_sesion`,`id_estudiante`),
  ADD KEY `idx_asistencia_estudiante` (`id_estudiante`);

--
-- Indices de la tabla `auditoria`
--
ALTER TABLE `auditoria`
  ADD PRIMARY KEY (`id_auditoria`),
  ADD KEY `fk_auditoria_usuario` (`id_usuario`),
  ADD KEY `idx_auditoria_fecha` (`fecha`);

--
-- Indices de la tabla `aulas`
--
ALTER TABLE `aulas`
  ADD PRIMARY KEY (`id_aula`),
  ADD UNIQUE KEY `codigo` (`codigo`);

--
-- Indices de la tabla `calendario_academico`
--
ALTER TABLE `calendario_academico`
  ADD PRIMARY KEY (`id_evento`),
  ADD KEY `fk_calendario_periodo` (`id_periodo`);

--
-- Indices de la tabla `carreras`
--
ALTER TABLE `carreras`
  ADD PRIMARY KEY (`id_carrera`),
  ADD UNIQUE KEY `codigo` (`codigo`),
  ADD KEY `fk_carrera_facultad` (`id_facultad`);

--
-- Indices de la tabla `comprobantes`
--
ALTER TABLE `comprobantes`
  ADD PRIMARY KEY (`id_comprobante`),
  ADD UNIQUE KEY `id_pago` (`id_pago`);

--
-- Indices de la tabla `conceptos_pago`
--
ALTER TABLE `conceptos_pago`
  ADD PRIMARY KEY (`id_concepto`),
  ADD UNIQUE KEY `codigo` (`codigo`);

--
-- Indices de la tabla `cuentas_cobrar`
--
ALTER TABLE `cuentas_cobrar`
  ADD PRIMARY KEY (`id_cuenta`),
  ADD KEY `fk_cuenta_periodo` (`id_periodo`),
  ADD KEY `fk_cuenta_concepto` (`id_concepto`),
  ADD KEY `idx_cuenta_estudiante` (`id_estudiante`);

--
-- Indices de la tabla `cursos`
--
ALTER TABLE `cursos`
  ADD PRIMARY KEY (`id_curso`),
  ADD UNIQUE KEY `codigo` (`codigo`);

--
-- Indices de la tabla `detalle_matriculas`
--
ALTER TABLE `detalle_matriculas`
  ADD PRIMARY KEY (`id_detalle_matricula`),
  ADD UNIQUE KEY `uk_matricula_seccion` (`id_matricula`,`id_seccion`),
  ADD KEY `fk_dm_seccion` (`id_seccion`),
  ADD KEY `idx_detalle_matricula` (`id_matricula`);

--
-- Indices de la tabla `docentes`
--
ALTER TABLE `docentes`
  ADD PRIMARY KEY (`id_docente`),
  ADD UNIQUE KEY `id_persona` (`id_persona`),
  ADD UNIQUE KEY `codigo_docente` (`codigo_docente`);

--
-- Indices de la tabla `docente_especialidades`
--
ALTER TABLE `docente_especialidades`
  ADD PRIMARY KEY (`id_docente`,`id_especialidad`),
  ADD KEY `fk_de_especialidad` (`id_especialidad`);

--
-- Indices de la tabla `egresos`
--
ALTER TABLE `egresos`
  ADD PRIMARY KEY (`id_egreso`),
  ADD UNIQUE KEY `id_estudiante` (`id_estudiante`);

--
-- Indices de la tabla `especialidades`
--
ALTER TABLE `especialidades`
  ADD PRIMARY KEY (`id_especialidad`),
  ADD UNIQUE KEY `nombre` (`nombre`);

--
-- Indices de la tabla `estudiantes`
--
ALTER TABLE `estudiantes`
  ADD PRIMARY KEY (`id_estudiante`),
  ADD UNIQUE KEY `id_persona` (`id_persona`),
  ADD UNIQUE KEY `codigo_estudiante` (`codigo_estudiante`),
  ADD KEY `idx_estudiante_codigo` (`codigo_estudiante`);

--
-- Indices de la tabla `estudiante_carreras`
--
ALTER TABLE `estudiante_carreras`
  ADD PRIMARY KEY (`id_estudiante_carrera`),
  ADD KEY `fk_ec_estudiante` (`id_estudiante`),
  ADD KEY `fk_ec_carrera` (`id_carrera`),
  ADD KEY `fk_ec_plan` (`id_plan`);

--
-- Indices de la tabla `evaluaciones`
--
ALTER TABLE `evaluaciones`
  ADD PRIMARY KEY (`id_evaluacion`),
  ADD KEY `fk_evaluacion_seccion` (`id_seccion`);

--
-- Indices de la tabla `evaluaciones_admision`
--
ALTER TABLE `evaluaciones_admision`
  ADD PRIMARY KEY (`id_evaluacion_admision`),
  ADD KEY `fk_evaluacion_postulacion` (`id_postulacion`);

--
-- Indices de la tabla `facultades`
--
ALTER TABLE `facultades`
  ADD PRIMARY KEY (`id_facultad`),
  ADD UNIQUE KEY `codigo` (`codigo`);

--
-- Indices de la tabla `grados_academicos`
--
ALTER TABLE `grados_academicos`
  ADD PRIMARY KEY (`id_grado`),
  ADD KEY `fk_grado_egreso` (`id_egreso`);

--
-- Indices de la tabla `horarios`
--
ALTER TABLE `horarios`
  ADD PRIMARY KEY (`id_horario`),
  ADD KEY `fk_horario_seccion` (`id_seccion`),
  ADD KEY `fk_horario_aula` (`id_aula`);

--
-- Indices de la tabla `matriculas`
--
ALTER TABLE `matriculas`
  ADD PRIMARY KEY (`id_matricula`),
  ADD UNIQUE KEY `uk_estudiante_periodo` (`id_estudiante`,`id_periodo`),
  ADD KEY `fk_matricula_periodo` (`id_periodo`),
  ADD KEY `idx_matricula_estudiante` (`id_estudiante`);

--
-- Indices de la tabla `modalidades_ingreso`
--
ALTER TABLE `modalidades_ingreso`
  ADD PRIMARY KEY (`id_modalidad`),
  ADD UNIQUE KEY `nombre` (`nombre`);

--
-- Indices de la tabla `notas`
--
ALTER TABLE `notas`
  ADD PRIMARY KEY (`id_nota`),
  ADD UNIQUE KEY `uk_nota_estudiante` (`id_evaluacion`,`id_estudiante`),
  ADD KEY `idx_nota_estudiante` (`id_estudiante`);

--
-- Indices de la tabla `pagos`
--
ALTER TABLE `pagos`
  ADD PRIMARY KEY (`id_pago`),
  ADD KEY `fk_pago_cuenta` (`id_cuenta`),
  ADD KEY `idx_pago_fecha` (`fecha_pago`);

--
-- Indices de la tabla `periodos_academicos`
--
ALTER TABLE `periodos_academicos`
  ADD PRIMARY KEY (`id_periodo`),
  ADD UNIQUE KEY `codigo` (`codigo`);

--
-- Indices de la tabla `permisos`
--
ALTER TABLE `permisos`
  ADD PRIMARY KEY (`id_permiso`),
  ADD UNIQUE KEY `codigo` (`codigo`);

--
-- Indices de la tabla `personas`
--
ALTER TABLE `personas`
  ADD PRIMARY KEY (`id_persona`),
  ADD UNIQUE KEY `numero_documento` (`numero_documento`),
  ADD KEY `idx_persona_documento` (`numero_documento`);

--
-- Indices de la tabla `planes_estudio`
--
ALTER TABLE `planes_estudio`
  ADD PRIMARY KEY (`id_plan`),
  ADD UNIQUE KEY `codigo` (`codigo`),
  ADD KEY `fk_plan_carrera` (`id_carrera`);

--
-- Indices de la tabla `plan_cursos`
--
ALTER TABLE `plan_cursos`
  ADD PRIMARY KEY (`id_plan_curso`),
  ADD UNIQUE KEY `uk_plan_curso` (`id_plan`,`id_curso`),
  ADD KEY `fk_pc_curso` (`id_curso`);

--
-- Indices de la tabla `postulaciones`
--
ALTER TABLE `postulaciones`
  ADD PRIMARY KEY (`id_postulacion`),
  ADD KEY `fk_postulacion_proceso` (`id_proceso`),
  ADD KEY `fk_postulacion_carrera` (`id_carrera`),
  ADD KEY `fk_postulacion_modalidad` (`id_modalidad`),
  ADD KEY `idx_postulacion_persona` (`id_persona`);

--
-- Indices de la tabla `prerrequisitos`
--
ALTER TABLE `prerrequisitos`
  ADD PRIMARY KEY (`id_prerrequisito`),
  ADD UNIQUE KEY `uk_prerrequisito` (`id_plan_curso`,`id_curso_prerrequisito`),
  ADD KEY `fk_prerrequisito_curso` (`id_curso_prerrequisito`);

--
-- Indices de la tabla `procesos_admision`
--
ALTER TABLE `procesos_admision`
  ADD PRIMARY KEY (`id_proceso`);

--
-- Indices de la tabla `resultados_admision`
--
ALTER TABLE `resultados_admision`
  ADD PRIMARY KEY (`id_resultado`),
  ADD UNIQUE KEY `id_postulacion` (`id_postulacion`);

--
-- Indices de la tabla `resultados_finales`
--
ALTER TABLE `resultados_finales`
  ADD PRIMARY KEY (`id_resultado_final`),
  ADD UNIQUE KEY `id_detalle_matricula` (`id_detalle_matricula`);

--
-- Indices de la tabla `roles`
--
ALTER TABLE `roles`
  ADD PRIMARY KEY (`id_rol`),
  ADD UNIQUE KEY `nombre` (`nombre`);

--
-- Indices de la tabla `rol_permisos`
--
ALTER TABLE `rol_permisos`
  ADD PRIMARY KEY (`id_rol`,`id_permiso`),
  ADD KEY `fk_rp_permiso` (`id_permiso`);

--
-- Indices de la tabla `secciones`
--
ALTER TABLE `secciones`
  ADD PRIMARY KEY (`id_seccion`),
  ADD UNIQUE KEY `uk_seccion_periodo` (`id_periodo`,`id_curso`,`codigo`),
  ADD KEY `fk_seccion_curso` (`id_curso`),
  ADD KEY `idx_seccion_periodo` (`id_periodo`);

--
-- Indices de la tabla `seccion_docentes`
--
ALTER TABLE `seccion_docentes`
  ADD PRIMARY KEY (`id_seccion`,`id_docente`),
  ADD KEY `fk_sd_docente` (`id_docente`);

--
-- Indices de la tabla `seguimiento_tramites`
--
ALTER TABLE `seguimiento_tramites`
  ADD PRIMARY KEY (`id_seguimiento`),
  ADD KEY `fk_seguimiento_solicitud` (`id_solicitud`);

--
-- Indices de la tabla `sesiones_clase`
--
ALTER TABLE `sesiones_clase`
  ADD PRIMARY KEY (`id_sesion`),
  ADD KEY `fk_sesion_seccion` (`id_seccion`);

--
-- Indices de la tabla `solicitudes_tramite`
--
ALTER TABLE `solicitudes_tramite`
  ADD PRIMARY KEY (`id_solicitud`),
  ADD KEY `fk_solicitud_estudiante` (`id_estudiante`),
  ADD KEY `fk_solicitud_tipo` (`id_tipo_tramite`);

--
-- Indices de la tabla `tipos_tramite`
--
ALTER TABLE `tipos_tramite`
  ADD PRIMARY KEY (`id_tipo_tramite`),
  ADD UNIQUE KEY `nombre` (`nombre`);

--
-- Indices de la tabla `titulaciones`
--
ALTER TABLE `titulaciones`
  ADD PRIMARY KEY (`id_titulacion`),
  ADD KEY `fk_titulacion_egreso` (`id_egreso`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id_usuario`),
  ADD UNIQUE KEY `id_persona` (`id_persona`),
  ADD UNIQUE KEY `username` (`username`);

--
-- Indices de la tabla `usuario_roles`
--
ALTER TABLE `usuario_roles`
  ADD PRIMARY KEY (`id_usuario`,`id_rol`),
  ADD KEY `fk_ur_rol` (`id_rol`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `asistencias`
--
ALTER TABLE `asistencias`
  MODIFY `id_asistencia` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `auditoria`
--
ALTER TABLE `auditoria`
  MODIFY `id_auditoria` bigint(20) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `aulas`
--
ALTER TABLE `aulas`
  MODIFY `id_aula` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `calendario_academico`
--
ALTER TABLE `calendario_academico`
  MODIFY `id_evento` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `carreras`
--
ALTER TABLE `carreras`
  MODIFY `id_carrera` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `comprobantes`
--
ALTER TABLE `comprobantes`
  MODIFY `id_comprobante` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `conceptos_pago`
--
ALTER TABLE `conceptos_pago`
  MODIFY `id_concepto` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `cuentas_cobrar`
--
ALTER TABLE `cuentas_cobrar`
  MODIFY `id_cuenta` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `cursos`
--
ALTER TABLE `cursos`
  MODIFY `id_curso` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `detalle_matriculas`
--
ALTER TABLE `detalle_matriculas`
  MODIFY `id_detalle_matricula` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `docentes`
--
ALTER TABLE `docentes`
  MODIFY `id_docente` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `egresos`
--
ALTER TABLE `egresos`
  MODIFY `id_egreso` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `especialidades`
--
ALTER TABLE `especialidades`
  MODIFY `id_especialidad` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `estudiantes`
--
ALTER TABLE `estudiantes`
  MODIFY `id_estudiante` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `estudiante_carreras`
--
ALTER TABLE `estudiante_carreras`
  MODIFY `id_estudiante_carrera` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `evaluaciones`
--
ALTER TABLE `evaluaciones`
  MODIFY `id_evaluacion` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `evaluaciones_admision`
--
ALTER TABLE `evaluaciones_admision`
  MODIFY `id_evaluacion_admision` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `facultades`
--
ALTER TABLE `facultades`
  MODIFY `id_facultad` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `grados_academicos`
--
ALTER TABLE `grados_academicos`
  MODIFY `id_grado` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `horarios`
--
ALTER TABLE `horarios`
  MODIFY `id_horario` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `matriculas`
--
ALTER TABLE `matriculas`
  MODIFY `id_matricula` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `modalidades_ingreso`
--
ALTER TABLE `modalidades_ingreso`
  MODIFY `id_modalidad` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `notas`
--
ALTER TABLE `notas`
  MODIFY `id_nota` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `pagos`
--
ALTER TABLE `pagos`
  MODIFY `id_pago` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `periodos_academicos`
--
ALTER TABLE `periodos_academicos`
  MODIFY `id_periodo` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `permisos`
--
ALTER TABLE `permisos`
  MODIFY `id_permiso` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `personas`
--
ALTER TABLE `personas`
  MODIFY `id_persona` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `planes_estudio`
--
ALTER TABLE `planes_estudio`
  MODIFY `id_plan` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `plan_cursos`
--
ALTER TABLE `plan_cursos`
  MODIFY `id_plan_curso` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `postulaciones`
--
ALTER TABLE `postulaciones`
  MODIFY `id_postulacion` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `prerrequisitos`
--
ALTER TABLE `prerrequisitos`
  MODIFY `id_prerrequisito` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `procesos_admision`
--
ALTER TABLE `procesos_admision`
  MODIFY `id_proceso` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `resultados_admision`
--
ALTER TABLE `resultados_admision`
  MODIFY `id_resultado` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `resultados_finales`
--
ALTER TABLE `resultados_finales`
  MODIFY `id_resultado_final` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `roles`
--
ALTER TABLE `roles`
  MODIFY `id_rol` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `secciones`
--
ALTER TABLE `secciones`
  MODIFY `id_seccion` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `seguimiento_tramites`
--
ALTER TABLE `seguimiento_tramites`
  MODIFY `id_seguimiento` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `sesiones_clase`
--
ALTER TABLE `sesiones_clase`
  MODIFY `id_sesion` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `solicitudes_tramite`
--
ALTER TABLE `solicitudes_tramite`
  MODIFY `id_solicitud` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `tipos_tramite`
--
ALTER TABLE `tipos_tramite`
  MODIFY `id_tipo_tramite` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `titulaciones`
--
ALTER TABLE `titulaciones`
  MODIFY `id_titulacion` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id_usuario` int(11) NOT NULL AUTO_INCREMENT;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `asistencias`
--
ALTER TABLE `asistencias`
  ADD CONSTRAINT `fk_asistencia_estudiante` FOREIGN KEY (`id_estudiante`) REFERENCES `estudiantes` (`id_estudiante`),
  ADD CONSTRAINT `fk_asistencia_sesion` FOREIGN KEY (`id_sesion`) REFERENCES `sesiones_clase` (`id_sesion`);

--
-- Filtros para la tabla `auditoria`
--
ALTER TABLE `auditoria`
  ADD CONSTRAINT `fk_auditoria_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE SET NULL;

--
-- Filtros para la tabla `calendario_academico`
--
ALTER TABLE `calendario_academico`
  ADD CONSTRAINT `fk_calendario_periodo` FOREIGN KEY (`id_periodo`) REFERENCES `periodos_academicos` (`id_periodo`);

--
-- Filtros para la tabla `carreras`
--
ALTER TABLE `carreras`
  ADD CONSTRAINT `fk_carrera_facultad` FOREIGN KEY (`id_facultad`) REFERENCES `facultades` (`id_facultad`);

--
-- Filtros para la tabla `comprobantes`
--
ALTER TABLE `comprobantes`
  ADD CONSTRAINT `fk_comprobante_pago` FOREIGN KEY (`id_pago`) REFERENCES `pagos` (`id_pago`);

--
-- Filtros para la tabla `cuentas_cobrar`
--
ALTER TABLE `cuentas_cobrar`
  ADD CONSTRAINT `fk_cuenta_concepto` FOREIGN KEY (`id_concepto`) REFERENCES `conceptos_pago` (`id_concepto`),
  ADD CONSTRAINT `fk_cuenta_estudiante` FOREIGN KEY (`id_estudiante`) REFERENCES `estudiantes` (`id_estudiante`),
  ADD CONSTRAINT `fk_cuenta_periodo` FOREIGN KEY (`id_periodo`) REFERENCES `periodos_academicos` (`id_periodo`);

--
-- Filtros para la tabla `detalle_matriculas`
--
ALTER TABLE `detalle_matriculas`
  ADD CONSTRAINT `fk_dm_matricula` FOREIGN KEY (`id_matricula`) REFERENCES `matriculas` (`id_matricula`),
  ADD CONSTRAINT `fk_dm_seccion` FOREIGN KEY (`id_seccion`) REFERENCES `secciones` (`id_seccion`);

--
-- Filtros para la tabla `docentes`
--
ALTER TABLE `docentes`
  ADD CONSTRAINT `fk_docente_persona` FOREIGN KEY (`id_persona`) REFERENCES `personas` (`id_persona`);

--
-- Filtros para la tabla `docente_especialidades`
--
ALTER TABLE `docente_especialidades`
  ADD CONSTRAINT `fk_de_docente` FOREIGN KEY (`id_docente`) REFERENCES `docentes` (`id_docente`),
  ADD CONSTRAINT `fk_de_especialidad` FOREIGN KEY (`id_especialidad`) REFERENCES `especialidades` (`id_especialidad`);

--
-- Filtros para la tabla `egresos`
--
ALTER TABLE `egresos`
  ADD CONSTRAINT `fk_egreso_estudiante` FOREIGN KEY (`id_estudiante`) REFERENCES `estudiantes` (`id_estudiante`);

--
-- Filtros para la tabla `estudiantes`
--
ALTER TABLE `estudiantes`
  ADD CONSTRAINT `fk_estudiante_persona` FOREIGN KEY (`id_persona`) REFERENCES `personas` (`id_persona`);

--
-- Filtros para la tabla `estudiante_carreras`
--
ALTER TABLE `estudiante_carreras`
  ADD CONSTRAINT `fk_ec_carrera` FOREIGN KEY (`id_carrera`) REFERENCES `carreras` (`id_carrera`),
  ADD CONSTRAINT `fk_ec_estudiante` FOREIGN KEY (`id_estudiante`) REFERENCES `estudiantes` (`id_estudiante`),
  ADD CONSTRAINT `fk_ec_plan` FOREIGN KEY (`id_plan`) REFERENCES `planes_estudio` (`id_plan`);

--
-- Filtros para la tabla `evaluaciones`
--
ALTER TABLE `evaluaciones`
  ADD CONSTRAINT `fk_evaluacion_seccion` FOREIGN KEY (`id_seccion`) REFERENCES `secciones` (`id_seccion`);

--
-- Filtros para la tabla `evaluaciones_admision`
--
ALTER TABLE `evaluaciones_admision`
  ADD CONSTRAINT `fk_evaluacion_postulacion` FOREIGN KEY (`id_postulacion`) REFERENCES `postulaciones` (`id_postulacion`);

--
-- Filtros para la tabla `grados_academicos`
--
ALTER TABLE `grados_academicos`
  ADD CONSTRAINT `fk_grado_egreso` FOREIGN KEY (`id_egreso`) REFERENCES `egresos` (`id_egreso`);

--
-- Filtros para la tabla `horarios`
--
ALTER TABLE `horarios`
  ADD CONSTRAINT `fk_horario_aula` FOREIGN KEY (`id_aula`) REFERENCES `aulas` (`id_aula`),
  ADD CONSTRAINT `fk_horario_seccion` FOREIGN KEY (`id_seccion`) REFERENCES `secciones` (`id_seccion`);

--
-- Filtros para la tabla `matriculas`
--
ALTER TABLE `matriculas`
  ADD CONSTRAINT `fk_matricula_estudiante` FOREIGN KEY (`id_estudiante`) REFERENCES `estudiantes` (`id_estudiante`),
  ADD CONSTRAINT `fk_matricula_periodo` FOREIGN KEY (`id_periodo`) REFERENCES `periodos_academicos` (`id_periodo`);

--
-- Filtros para la tabla `notas`
--
ALTER TABLE `notas`
  ADD CONSTRAINT `fk_nota_estudiante` FOREIGN KEY (`id_estudiante`) REFERENCES `estudiantes` (`id_estudiante`),
  ADD CONSTRAINT `fk_nota_evaluacion` FOREIGN KEY (`id_evaluacion`) REFERENCES `evaluaciones` (`id_evaluacion`);

--
-- Filtros para la tabla `pagos`
--
ALTER TABLE `pagos`
  ADD CONSTRAINT `fk_pago_cuenta` FOREIGN KEY (`id_cuenta`) REFERENCES `cuentas_cobrar` (`id_cuenta`);

--
-- Filtros para la tabla `planes_estudio`
--
ALTER TABLE `planes_estudio`
  ADD CONSTRAINT `fk_plan_carrera` FOREIGN KEY (`id_carrera`) REFERENCES `carreras` (`id_carrera`);

--
-- Filtros para la tabla `plan_cursos`
--
ALTER TABLE `plan_cursos`
  ADD CONSTRAINT `fk_pc_curso` FOREIGN KEY (`id_curso`) REFERENCES `cursos` (`id_curso`),
  ADD CONSTRAINT `fk_pc_plan` FOREIGN KEY (`id_plan`) REFERENCES `planes_estudio` (`id_plan`);

--
-- Filtros para la tabla `postulaciones`
--
ALTER TABLE `postulaciones`
  ADD CONSTRAINT `fk_postulacion_carrera` FOREIGN KEY (`id_carrera`) REFERENCES `carreras` (`id_carrera`),
  ADD CONSTRAINT `fk_postulacion_modalidad` FOREIGN KEY (`id_modalidad`) REFERENCES `modalidades_ingreso` (`id_modalidad`),
  ADD CONSTRAINT `fk_postulacion_persona` FOREIGN KEY (`id_persona`) REFERENCES `personas` (`id_persona`),
  ADD CONSTRAINT `fk_postulacion_proceso` FOREIGN KEY (`id_proceso`) REFERENCES `procesos_admision` (`id_proceso`);

--
-- Filtros para la tabla `prerrequisitos`
--
ALTER TABLE `prerrequisitos`
  ADD CONSTRAINT `fk_prerrequisito_curso` FOREIGN KEY (`id_curso_prerrequisito`) REFERENCES `cursos` (`id_curso`),
  ADD CONSTRAINT `fk_prerrequisito_plan_curso` FOREIGN KEY (`id_plan_curso`) REFERENCES `plan_cursos` (`id_plan_curso`);

--
-- Filtros para la tabla `resultados_admision`
--
ALTER TABLE `resultados_admision`
  ADD CONSTRAINT `fk_resultado_postulacion` FOREIGN KEY (`id_postulacion`) REFERENCES `postulaciones` (`id_postulacion`);

--
-- Filtros para la tabla `resultados_finales`
--
ALTER TABLE `resultados_finales`
  ADD CONSTRAINT `fk_resultado_detalle` FOREIGN KEY (`id_detalle_matricula`) REFERENCES `detalle_matriculas` (`id_detalle_matricula`);

--
-- Filtros para la tabla `rol_permisos`
--
ALTER TABLE `rol_permisos`
  ADD CONSTRAINT `fk_rp_permiso` FOREIGN KEY (`id_permiso`) REFERENCES `permisos` (`id_permiso`),
  ADD CONSTRAINT `fk_rp_rol` FOREIGN KEY (`id_rol`) REFERENCES `roles` (`id_rol`);

--
-- Filtros para la tabla `secciones`
--
ALTER TABLE `secciones`
  ADD CONSTRAINT `fk_seccion_curso` FOREIGN KEY (`id_curso`) REFERENCES `cursos` (`id_curso`),
  ADD CONSTRAINT `fk_seccion_periodo` FOREIGN KEY (`id_periodo`) REFERENCES `periodos_academicos` (`id_periodo`);

--
-- Filtros para la tabla `seccion_docentes`
--
ALTER TABLE `seccion_docentes`
  ADD CONSTRAINT `fk_sd_docente` FOREIGN KEY (`id_docente`) REFERENCES `docentes` (`id_docente`),
  ADD CONSTRAINT `fk_sd_seccion` FOREIGN KEY (`id_seccion`) REFERENCES `secciones` (`id_seccion`);

--
-- Filtros para la tabla `seguimiento_tramites`
--
ALTER TABLE `seguimiento_tramites`
  ADD CONSTRAINT `fk_seguimiento_solicitud` FOREIGN KEY (`id_solicitud`) REFERENCES `solicitudes_tramite` (`id_solicitud`);

--
-- Filtros para la tabla `sesiones_clase`
--
ALTER TABLE `sesiones_clase`
  ADD CONSTRAINT `fk_sesion_seccion` FOREIGN KEY (`id_seccion`) REFERENCES `secciones` (`id_seccion`);

--
-- Filtros para la tabla `solicitudes_tramite`
--
ALTER TABLE `solicitudes_tramite`
  ADD CONSTRAINT `fk_solicitud_estudiante` FOREIGN KEY (`id_estudiante`) REFERENCES `estudiantes` (`id_estudiante`),
  ADD CONSTRAINT `fk_solicitud_tipo` FOREIGN KEY (`id_tipo_tramite`) REFERENCES `tipos_tramite` (`id_tipo_tramite`);

--
-- Filtros para la tabla `titulaciones`
--
ALTER TABLE `titulaciones`
  ADD CONSTRAINT `fk_titulacion_egreso` FOREIGN KEY (`id_egreso`) REFERENCES `egresos` (`id_egreso`);

--
-- Filtros para la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD CONSTRAINT `fk_usuario_persona` FOREIGN KEY (`id_persona`) REFERENCES `personas` (`id_persona`);

--
-- Filtros para la tabla `usuario_roles`
--
ALTER TABLE `usuario_roles`
  ADD CONSTRAINT `fk_ur_rol` FOREIGN KEY (`id_rol`) REFERENCES `roles` (`id_rol`),
  ADD CONSTRAINT `fk_ur_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
