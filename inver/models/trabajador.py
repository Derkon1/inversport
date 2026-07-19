from datetime import datetime, timedelta
from typing import List, Optional, Dict
import re
from .registro import RegistroEntrada
from .permiso import Permiso


class Trabajador:
    CARGOS_VALIDOS = ['Limpiador', 'Soletero', 'Montador', 'Forrador', 'Costurero', 'Cortador', 'Supervisor', 'Otro']

    def __init__(self, cedula: str, nombres: str, apellidos: str, cargo: str):
        if not cedula or not cedula.strip():
            raise ValueError("La cédula no puede estar vacía")
        if not cedula.isdigit():
            raise ValueError("La cédula debe contener solo números")
        if not nombres or not nombres.strip():
            raise ValueError("Los nombres no pueden estar vacíos")
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', nombres):
            raise ValueError("Los nombres solo pueden contener letras y espacios")
        if not apellidos or not apellidos.strip():
            raise ValueError("Los apellidos no pueden estar vacíos")
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', apellidos):
            raise ValueError("Los apellidos solo pueden contener letras y espacios")
        if cargo not in self.CARGOS_VALIDOS:
            raise ValueError(f"Cargo inválido. Debe ser uno de: {', '.join(self.CARGOS_VALIDOS)}")

        self.cedula = cedula.strip()
        self.nombres = nombres.strip().title()
        self.apellidos = apellidos.strip().title()
        self.nombre = f"{self.nombres} {self.apellidos}".strip()
        self.cargo = cargo
        self.registros_entrada: List[RegistroEntrada] = []
        self.permisos: List[Permiso] = []
        self._cache_estado: Dict[str, int] = {}

        self.fecha_nacimiento: Optional[str] = None
        self.edad: Optional[int] = None
        self.direccion: str = ""
        self.telefono: str = ""
        self.correo: str = ""
        self.hijos: int = 0
        self.contacto_emergencia: Dict[str, str] = {
            "nombre": "",
            "parentesco": "",
            "telefono": ""
        }
        self.condiciones_medicas: str = ""
        self.foto_path: str = ""

    def calcular_edad(self):
        if self.fecha_nacimiento:
            try:
                nac = datetime.strptime(self.fecha_nacimiento, "%Y-%m-%d").date()
                hoy = datetime.now().date()
                self.edad = hoy.year - nac.year - ((hoy.month, hoy.day) < (nac.month, nac.day))
            except:
                self.edad = None
        else:
            self.edad = None

    @property
    def esta_activo_hoy(self) -> bool:
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        registro_hoy = self.get_registro_por_fecha(fecha_hoy)
        if registro_hoy and not registro_hoy.hora_salida:
            permiso = self.tiene_permiso_en_fecha(fecha_hoy)
            if permiso:
                return False
            return True
        return False

    def get_registro_por_fecha(self, fecha: str) -> Optional[RegistroEntrada]:
        for registro in self.registros_entrada:
            if registro.fecha == fecha:
                return registro
        return None

    def agregar_registro_entrada(self, registro: RegistroEntrada) -> bool:
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        if self.get_registro_por_fecha(fecha_hoy):
            return False
        self.registros_entrada.append(registro)
        self._cache_estado.clear()
        return True

    def registrar_salida(self, fecha: Optional[str] = None) -> bool:
        if fecha is None:
            fecha = datetime.now().strftime("%Y-%m-%d")
        registro = self.get_registro_por_fecha(fecha)
        if registro and not registro.hora_salida:
            registro.hora_salida = datetime.now().strftime("%H:%M:%S")
            return True
        return False

    def agregar_permiso(self, permiso: Permiso) -> bool:
        for p in self.permisos:
            if (permiso.fecha_inicio <= p.fecha_fin and permiso.fecha_fin >= p.fecha_inicio):
                return False
        self.permisos.append(permiso)
        return True

    def tiene_permiso_en_fecha(self, fecha: str) -> Optional[Permiso]:
        if fecha in self._cache_estado:
            permiso_idx = self._cache_estado[fecha]
            if permiso_idx >= 0:
                return self.permisos[permiso_idx]
            return None

        for i, permiso in enumerate(self.permisos):
            if permiso.cubre_fecha(fecha):
                self._cache_estado[fecha] = i
                return permiso
        self._cache_estado[fecha] = -1
        return None

    def get_estado_hoy(self) -> tuple:
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        permiso = self.tiene_permiso_en_fecha(fecha_hoy)
        if permiso:
            return f"EN PERMISO ({permiso.tipo})", 'warning'

        registro_hoy = self.get_registro_por_fecha(fecha_hoy)
        if not registro_hoy:
            return "NO HA ENTRADO", 'error'

        if not registro_hoy.hora_salida:
            return f"TRABAJANDO (Entrada: {registro_hoy.hora_entrada})", 'success'
        else:
            return f"FINALIZADO (Salida: {registro_hoy.hora_salida})", 'info'

    def get_horas_trabajadas_hoy(self) -> Optional[float]:
        fecha_hoy = datetime.now().strftime("%Y-%m-%d")
        registro = self.get_registro_por_fecha(fecha_hoy)
        if registro and registro.hora_salida:
            entrada = datetime.strptime(f"{fecha_hoy} {registro.hora_entrada}", "%Y-%m-%d %H:%M:%S")
            salida = datetime.strptime(f"{fecha_hoy} {registro.hora_salida}", "%Y-%m-%d %H:%M:%S")
            return round((salida - entrada).seconds / 3600, 2)
        return None

    def __str__(self) -> str:
        return f"{self.cedula} - {self.nombre} ({self.cargo})"

    def __repr__(self) -> str:
        return f"Trabajador(cedula='{self.cedula}', nombre='{self.nombre}', cargo='{self.cargo}')"

    def get_horas_por_dia_semana(self, fecha_inicio_semana: str) -> dict:
        inicio = datetime.strptime(fecha_inicio_semana, "%Y-%m-%d").date()
        resultado = {}
        for i in range(7):
            dia = inicio + timedelta(days=i)
            fecha_str = dia.strftime("%Y-%m-%d")
            registro = self.get_registro_por_fecha(fecha_str)
            if registro and registro.hora_salida:
                entrada = datetime.strptime(f"{fecha_str} {registro.hora_entrada}", "%Y-%m-%d %H:%M:%S")
                salida = datetime.strptime(f"{fecha_str} {registro.hora_salida}", "%Y-%m-%d %H:%M:%S")
                horas = round((salida - entrada).seconds / 3600, 2)
                resultado[fecha_str] = horas
            else:
                resultado[fecha_str] = 0
        return resultado

    def contar_faltas(self, año: int = None, incluir_fines_semana: bool = False, hora_limite: str = "18:55") -> int:
        if año is None:
            año = datetime.now().year
        hoy = datetime.now().date()
        hora_limite_dt = datetime.strptime(hora_limite, "%H:%M").time()
        hora_actual = datetime.now().time()

        inicio = datetime(año, 1, 1).date()
        fin = datetime(año, 12, 31).date()
        delta = timedelta(days=1)
        faltas = 0
        current = inicio
        while current <= fin:
            if incluir_fines_semana or current.weekday() < 5:
                fecha_str = current.strftime("%Y-%m-%d")
                registro = self.get_registro_por_fecha(fecha_str)
                if not registro:
                    if current == hoy:
                        if hora_actual >= hora_limite_dt:
                            faltas += 1
                    else:
                        faltas += 1
            current += delta
        return faltas

    def limpiar_expediente(self):
        self.fecha_nacimiento = None
        self.edad = None
        self.direccion = ""
        self.telefono = ""
        self.correo = ""
        self.hijos = 0
        self.contacto_emergencia = {"nombre": "", "parentesco": "", "telefono": ""}
        self.condiciones_medicas = ""
        self.foto_path = ""

    def tiene_expediente(self) -> bool:
        return (self.fecha_nacimiento is not None and self.fecha_nacimiento != "") or \
               self.direccion != "" or self.telefono != "" or self.correo != "" or \
               self.hijos > 0 or \
               self.contacto_emergencia.get("nombre", "") != "" or \
               self.condiciones_medicas != "" or self.foto_path != ""