import tkinter as tk
from tkinter import ttk
import re
from datetime import datetime
from ...views.ui_utils import ToolTip


class RegistroView:
    def _mostrar_registro(self):
        self._limpiar_contenido()
        frame = tk.Frame(self.content_area, bg=self.colors['bg_main'])
        frame.pack(fill='both', expand=True)
        self.current_frame = frame

        center = tk.Frame(frame, bg=self.colors['bg_main'])
        center.pack(expand=True)

        card = tk.Frame(center, bg=self.colors['card_bg'], width=650, height=550)
        card.pack(pady=30)
        card.pack_propagate(False)
        card.config(highlightbackground=self.colors['border'], highlightthickness=1)

        header = tk.Frame(card, bg=self.colors['accent'], height=70)
        header.pack(fill='x')
        header.pack_propagate(False)
        tk.Label(header, text="🎯", font=('Segoe UI', 32), bg=self.colors['accent'], fg='white').pack(pady=12)

        tk.Label(card, text="Registro de Entrada / Salida", font=('Segoe UI', 18, 'bold'),
                 bg=self.colors['card_bg'], fg=self.colors['text_light']).pack(pady=12)

        form = tk.Frame(card, bg=self.colors['card_bg'])
        form.pack(padx=30, pady=15, fill='x')

        tk.Label(form, text="📇 Cédula de Identidad", font=('Segoe UI', 9, 'bold'),
                 bg=self.colors['card_bg'], fg=self.colors['text_gray']).pack(anchor='w')
        cedula_frame = tk.Frame(form, bg=self.colors['card_bg'])
        cedula_frame.pack(fill='x', pady=(4, 10))
        self.entry_cedula = tk.Entry(cedula_frame, font=('Segoe UI', 12),
                                     bg=self.colors['input_bg'], fg=self.colors['text_light'],
                                     insertbackground=self.colors['text_light'],
                                     highlightbackground=self.colors['input_border'],
                                     highlightthickness=1, relief='solid',
                                     validate='key', validatecommand=(self.vcmd_numeros, '%P'))
        self.entry_cedula.pack(side='left', fill='x', expand=True, ipady=8)
        self.entry_cedula.bind('<FocusOut>', lambda e: self._validar_cedula(self.entry_cedula, self.label_estado))
        self.entry_cedula.bind('<KeyRelease>', lambda e: (self._validar_cedula(self.entry_cedula, self.label_estado), self.auto_cargar_trabajador()))

        tk.Label(form, text="👤 Nombre del Trabajador", font=('Segoe UI', 9, 'bold'),
                 bg=self.colors['card_bg'], fg=self.colors['text_gray']).pack(anchor='w')
        nombre_frame = tk.Frame(form, bg=self.colors['card_bg'])
        nombre_frame.pack(fill='x', pady=(4, 8))
        self.entry_nombre = ttk.Combobox(nombre_frame, font=('Segoe UI', 12))
        self.entry_nombre.pack(fill='x', expand=True, ipady=8)
        self.entry_nombre.set('')
        self.entry_nombre.bind('<KeyRelease>', self._on_nombre_keyrelease)
        self.entry_nombre.bind('<<ComboboxSelected>>', self._on_nombre_selected)
        self.entry_nombre.bind('<FocusOut>', self._buscar_por_nombre_y_llenar)

        self.label_estado = tk.Label(form, text="", font=('Segoe UI', 10), bg=self.colors['card_bg'])
        self.label_estado.pack(pady=4)

        self.current_mensaje_label = tk.Label(form, text="", font=('Segoe UI', 9), bg=self.colors['card_bg'])
        self.current_mensaje_label.pack(pady=4)

        btn_frame = tk.Frame(card, bg=self.colors['card_bg'])
        btn_frame.pack(pady=20)
        self._crear_boton(btn_frame, "REGISTRAR ENTRADA", self.registrar_entrada, 'success').pack(side='left', padx=8)
        self._crear_boton(btn_frame, "REGISTRAR SALIDA", self.registrar_salida, 'danger').pack(side='left', padx=8)

    def _on_nombre_keyrelease(self, event):
        texto = self.entry_nombre.get()
        if texto and not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', texto):
            self._mostrar_mensaje("Solo se permiten letras y espacios", 'warning', status=True)
        if len(texto) >= 5:
            coincidencias = []
            for cedula, t in self.nomina.trabajadores.items():
                if texto.lower() in t.nombre.lower():
                    coincidencias.append(f"{t.nombre} ({cedula})")
            if coincidencias:
                self.entry_nombre['values'] = coincidencias
                self.entry_nombre.event_generate('<Down>')
            else:
                self.entry_nombre['values'] = []
        else:
            self.entry_nombre['values'] = []

    def _buscar_por_nombre_y_llenar(self, event=None):
        nombre_buscar = self.entry_nombre.get().strip()
        if not nombre_buscar:
            return
        if len(nombre_buscar) < 3:
            self.entry_cedula.delete(0, tk.END)
            self.label_estado.config(text="")
            return
        encontrado = None
        for cedula, t in self.nomina.trabajadores.items():
            if t.nombre.lower() == nombre_buscar.lower():
                encontrado = (cedula, t)
                break
        if encontrado:
            cedula, trabajador = encontrado
            self.entry_cedula.delete(0, tk.END)
            self.entry_cedula.insert(0, cedula)
            self.entry_nombre.set(trabajador.nombre)
            self.auto_cargar_trabajador()
        else:
            self.entry_cedula.delete(0, tk.END)
            self.label_estado.config(text="")
            if len(nombre_buscar) >= 3:
                self._mostrar_mensaje(f"No se encontró trabajador con nombre '{nombre_buscar}'", 'warning')

    def _on_nombre_selected(self, event):
        seleccion = self.entry_nombre.get()
        if '(' in seleccion and ')' in seleccion:
            cedula = seleccion.split('(')[-1].replace(')', '').strip()
            if cedula.isdigit():
                self.entry_cedula.delete(0, tk.END)
                self.entry_cedula.insert(0, cedula)
                self.auto_cargar_trabajador()

    def auto_cargar_trabajador(self, event=None):
        cedula = self.entry_cedula.get().strip()
        if not cedula:
            self.entry_nombre.set('')
            self.label_estado.config(text="")
            return
        if not cedula.isdigit():
            self.entry_nombre.set('')
            self.label_estado.config(text="La cédula solo debe contener números", fg=self.colors['error'])
            return
        trabajador = self.nomina.trabajadores.get(cedula)
        if not trabajador:
            self.entry_nombre.set('')
            self.label_estado.config(text="TRABAJADOR NO ENCONTRADO", fg=self.colors['error'])
            return
        estado, tipo = trabajador.get_estado_hoy()
        colores_estado = {'success': self.colors['success'], 'warning': self.colors['warning'],
                          'error': self.colors['error'], 'info': self.colors['info']}
        estado_formateado = self._formatear_estado_con_hora(estado)
        self.entry_nombre.set(trabajador.nombre)
        self.label_estado.config(text=estado_formateado, fg=colores_estado.get(tipo, self.colors['text_gray']))

    def registrar_entrada(self):
        cedula = self.entry_cedula.get().strip()
        if not cedula:
            self._mostrar_mensaje("Ingrese una cédula", 'warning')
            return
        if not cedula.isdigit():
            self._mostrar_mensaje("La cédula solo debe contener números", 'error')
            self.label_estado.config(text="Cédula inválida", fg=self.colors['error'])
            return
        resultado, mensaje = self.nomina.registrar_entrada(cedula)
        if resultado:
            import re
            def reemplazo_hora(match):
                return self._formato_hora_12h(match.group(1))
            mensaje_formateado = re.sub(r'a las (\d{2}:\d{2}:\d{2})', lambda m: f"a las {self._formato_hora_12h(m.group(1))}", mensaje)
            self._mostrar_mensaje(mensaje_formateado, 'success')
        else:
            self._mostrar_mensaje(mensaje, 'error')
        if resultado:
            self.entry_cedula.delete(0, tk.END)
            self.entry_nombre.set('')
            self.label_estado.config(text="")
            if hasattr(self, 'actualizar_lista_activos'):
                self.actualizar_lista_activos()

    def registrar_salida(self):
        cedula = self.entry_cedula.get().strip()
        if not cedula:
            self._mostrar_mensaje("Ingrese una cédula", 'warning')
            return
        if not cedula.isdigit():
            self._mostrar_mensaje("La cédula solo debe contener números", 'error')
            self.label_estado.config(text="Cédula inválida", fg=self.colors['error'])
            return
        resultado, mensaje = self.nomina.registrar_salida(cedula)
        if resultado:
            import re
            mensaje_formateado = re.sub(r'a las (\d{2}:\d{2}:\d{2})', lambda m: f"a las {self._formato_hora_12h(m.group(1))}", mensaje)
            self._mostrar_mensaje(mensaje_formateado, 'success')
        else:
            self._mostrar_mensaje(mensaje, 'error')
        if resultado:
            self.entry_cedula.delete(0, tk.END)
            self.entry_nombre.set('')
            self.label_estado.config(text="")
            if hasattr(self, 'actualizar_lista_activos'):
                self.actualizar_lista_activos()