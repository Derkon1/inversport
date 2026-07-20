import tkinter as tk
from tkinter import ttk
import re
from datetime import datetime
from ..views.ui_utils import crear_boton, darken_color
from ..utils.utils import formato_cop, parsear_cop


class BaseView:

    def __init__(self):
        pass

    def _limpiar_contenido(self):
        if self.current_frame:
            self.current_frame.destroy()
        self.current_mensaje_label = None

    def _crear_boton(self, parent, texto, comando, tipo='primary'):
        return crear_boton(parent, texto, comando, tipo, self.colors)

    def _darken_color(self, hex_color):
        return darken_color(hex_color)

    def _mostrar_mensaje(self, mensaje, tipo='info', status=True):
        colores = {'success': self.colors['success'], 'error': self.colors['error'],
                   'warning': self.colors['warning'], 'info': self.colors['info']}
        if status:
            self.status_msg.config(text=mensaje, fg=colores.get(tipo, self.colors['info']))
            if self.mensaje_timer:
                self.root.after_cancel(self.mensaje_timer)
            self.mensaje_timer = self.root.after(4000, lambda: self.status_msg.config(text=""))
        if self.current_mensaje_label and self.current_mensaje_label.winfo_exists():
            self.current_mensaje_label.config(text=mensaje, fg=colores.get(tipo, self.colors['info']))

    def _validar_solo_numeros(self, nuevo_valor):
        return nuevo_valor == "" or nuevo_valor.isdigit()

    def _validar_solo_letras(self, nuevo_valor):
        return nuevo_valor == "" or all(c.isalpha() or c.isspace() for c in nuevo_valor)

    def _validar_fecha(self, nuevo_valor):
        return nuevo_valor == "" or all(c.isdigit() or c in '-/' for c in nuevo_valor)

    def _validar_decimal(self, nuevo_valor):
        if nuevo_valor == "":
            return True
        if nuevo_valor.count('.') > 1:
            return False
        return all(c.isdigit() or c == '.' for c in nuevo_valor)

    def _validar_cedula(self, entry, label_estado=None):
        cedula = entry.get().strip()
        if cedula and not cedula.isdigit():
            if label_estado:
                label_estado.config(text="La cédula solo debe contener números", fg=self.colors['error'])
            else:
                self._mostrar_mensaje("La cédula solo debe contener números", 'error')
            return False
        if label_estado:
            label_estado.config(text="")
        return True

    def _validar_nombres(self, entry, label_estado=None):
        valor = entry.get().strip()
        if valor and not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', valor):
            if label_estado:
                label_estado.config(text="Solo se permiten letras y espacios", fg=self.colors['error'])
            else:
                self._mostrar_mensaje("Solo se permiten letras y espacios", 'error')
            return False
        if label_estado:
            label_estado.config(text="")
        return True

    def _validar_apellidos(self, entry, label_estado=None):
        valor = entry.get().strip()
        if valor and not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', valor):
            if label_estado:
                label_estado.config(text="Solo se permiten letras y espacios", fg=self.colors['error'])
            else:
                self._mostrar_mensaje("Solo se permiten letras y espacios", 'error')
            return False
        if label_estado:
            label_estado.config(text="")
        return True

    def _validar_motivo(self, entry, label_estado=None):
        motivo = entry.get().strip()
        if motivo and not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', motivo):
            if label_estado:
                label_estado.config(text="El motivo solo puede contener letras y espacios", fg=self.colors['error'])
            else:
                self._mostrar_mensaje("El motivo solo puede contener letras y espacios", 'error')
            return False
        if label_estado:
            label_estado.config(text="")
        return True

    def _validar_numero_entero(self, entry, campo):
        valor = entry.get().strip()
        if valor and not valor.isdigit():
            self._mostrar_mensaje(f"El campo '{campo}' debe ser un número entero", 'warning')
            return False
        return True

    def _validar_numero_decimal(self, entry, campo):
        valor = entry.get().strip()
        if valor:
            try:
                float(valor)
            except ValueError:
                self._mostrar_mensaje(f"El campo '{campo}' debe ser un número (puede usar punto decimal)", 'warning')
                return False
        return True

    def _formato_hora_12h(self, hora_str: str) -> str:
        try:
            dt = datetime.strptime(hora_str, "%H:%M:%S")
            return dt.strftime("%I:%M:%S %p")
        except ValueError:
            try:
                dt = datetime.strptime(hora_str, "%H:%M")
                return dt.strftime("%I:%M %p")
            except ValueError:
                return hora_str

    def _formatear_estado_con_hora(self, estado: str) -> str:
        import re
        def reemplazo(match):
            return self._formato_hora_12h(match.group(0))
        return re.sub(r'\b\d{2}:\d{2}(:\d{2})?\b', reemplazo, estado)

    def _formato_cop(self, valor):
        return formato_cop(valor)

    def _parsear_cop(self, texto):
        return parsear_cop(texto)

    def _actualizar_listas_combos(self):
        valores = [f"{cedula} - {nombre}" for cedula, nombre in self.nomina.get_trabajadores_lista()]
        combos = ['combo_permiso_trabajador', 'combo_historial', 'combo_actualizar_cargo',
                  'combo_nomina_trabajador', 'combo_expediente']
        for combo in combos:
            if hasattr(self, combo) and getattr(self, combo).winfo_exists():
                getattr(self, combo)['values'] = valores
        if hasattr(self, 'combo_nomina_trabajador') and self.combo_nomina_trabajador.winfo_exists():
            self._cargar_produccion_trabajador()