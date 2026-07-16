from typing import List, Tuple, Dict, Optional
from datetime import datetime, timedelta
import re
from .trabajador import Trabajador
from .registro import RegistroEntrada, RegistroProduccion
from .permiso import Permiso


class Nomina:
    TIPOS_PERMISO_VALIDOS = ['Médico', 'Personal', 'Familiar', 'Estudio', 'Vacaciones', 'Otro']

    def __init__(self):
        self.trabajadores: Dict[str, Trabajador] = {}
        self.produccion: Dict[str, List[RegistroProduccion]] = {}
        self.db_manager = None
        self._inicializar_db()

    def _inicializar_db(self):
        try:
            from ..database_manager import DatabaseManager
            self.db_manager = DatabaseManager()
            self.cargar_datos()
        except Exception as e:
            print(f"⚠️ No se pudo conectar a la base de datos: {e}")
            print("   La aplicación funcionará en modo local (sin persistencia)")

    def cargar_datos(self) -> None:
        if self.db_manager:
            self.db_manager.sincronizar_todo(self)

    def guardar_datos(self) -> None:
        if self.db_manager:
            for cedula, trabajador in self.trabajadores.items():
                self.db_manager.guardar_trabajador(trabajador)
            print("✅ Datos guardados en la base de datos")

    def agregar_trabajador(self, cedula: str, nombres: str, apellidos: str, cargo: str) -> Tuple[bool, str]:
        cedula = cedula.strip()
        nombres = nombres.strip()
        apellidos = apellidos.strip()
        if not cedula or not nombres or not apellidos:
            return False, "Cédula, nombres y apellidos son requeridos"
        if not cedula.isdigit():
            return False, "La cédula debe contener solo números"
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', nombres):
            return False, "Los nombres solo pueden contener letras y espacios"
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', apellidos):
            return False, "Los apellidos solo pueden contener letras y espacios"
        if cedula in self.trabajadores:
            return False, f"Ya existe un trabajador con cédula {cedula}"
        if cargo not in Trabajador.CARGOS_VALIDOS:
            return False, f"Cargo inválido. Opciones: {', '.join(Trabajador.CARGOS_VALIDOS)}"
        try:
            nuevo = Trabajador(cedula, nombres, apellidos, cargo)
            self.trabajadores[cedula] = nuevo
            if self.db_manager and self.db_manager.guardar_trabajador(nuevo):
                return True, f"Trabajador {nombres} {apellidos} agregado exitosamente"
            elif self.db_manager is None:
                return True, f"Trabajador {nombres} {apellidos} agregado (sin conexión a BD)"
            else:
                del self.trabajadores[cedula]
                return False, "Error al guardar en la base de datos"
        except ValueError as e:
            return False, f"Error: {str(e)}"

    def registrar_entrada(self, cedula: str) -> Tuple[bool, str]:
        trabajador = self.trabajadores.get(cedula)
        if not trabajador:
            return False, "Trabajador no encontrado"
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        hora_actual = datetime.now().strftime("%H:%M:%S")
        if trabajador.get_registro_por_fecha(fecha_hoy):
            return False, f"{trabajador.nombre} ya registró entrada hoy"
        permiso = trabajador.tiene_permiso_en_fecha(fecha_hoy)
        if permiso:
            return False, f"{trabajador.nombre} tiene permiso ({permiso.tipo}) hoy"
        registro = RegistroEntrada(fecha_hoy, hora_actual)
        trabajador.agregar_registro_entrada(registro)
        if self.db_manager:
            self.db_manager.guardar_registro(cedula, fecha_hoy, hora_actual)
        return True, f"ENTRADA REGISTRADA - {trabajador.nombre} a las {hora_actual}"

    def registrar_salida(self, cedula: str) -> Tuple[bool, str]:
        trabajador = self.trabajadores.get(cedula)
        if not trabajador:
            return False, "Trabajador no encontrado"
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        permiso = trabajador.tiene_permiso_en_fecha(fecha_hoy)
        if permiso:
            return False, f"{trabajador.nombre} tiene permiso ({permiso.tipo}) hoy, no puede registrar salida"
        registro = trabajador.get_registro_por_fecha(fecha_hoy)
        if not registro:
            return False, f"{trabajador.nombre} no ha registrado entrada hoy"
        if registro.hora_salida:
            return False, f"{trabajador.nombre} ya registró salida hoy"
        hora_actual = datetime.now().strftime("%H:%M:%S")
        registro.hora_salida = hora_actual
        if self.db_manager:
            self.db_manager.guardar_registro(cedula, fecha_hoy, registro.hora_entrada, hora_actual)
        horas = trabajador.get_horas_trabajadas_hoy()
        return True, f"SALIDA REGISTRADA - {trabajador.nombre} a las {hora_actual} (Horas: {horas}h)"

    def registrar_permiso(self, cedula: str, tipo: str, dias: int, motivo: str,
                          fecha_inicio: str = None, fecha_fin: str = None) -> Tuple[bool, str]:
        trabajador = self.trabajadores.get(cedula)
        if not trabajador:
            return False, "Trabajador no encontrado"
        if tipo not in self.TIPOS_PERMISO_VALIDOS:
            return False, f"Tipo de permiso inválido. Opciones: {', '.join(self.TIPOS_PERMISO_VALIDOS)}"
        if dias <= 0:
            return False, "Los días deben ser un número positivo"
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', motivo):
            return False, "El motivo solo puede contener letras y espacios"
        if fecha_inicio is None:
            fecha_inicio = datetime.now().strftime("%Y-%m-%d")
        if fecha_fin is None:
            fecha_fin = (datetime.strptime(fecha_inicio, "%Y-%m-%d") + timedelta(days=dias-1)).strftime("%Y-%m-%d")
        try:
            d_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
            d_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
            if d_fin < d_inicio:
                return False, "La fecha de fin no puede ser anterior a la fecha de inicio"
            dias_calculados = (d_fin - d_inicio).days + 1
            if dias_calculados != dias:
                return False, f"El número de días ({dias}) no coincide con el rango de fechas ({dias_calculados} días)"
        except ValueError as e:
            return False, f"Formato de fecha inválido: {e}"

        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        if fecha_inicio <= fecha_hoy <= fecha_fin:
            registro_hoy = trabajador.get_registro_por_fecha(fecha_hoy)
            if registro_hoy and not registro_hoy.hora_salida:
                return False, "El trabajador está activo hoy (tiene una entrada sin salida). No se puede registrar un permiso que cubra hoy."

        try:
            permiso = Permiso(tipo, dias, motivo, fecha_inicio, fecha_fin)
            if trabajador.agregar_permiso(permiso):
                if self.db_manager:
                    self.db_manager.guardar_permiso(cedula, tipo, dias, fecha_inicio, fecha_fin, motivo)
                return True, f"Permiso {tipo} registrado para {trabajador.nombre}"
            else:
                return False, "El permiso se solapa con otro existente"
        except ValueError as e:
            return False, f"Error: {str(e)}"

    def modificar_permiso(self, cedula: str, indice: int, nuevo_permiso: Permiso) -> Tuple[bool, str]:
        trabajador = self.trabajadores.get(cedula)
        if not trabajador:
            return False, "Trabajador no encontrado"
        if indice < 0 or indice >= len(trabajador.permisos):
            return False, "Índice de permiso inválido"
        
        for i, p in enumerate(trabajador.permisos):
            if i == indice:
                continue
            if (nuevo_permiso.fecha_inicio <= p.fecha_fin and nuevo_permiso.fecha_fin >= p.fecha_inicio):
                return False, "El nuevo permiso se solapa con otro existente"
        
        permiso_viejo = trabajador.permisos[indice]
        id_permiso = getattr(permiso_viejo, 'id_permiso', None)
        
        trabajador.permisos[indice] = nuevo_permiso
        trabajador._cache_estado.clear()
        
        if self.db_manager and id_permiso:
            self.db_manager.modificar_permiso(
                id_permiso,
                nuevo_permiso.tipo,
                nuevo_permiso.dias,
                nuevo_permiso.fecha_inicio,
                nuevo_permiso.fecha_fin,
                nuevo_permiso.motivo
            )
        elif self.db_manager:
            self.db_manager.guardar_permiso(
                cedula,
                nuevo_permiso.tipo,
                nuevo_permiso.dias,
                nuevo_permiso.fecha_inicio,
                nuevo_permiso.fecha_fin,
                nuevo_permiso.motivo
            )
        return True, "Permiso modificado exitosamente"

    def eliminar_permiso(self, cedula: str, indice: int) -> Tuple[bool, str]:
        trabajador = self.trabajadores.get(cedula)
        if not trabajador:
            return False, "Trabajador no encontrado"
        if indice < 0 or indice >= len(trabajador.permisos):
            return False, "Índice de permiso inválido"
        
        permiso = trabajador.permisos[indice]
        id_permiso = getattr(permiso, 'id_permiso', None)
        
        del trabajador.permisos[indice]
        trabajador._cache_estado.clear()
        
        if self.db_manager and id_permiso:
            self.db_manager.eliminar_permiso(id_permiso)
        return True, "Permiso eliminado"

    def verificar_estado_hoy(self, cedula: str) -> Tuple[str, str]:
        trabajador = self.trabajadores.get(cedula)
        if not trabajador:
            return "Trabajador no encontrado", 'error'
        return trabajador.get_estado_hoy()

    def get_trabajadores_lista(self) -> List[Tuple[str, str]]:
        return [(cedula, t.nombre) for cedula, t in self.trabajadores.items()]

    def get_trabajadores_con_detalle(self) -> List[Tuple[str, str, str, str]]:
        return [(cedula, t.nombre, t.nombres, t.apellidos) for cedula, t in self.trabajadores.items()]

    def get_registros_por_fecha(self, cedula: str, fecha: str) -> List[str]:
        trabajador = self.trabajadores.get(cedula)
        if not trabajador:
            return []
        registro = trabajador.get_registro_por_fecha(fecha)
        if registro:
            return [str(registro)]
        return []

    def get_permisos_por_fecha(self, cedula: str, fecha: str) -> List[str]:
        trabajador = self.trabajadores.get(cedula)
        if not trabajador:
            return []
        permisos = []
        for permiso in trabajador.permisos:
            if permiso.cubre_fecha(fecha):
                permisos.append(str(permiso))
        return permisos

    def actualizar_cargo(self, cedula: str, nuevo_cargo: str) -> Tuple[bool, str]:
        trabajador = self.trabajadores.get(cedula)
        if not trabajador:
            return False, "Trabajador no encontrado"
        if nuevo_cargo not in Trabajador.CARGOS_VALIDOS:
            return False, f"Cargo inválido. Opciones: {', '.join(Trabajador.CARGOS_VALIDOS)}"
        cargo_anterior = trabajador.cargo
        trabajador.cargo = nuevo_cargo
        if self.db_manager:
            self.db_manager.guardar_trabajador(trabajador)
        return True, f"Cargo actualizado: {trabajador.nombre} de '{cargo_anterior}' a '{nuevo_cargo}'"

    def eliminar_trabajador(self, cedula: str) -> Tuple[bool, str]:
        if cedula not in self.trabajadores:
            return False, "Trabajador no encontrado"
        nombre = self.trabajadores[cedula].nombre
        del self.trabajadores[cedula]
        if self.db_manager:
            self.db_manager.eliminar_trabajador_completo(cedula)
        return True, f"Trabajador {nombre} eliminado exitosamente"

    def buscar_trabajador(self, cedula: str = None, nombre: str = None) -> List[Trabajador]:
        resultados = []
        for t in self.trabajadores.values():
            if cedula and cedula in t.cedula:
                resultados.append(t)
            elif nombre and nombre.lower() in t.nombre.lower():
                resultados.append(t)
            elif not cedula and not nombre:
                resultados.append(t)
        return resultados

    def agregar_produccion(self, cedula: str, registro: RegistroProduccion):
        if not isinstance(registro.pares, int) or registro.pares <= 0:
            raise ValueError("Los pares deben ser un entero positivo")
        if registro.pedido and not isinstance(registro.pedido, (int, str)):
            raise ValueError("El pedido debe ser un texto o número")
        if not isinstance(registro.precio, (int, float)) or registro.precio <= 0:
            raise ValueError("El precio debe ser un número positivo")
        if not isinstance(registro.color, str) or not registro.color.strip():
            raise ValueError("El color debe ser un texto no vacío")
        if cedula not in self.produccion:
            self.produccion[cedula] = []
        self.produccion[cedula].append(registro)
        if self.db_manager:
            id_prod = self.db_manager.guardar_produccion(cedula, registro)
            if id_prod:
                registro.id_produccion = id_prod

    def obtener_produccion(self, cedula: str) -> List[RegistroProduccion]:
        return self.produccion.get(cedula, [])

    def eliminar_produccion(self, cedula: str, indice: int) -> bool:
        if cedula in self.produccion and 0 <= indice < len(self.produccion[cedula]):
            registro = self.produccion[cedula][indice]
            if self.db_manager and hasattr(registro, 'id_produccion') and registro.id_produccion:
                self.db_manager.eliminar_produccion(registro.id_produccion)
            del self.produccion[cedula][indice]
            return True
        return False

    def modificar_produccion(self, cedula: str, indice: int, nuevo_registro: RegistroProduccion) -> bool:
        if cedula in self.produccion and 0 <= indice < len(self.produccion[cedula]):
            viejo = self.produccion[cedula][indice]
            if hasattr(viejo, 'id_produccion') and viejo.id_produccion:
                nuevo_registro.id_produccion = viejo.id_produccion
            self.produccion[cedula][indice] = nuevo_registro
            if self.db_manager:
                if nuevo_registro.id_produccion:
                    self.db_manager.modificar_produccion(nuevo_registro.id_produccion, nuevo_registro)
                else:
                    id_prod = self.db_manager.guardar_produccion(cedula, nuevo_registro)
                    if id_prod:
                        nuevo_registro.id_produccion = id_prod
            return True
        return False