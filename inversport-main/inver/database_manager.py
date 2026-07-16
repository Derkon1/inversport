# inver/database_manager.py
from typing import Optional, Tuple, List, Dict
from datetime import datetime, timedelta
from .database import (
    TrabajadorDB, RegistroDB, PermisoDB, ProduccionDB, ExpedienteDB, NominaDB
)


class DatabaseManager:
    """Gestiona la sincronización entre la aplicación y la base de datos."""
    
    def __init__(self):
        self.trabajador_db = TrabajadorDB()
        self.registro_db = RegistroDB()
        self.permiso_db = PermisoDB()
        self.produccion_db = ProduccionDB()
        self.expediente_db = ExpedienteDB()
        self.nomina_db = NominaDB()
        
        # Conectar automáticamente
        self.trabajador_db.connect()
        self.registro_db.connect()
        self.permiso_db.connect()
        self.produccion_db.connect()
        self.expediente_db.connect()
        self.nomina_db.connect()

    def guardar_trabajador(self, trabajador) -> bool:
        """Guarda un trabajador en la base de datos."""
        return self.trabajador_db.guardar_trabajador(
            trabajador.cedula,
            trabajador.nombres,
            trabajador.apellidos,
            trabajador.cargo
        )

    def cargar_trabajadores(self, nomina) -> None:
        """Carga todos los trabajadores desde la base de datos a la nómina."""
        # Importar aquí para evitar circular import
        from .models import Trabajador
        
        trabajadores = self.trabajador_db.obtener_todos_trabajadores()
        if not trabajadores:
            return
            
        for t in trabajadores:
            if t['cedula'] in nomina.trabajadores:
                trabajador = nomina.trabajadores[t['cedula']]
                trabajador.nombres = t['nombres']
                trabajador.apellidos = t['apellidos']
                trabajador.cargo = t['cargo']
                trabajador.nombre = f"{t['nombres']} {t['apellidos']}".strip()
            else:
                try:
                    nuevo = Trabajador(t['cedula'], t['nombres'], t['apellidos'], t['cargo'])
                    nomina.trabajadores[t['cedula']] = nuevo
                except ValueError as e:
                    print(f"Error al crear trabajador {t['cedula']}: {e}")

    def cargar_registros(self, nomina) -> None:
        """Carga todos los registros de entrada desde la base de datos."""
        from .models import RegistroEntrada
        
        for cedula, trabajador in nomina.trabajadores.items():
            trabajador.registros_entrada = []
            fecha_hoy = datetime.now().strftime("%Y-%m-%d")
            fecha_inicio = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            registros = self.registro_db.obtener_registros_por_fecha(cedula, fecha_inicio, fecha_hoy)
            
            for r in registros:
                fecha = str(r['fecha'])
                hora_entrada = str(r['hora_entrada'])
                hora_salida = str(r['hora_salida']) if r['hora_salida'] else None
                nuevo_registro = RegistroEntrada(fecha, hora_entrada, hora_salida)
                trabajador.registros_entrada.append(nuevo_registro)

    def cargar_permisos(self, nomina) -> None:
        """Carga todos los permisos desde la base de datos."""
        from .models import Permiso
        
        for cedula, trabajador in nomina.trabajadores.items():
            permisos_db = self.permiso_db.obtener_todos_permisos(cedula)
            trabajador.permisos = []
            for p in permisos_db:
                try:
                    permiso = Permiso(
                        p['tipo'],
                        p['dias'],
                        p['motivo'] or '',
                        str(p['fecha_inicio']),
                        str(p['fecha_fin'])
                    )
                    permiso.id_permiso = p['id_permiso']
                    trabajador.permisos.append(permiso)
                except ValueError as e:
                    print(f"Error al cargar permiso: {e}")

    def cargar_produccion(self, nomina) -> None:
        """Carga toda la producción desde la base de datos."""
        from .models import RegistroProduccion
        
        for cedula, trabajador in nomina.trabajadores.items():
            produccion_db = self.produccion_db.obtener_produccion_por_cedula(cedula)
            nomina.produccion[cedula] = []
            for p in produccion_db:
                try:
                    registro = RegistroProduccion(
                        str(p['fecha']),
                        p['ticket'] or '',
                        p['referencia'] or '',
                        p['color'] or '',
                        p['pares'],
                        int(p['pedido']) if p['pedido'] else 0,
                        float(p['precio'])
                    )
                    registro.id_produccion = p['id_produccion']
                    nomina.produccion[cedula].append(registro)
                except Exception as e:
                    print(f"Error al cargar producción: {e}")

    def guardar_registro(self, cedula: str, fecha: str, hora_entrada: str, hora_salida: str = None) -> bool:
        """Guarda un registro de entrada/salida en la base de datos."""
        return self.registro_db.guardar_registro(cedula, fecha, hora_entrada, hora_salida)

    def guardar_permiso(self, cedula: str, tipo: str, dias: int, 
                        fecha_inicio: str, fecha_fin: str, motivo: str) -> bool:
        """Guarda un permiso en la base de datos."""
        return self.permiso_db.guardar_permiso(cedula, tipo, dias, fecha_inicio, fecha_fin, motivo)

    def modificar_permiso(self, id_permiso: int, tipo: str, dias: int,
                          fecha_inicio: str, fecha_fin: str, motivo: str) -> bool:
        """Modifica un permiso en la base de datos."""
        return self.permiso_db.modificar_permiso(id_permiso, tipo, dias, fecha_inicio, fecha_fin, motivo)

    def eliminar_permiso(self, id_permiso: int) -> bool:
        """Elimina un permiso de la base de datos."""
        return self.permiso_db.eliminar_permiso(id_permiso)

    def guardar_produccion(self, cedula: str, registro) -> Optional[int]:
        """Guarda un registro de producción en la base de datos y retorna el ID."""
        return self.produccion_db.guardar_produccion(
            cedula, registro.fecha, registro.ticket, registro.referencia,
            registro.color, registro.pares, str(registro.pedido), registro.precio
        )

    def eliminar_produccion(self, id_produccion: int) -> bool:
        """Elimina un registro de producción."""
        return self.produccion_db.eliminar_produccion(id_produccion)

    def modificar_produccion(self, id_produccion: int, registro) -> bool:
        """Modifica un registro de producción."""
        return self.produccion_db.modificar_produccion(
            id_produccion, registro.fecha, registro.ticket, registro.referencia,
            registro.color, registro.pares, str(registro.pedido), registro.precio
        )

    def guardar_expediente(self, cedula: str, trabajador) -> bool:
        """Guarda el expediente de un trabajador."""
        tiene_condiciones = trabajador.condiciones_medicas and trabajador.condiciones_medicas.strip() != 'Ninguna'
        return self.expediente_db.guardar_expediente(
            cedula,
            trabajador.fecha_nacimiento,
            trabajador.direccion,
            trabajador.telefono,
            trabajador.correo,
            trabajador.hijos,
            trabajador.contacto_emergencia.get("nombre", ""),
            trabajador.contacto_emergencia.get("parentesco", ""),
            trabajador.contacto_emergencia.get("telefono", ""),
            tiene_condiciones,
            trabajador.condiciones_medicas if tiene_condiciones else "",
            trabajador.foto_path
        )

    def cargar_expediente(self, nomina) -> None:
        """Carga los expedientes de todos los trabajadores."""
        for cedula, trabajador in nomina.trabajadores.items():
            expediente = self.expediente_db.obtener_expediente(cedula)
            if expediente:
                trabajador.fecha_nacimiento = str(expediente['fecha_nacimiento']) if expediente['fecha_nacimiento'] else None
                trabajador.direccion = expediente['direccion'] or ''
                trabajador.telefono = expediente['telefono'] or ''
                trabajador.correo = expediente['correo'] or ''
                trabajador.hijos = expediente['numero_hijos'] or 0
                trabajador.contacto_emergencia = {
                    "nombre": expediente['nombre_emergencia'] or '',
                    "parentesco": expediente['parentesco_emergencia'] or '',
                    "telefono": expediente['telefono_emergencia'] or ''
                }
                trabajador.condiciones_medicas = expediente['descripcion_condiciones'] or ''
                trabajador.foto_path = expediente['foto_path'] or ''
                trabajador.calcular_edad()

    def eliminar_expediente(self, cedula: str) -> bool:
        """Elimina el expediente de un trabajador."""
        return self.expediente_db.eliminar_expediente(cedula)

    def guardar_nomina(self, cedula: str, datos: Dict) -> bool:
        """Guarda un cálculo de nómina."""
        return self.nomina_db.guardar_nomina(
            cedula,
            datos.get('periodo', 'Quincenal'),
            datos.get('fecha_inicio'),
            datos.get('fecha_fin'),
            datos.get('salario_base', 0),
            datos.get('asignacion_produccion', 0),
            datos.get('estaticket', 0),
            datos.get('alicuota_utilidades', 0),
            datos.get('alicuota_bono_vacacional', 0),
            datos.get('total_asignaciones', 0),
            datos.get('deduccion_ivss', 0),
            datos.get('deduccion_faov', 0),
            datos.get('total_deducciones', 0),
            datos.get('neto_pagar', 0),
            datos.get('aporte_ivss_patronal', 0),
            datos.get('aporte_lopcymat', 0),
            datos.get('total_aportes_patronales', 0)
        )

    def eliminar_trabajador_completo(self, cedula: str) -> bool:
        """Elimina un trabajador y todos sus datos relacionados."""
        return self.trabajador_db.eliminar_trabajador(cedula)

    def sincronizar_todo(self, nomina) -> None:
        """Sincroniza todos los datos entre la aplicación y la base de datos."""
        self.cargar_trabajadores(nomina)
        self.cargar_permisos(nomina)
        self.cargar_registros(nomina)
        self.cargar_produccion(nomina)
        self.cargar_expediente(nomina)
        print("✅ Datos sincronizados correctamente")

    def cerrar_conexiones(self) -> None:
        """Cierra todas las conexiones a la base de datos."""
        self.trabajador_db.disconnect()
        self.registro_db.disconnect()
        self.permiso_db.disconnect()
        self.produccion_db.disconnect()
        self.expediente_db.disconnect()
        self.nomina_db.disconnect()