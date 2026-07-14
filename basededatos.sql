/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

CREATE DATABASE IF NOT EXISTS `gestion_talento` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_uca1400_ai_ci */;
USE `gestion_talento`;

CREATE TABLE IF NOT EXISTS `cargo` (
  `id_cargo` int(11) NOT NULL AUTO_INCREMENT,
  `nombre_cargo` varchar(100) NOT NULL DEFAULT '',
  PRIMARY KEY (`id_cargo`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

INSERT INTO `cargo` (`id_cargo`, `nombre_cargo`) VALUES
	(1, 'Limpiador'),
	(2, 'Soletero'),
	(3, 'Montador'),
	(4, 'Forrador'),
	(5, 'Costurero'),
	(6, 'Cortador'),
	(7, 'Supervisor'),
	(8, 'Otro');

CREATE TABLE IF NOT EXISTS `expediente` (
  `cedula` varchar(20) NOT NULL,
  `nombre_emergencia` varchar(100) DEFAULT '',
  `parentesco_emergencia` varchar(50) DEFAULT '',
  `telefono_emergencia` varchar(20) DEFAULT '',
  `tiene_condiciones` tinyint(1) DEFAULT 0,
  `descripcion_condiciones` text DEFAULT NULL,
  `foto_path` varchar(255) DEFAULT '',
  `fecha_nacimiento` date DEFAULT NULL,
  `direccion` varchar(255) DEFAULT '',
  `telefono` varchar(20) DEFAULT '',
  `correo` varchar(100) DEFAULT '',
  `numero_hijos` int(11) DEFAULT 0,
  PRIMARY KEY (`cedula`),
  CONSTRAINT `expediente_ibfk_1` FOREIGN KEY (`cedula`) REFERENCES `trabajador` (`cedula`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;


CREATE TABLE IF NOT EXISTS `nomina` (
  `id_nomina` int(11) NOT NULL AUTO_INCREMENT,
  `cedula` varchar(20) NOT NULL,
  `periodo` varchar(20) DEFAULT 'Quincenal',
  `fecha_inicio` date DEFAULT NULL,
  `fecha_fin` date DEFAULT NULL,
  `salario_base` decimal(10,2) DEFAULT 0.00,
  `asignacion_produccion` decimal(10,2) DEFAULT 0.00,
  `estaticket` decimal(10,2) DEFAULT 0.00,
  `alicuota_utilidades` decimal(10,2) DEFAULT 0.00,
  `alicuota_bono_vacacional` decimal(10,2) DEFAULT 0.00,
  `total_asignaciones` decimal(10,2) DEFAULT 0.00,
  `deduccion_ivss` decimal(10,2) DEFAULT 0.00,
  `deduccion_faov` decimal(10,2) DEFAULT 0.00,
  `total_deducciones` decimal(10,2) DEFAULT 0.00,
  `neto_pagar` decimal(10,2) DEFAULT 0.00,
  `aporte_ivss_patronal` decimal(10,2) DEFAULT 0.00,
  `aporte_lopcymat` decimal(10,2) DEFAULT 0.00,
  `total_aportes_patronales` decimal(10,2) DEFAULT 0.00,
  PRIMARY KEY (`id_nomina`),
  KEY `cedula` (`cedula`),
  CONSTRAINT `nomina_ibfk_1` FOREIGN KEY (`cedula`) REFERENCES `trabajador` (`cedula`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;


CREATE TABLE IF NOT EXISTS `parametros` (
  `id_parametro` int(11) NOT NULL AUTO_INCREMENT,
  `salario_minimo` decimal(10,2) NOT NULL DEFAULT 0.00,
  `lopcymat_patronal` decimal(5,2) NOT NULL DEFAULT 0.00,
  `ivss_patronal` decimal(5,2) NOT NULL DEFAULT 0.00,
  `ivss_trabajador` decimal(5,2) NOT NULL DEFAULT 0.00,
  `faov` decimal(5,2) NOT NULL DEFAULT 0.00,
  `inces` decimal(5,2) NOT NULL DEFAULT 0.00,
  PRIMARY KEY (`id_parametro`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;


CREATE TABLE IF NOT EXISTS `permiso` (
  `id_permiso` int(11) NOT NULL AUTO_INCREMENT,
  `cedula` varchar(20) NOT NULL,
  `tipo` varchar(50) NOT NULL DEFAULT '',
  `dias` int(11) NOT NULL DEFAULT 0,
  `fecha_inicio` date NOT NULL,
  `fecha_fin` date NOT NULL,
  `motivo` text DEFAULT NULL,
  PRIMARY KEY (`id_permiso`),
  KEY `cedula` (`cedula`),
  CONSTRAINT `permiso_ibfk_1` FOREIGN KEY (`cedula`) REFERENCES `trabajador` (`cedula`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;


CREATE TABLE IF NOT EXISTS `produccion` (
  `id_produccion` int(11) NOT NULL AUTO_INCREMENT,
  `cedula` varchar(20) NOT NULL,
  `fecha` date NOT NULL,
  `ticket` varchar(50) DEFAULT '',
  `referencia` varchar(50) DEFAULT '',
  `color` varchar(30) DEFAULT '',
  `cantidad` int(11) DEFAULT 0,
  `pedido` varchar(100) DEFAULT '',
  `precio_unitario` decimal(10,2) DEFAULT 0.00,
  `total` decimal(10,2) DEFAULT 0.00,
  PRIMARY KEY (`id_produccion`),
  KEY `cedula` (`cedula`),
  CONSTRAINT `produccion_ibfk_1` FOREIGN KEY (`cedula`) REFERENCES `trabajador` (`cedula`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;


CREATE TABLE IF NOT EXISTS `registro_diario` (
  `id_registro` int(11) NOT NULL AUTO_INCREMENT,
  `cedula` varchar(20) NOT NULL,
  `fecha` date NOT NULL,
  `hora_entrada` time DEFAULT NULL,
  `hora_salida` time DEFAULT NULL,
  PRIMARY KEY (`id_registro`),
  UNIQUE KEY `unique_registro_dia` (`cedula`,`fecha`),
  CONSTRAINT `registro_diario_ibfk_1` FOREIGN KEY (`cedula`) REFERENCES `trabajador` (`cedula`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;


CREATE TABLE IF NOT EXISTS `trabajador` (
  `cedula` varchar(20) NOT NULL,
  `nombres` varchar(100) NOT NULL DEFAULT '',
  `apellidos` varchar(100) NOT NULL DEFAULT '',
  `id_cargo` int(11) NOT NULL,
  PRIMARY KEY (`cedula`),
  KEY `id_cargo` (`id_cargo`),
  CONSTRAINT `trabajador_ibfk_1` FOREIGN KEY (`id_cargo`) REFERENCES `cargo` (`id_cargo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;

INSERT INTO `trabajador` (`cedula`, `nombres`, `apellidos`, `id_cargo`) VALUES
	('32070926', 'Jonathan', 'Novoa', 7),
	('32202309', 'Diego', 'Garcia', 1);

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
