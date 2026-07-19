# inver/database.py
import mysql.connector
from mysql.connector import Error
from typing import Optional, List, Dict, Tuple, Any
from datetime import datetime
import os


class Database:
    """Clase para manejar la conexión y operaciones con la base de datos MySQL."""
    
    def __init__(self, host='localhost', database='gestion_talento', user='root', password='root'):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.connection = None
        self.cursor = None

    def connect(self) -> bool:
        """Establece conexión con la base de datos."""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                database=self.database,
                user=self.user,
                password=self.password
            )
            self.cursor = self.connection.cursor(dictionary=True)
            print(f"✅ Conectado a la base de datos: {self.database}")
            return True
        except Error as e:
            print(f"❌ Error al conectar: {e}")
            return False

    def disconnect(self):
        """Cierra la conexión."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("🔌 Conexión cerrada")

    def execute_query(self, query: str, params: tuple = None) -> Optional[List[Dict]]:
        """Ejecuta una consulta y retorna los resultados con manejo de concurrencia."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                if not self.connection or not self.connection.is_connected():
                    self.connect()
                
                # Usar un cursor nuevo para cada intento
                cursor = self.connection.cursor(dictionary=True, buffered=True)
                cursor.execute(query, params or ())
                
                if query.strip().upper().startswith('SELECT'):
                    result = cursor.fetchall()
                    cursor.close()
                    return result
                
                self.connection.commit()
                cursor.close()
                return None
                
            except Error as e:
                print(f"❌ Error en consulta (intento {attempt + 1}): {e}")
                if self.connection:
                    try:
                        self.connection.rollback()
                    except:
                        pass
                
                # Si es error de concurrencia, reintentar
                if "Record has changed since last read" in str(e) or "1020" in str(e):
                    if attempt < max_retries - 1:
                        print(f"⚠️ Reintentando ({attempt + 1}/{max_retries})...")
                        self.disconnect()
                        continue
                return None
            except Exception as e:
                print(f"❌ Error inesperado: {e}")
                return None
        return None

    def get_cargo_id(self, nombre_cargo: str) -> Optional[int]:
        """Obtiene el ID de un cargo por su nombre."""
        query = "SELECT id_cargo FROM cargo WHERE nombre_cargo = %s"
        result = self.execute_query(query, (nombre_cargo,))
        return result[0]['id_cargo'] if result else None

    def get_cargo_nombre(self, id_cargo: int) -> Optional[str]:
        """Obtiene el nombre de un cargo por su ID."""
        query = "SELECT nombre_cargo FROM cargo WHERE id_cargo = %s"
        result = self.execute_query(query, (id_cargo,))
        return result[0]['nombre_cargo'] if result else None


class TrabajadorDB(Database):
    """Operaciones CRUD para trabajadores."""
    
    def guardar_trabajador(self, cedula: str, nombres: str, apellidos: str, cargo: str) -> bool:
        """Guarda un trabajador en la base de datos."""
        cargo_id = self.get_cargo_id(cargo)
        if not cargo_id:
            return False
        
        query = """
            INSERT INTO trabajador (cedula, nombres, apellidos, id_cargo)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            nombres = VALUES(nombres),
            apellidos = VALUES(apellidos),
            id_cargo = VALUES(id_cargo)
        """
        result = self.execute_query(query, (cedula, nombres, apellidos, cargo_id))
        return result is None

    def obtener_trabajador(self, cedula: str) -> Optional[Dict]:
        """Obtiene un trabajador por su cédula."""
        query = """
            SELECT t.cedula, t.nombres, t.apellidos, c.nombre_cargo as cargo
            FROM trabajador t
            JOIN cargo c ON t.id_cargo = c.id_cargo
            WHERE t.cedula = %s
        """
        result = self.execute_query(query, (cedula,))
        return result[0] if result else None

    def obtener_todos_trabajadores(self) -> List[Dict]:
        """Obtiene todos los trabajadores."""
        query = """
            SELECT t.cedula, t.nombres, t.apellidos, c.nombre_cargo as cargo
            FROM trabajador t
            JOIN cargo c ON t.id_cargo = c.id_cargo
        """
        return self.execute_query(query) or []

    def eliminar_trabajador(self, cedula: str) -> bool:
        """Elimina un trabajador (ON DELETE CASCADE eliminará todo lo relacionado)."""
        query = "DELETE FROM trabajador WHERE cedula = %s"
        result = self.execute_query(query, (cedula,))
        return result is None


class RegistroDB(Database):
    """Operaciones CRUD para registros diarios."""
    
    def guardar_registro(self, cedula: str, fecha: str, hora_entrada: str, hora_salida: str = None) -> bool:
        """Guarda un registro de entrada/salida."""
        query = """
            INSERT INTO registro_diario (cedula, fecha, hora_entrada, hora_salida)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            hora_entrada = VALUES(hora_entrada),
            hora_salida = VALUES(hora_salida)
        """
        result = self.execute_query(query, (cedula, fecha, hora_entrada, hora_salida))
        return result is None

    def obtener_registro_dia(self, cedula: str, fecha: str) -> Optional[Dict]:
        """Obtiene el registro de un día específico."""
        query = """
            SELECT fecha, hora_entrada, hora_salida
            FROM registro_diario
            WHERE cedula = %s AND fecha = %s
        """
        result = self.execute_query(query, (cedula, fecha))
        return result[0] if result else None

    def obtener_registros_por_fecha(self, cedula: str, fecha_inicio: str, fecha_fin: str) -> List[Dict]:
        """Obtiene registros en un rango de fechas."""
        query = """
            SELECT fecha, hora_entrada, hora_salida
            FROM registro_diario
            WHERE cedula = %s AND fecha BETWEEN %s AND %s
            ORDER BY fecha
        """
        return self.execute_query(query, (cedula, fecha_inicio, fecha_fin)) or []


class PermisoDB(Database):
    """Operaciones CRUD para permisos."""
    
    def guardar_permiso(self, cedula: str, tipo: str, dias: int, fecha_inicio: str, fecha_fin: str, motivo: str) -> bool:
        """Guarda un permiso."""
        query = """
            INSERT INTO permiso (cedula, tipo, dias, fecha_inicio, fecha_fin, motivo)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        result = self.execute_query(query, (cedula, tipo, dias, fecha_inicio, fecha_fin, motivo))
        return result is None

    def obtener_permisos_por_fecha(self, cedula: str, fecha: str) -> List[Dict]:
        """Obtiene permisos activos para una fecha específica."""
        query = """
            SELECT id_permiso, tipo, dias, fecha_inicio, fecha_fin, motivo
            FROM permiso
            WHERE cedula = %s AND %s BETWEEN fecha_inicio AND fecha_fin
        """
        return self.execute_query(query, (cedula, fecha)) or []

    def obtener_todos_permisos(self, cedula: str = None) -> List[Dict]:
        """Obtiene todos los permisos de un trabajador."""
        if cedula:
            query = "SELECT * FROM permiso WHERE cedula = %s ORDER BY fecha_inicio"
            return self.execute_query(query, (cedula,)) or []
        query = "SELECT * FROM permiso ORDER BY fecha_inicio"
        return self.execute_query(query) or []

    def modificar_permiso(self, id_permiso: int, tipo: str, dias: int, 
                          fecha_inicio: str, fecha_fin: str, motivo: str) -> bool:
        """Modifica un permiso existente."""
        query = """
            UPDATE permiso 
            SET tipo = %s, dias = %s, fecha_inicio = %s, fecha_fin = %s, motivo = %s
            WHERE id_permiso = %s
        """
        result = self.execute_query(query, (tipo, dias, fecha_inicio, fecha_fin, motivo, id_permiso))
        return result is None

    def eliminar_permiso(self, id_permiso: int) -> bool:
        """Elimina un permiso por ID."""
        query = "DELETE FROM permiso WHERE id_permiso = %s"
        result = self.execute_query(query, (id_permiso,))
        return result is None

    def eliminar_permisos_trabajador(self, cedula: str) -> bool:
        """Elimina todos los permisos de un trabajador."""
        query = "DELETE FROM permiso WHERE cedula = %s"
        result = self.execute_query(query, (cedula,))
        return result is None


class ProduccionDB(Database):
    """Operaciones CRUD para producción."""
    
    def guardar_produccion(self, cedula: str, fecha: str, ticket: str, referencia: str,
                           color: str, cantidad: int, pedido: str, precio_unitario: float) -> bool:
        """Guarda un registro de producción con manejo de concurrencia."""
        total = cantidad * precio_unitario
        query = """
            INSERT INTO produccion (cedula, fecha, ticket, referencia, color, cantidad, pedido, precio_unitario, total)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            ticket = VALUES(ticket),
            referencia = VALUES(referencia),
            color = VALUES(color),
            cantidad = VALUES(cantidad),
            pedido = VALUES(pedido),
            precio_unitario = VALUES(precio_unitario),
            total = VALUES(total)
        """
        result = self.execute_query(query, (cedula, fecha, ticket, referencia, color, cantidad, pedido, precio_unitario, total))
        return result is None

    def obtener_produccion_por_cedula(self, cedula: str) -> List[Dict]:
        """Obtiene toda la producción de un trabajador."""
        query = """
            SELECT id_produccion, fecha, ticket, referencia, color, cantidad as pares, pedido, precio_unitario as precio, total
            FROM produccion
            WHERE cedula = %s
            ORDER BY fecha DESC
        """
        return self.execute_query(query, (cedula,)) or []

    def eliminar_produccion(self, id_produccion: int) -> bool:
        """Elimina un registro de producción."""
        query = "DELETE FROM produccion WHERE id_produccion = %s"
        result = self.execute_query(query, (id_produccion,))
        return result is None

    def modificar_produccion(self, id_produccion: int, fecha: str, ticket: str, referencia: str,
                             color: str, cantidad: int, pedido: str, precio_unitario: float) -> bool:
        """Modifica un registro de producción."""
        total = cantidad * precio_unitario
        query = """
            UPDATE produccion
            SET fecha = %s, ticket = %s, referencia = %s, color = %s,
                cantidad = %s, pedido = %s, precio_unitario = %s, total = %s
            WHERE id_produccion = %s
        """
        result = self.execute_query(query, (fecha, ticket, referencia, color, cantidad, pedido, precio_unitario, total, id_produccion))
        return result is None


class ExpedienteDB(Database):
    """Operaciones CRUD para expedientes."""
    
    def guardar_expediente(self, cedula: str, fecha_nacimiento: str = None, direccion: str = '',
                          telefono: str = '', correo: str = '', numero_hijos: int = 0,
                          nombre_emergencia: str = '', parentesco_emergencia: str = '',
                          telefono_emergencia: str = '', tiene_condiciones: bool = False,
                          descripcion_condiciones: str = '', foto_path: str = '') -> bool:
        """Guarda el expediente de un trabajador con manejo de concurrencia."""
        query = """
            INSERT INTO expediente 
            (cedula, fecha_nacimiento, direccion, telefono, correo, numero_hijos,
             nombre_emergencia, parentesco_emergencia, telefono_emergencia,
             tiene_condiciones, descripcion_condiciones, foto_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            fecha_nacimiento = VALUES(fecha_nacimiento),
            direccion = VALUES(direccion),
            telefono = VALUES(telefono),
            correo = VALUES(correo),
            numero_hijos = VALUES(numero_hijos),
            nombre_emergencia = VALUES(nombre_emergencia),
            parentesco_emergencia = VALUES(parentesco_emergencia),
            telefono_emergencia = VALUES(telefono_emergencia),
            tiene_condiciones = VALUES(tiene_condiciones),
            descripcion_condiciones = VALUES(descripcion_condiciones),
            foto_path = VALUES(foto_path)
        """
        result = self.execute_query(query, (
            cedula, fecha_nacimiento, direccion, telefono, correo, numero_hijos,
            nombre_emergencia, parentesco_emergencia, telefono_emergencia,
            1 if tiene_condiciones else 0, descripcion_condiciones, foto_path
        ))
        return result is None

    def obtener_expediente(self, cedula: str) -> Optional[Dict]:
        """Obtiene el expediente de un trabajador."""
        query = """
            SELECT * FROM expediente WHERE cedula = %s
        """
        result = self.execute_query(query, (cedula,))
        return result[0] if result else None


class NominaDB(Database):
    """Operaciones CRUD para nóminas."""
    
    def guardar_nomina(self, cedula: str, periodo: str, fecha_inicio: str, fecha_fin: str,
                      salario_base: float, asignacion_produccion: float, estaticket: float,
                      alicuota_utilidades: float, alicuota_bono_vacacional: float,
                      total_asignaciones: float, deduccion_ivss: float, deduccion_faov: float,
                      total_deducciones: float, neto_pagar: float,
                      aporte_ivss_patronal: float, aporte_lopcymat: float,
                      total_aportes_patronales: float) -> bool:
        """Guarda un cálculo de nómina."""
        query = """
            INSERT INTO nomina
            (cedula, periodo, fecha_inicio, fecha_fin, salario_base,
             asignacion_produccion, estaticket, alicuota_utilidades,
             alicuota_bono_vacacional, total_asignaciones,
             deduccion_ivss, deduccion_faov, total_deducciones, neto_pagar,
             aporte_ivss_patronal, aporte_lopcymat, total_aportes_patronales)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        result = self.execute_query(query, (
            cedula, periodo, fecha_inicio, fecha_fin, salario_base,
            asignacion_produccion, estaticket, alicuota_utilidades,
            alicuota_bono_vacacional, total_asignaciones,
            deduccion_ivss, deduccion_faov, total_deducciones, neto_pagar,
            aporte_ivss_patronal, aporte_lopcymat, total_aportes_patronales
        ))
        return result is None

    def obtener_nominas_por_cedula(self, cedula: str) -> List[Dict]:
        """Obtiene todas las nóminas de un trabajador."""
        query = """
            SELECT * FROM nomina WHERE cedula = %s ORDER BY fecha_inicio DESC
        """
        return self.execute_query(query, (cedula,)) or []