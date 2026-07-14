# inver/views/components/trabajadores.py
import tkinter as tk
from tkinter import ttk, messagebox
from ...models import Trabajador


class TrabajadoresView:
    def _mostrar_agregar_trabajador(self):
        self._limpiar_contenido()
        frame = tk.Frame(self.content_area, bg=self.colors['bg_main'])
        frame.pack(fill='both', expand=True)
        self.current_frame = frame

        center = tk.Frame(frame, bg=self.colors['bg_main'])
        center.pack(expand=True)

        card = tk.Frame(center, bg=self.colors['card_bg'], width=650, height=580)
        card.pack(pady=30)
        card.pack_propagate(False)
        card.config(highlightbackground=self.colors['border'], highlightthickness=1)

        header = tk.Frame(card, bg=self.colors['success'], height=70)
        header.pack(fill='x')
        header.pack_propagate(False)
        tk.Label(header, text="👤", font=('Segoe UI', 32), bg=self.colors['success'], fg='white').pack(pady=12)

        tk.Label(card, text="Registrar Nuevo Trabajador", font=('Segoe UI', 18, 'bold'),
                 bg=self.colors['card_bg'], fg=self.colors['text_light']).pack(pady=12)

        form = tk.Frame(card, bg=self.colors['card_bg'])
        form.pack(padx=30, pady=15, fill='x')

        tk.Label(form, text="📇 Cédula de Identidad", font=('Segoe UI', 9, 'bold'),
                 bg=self.colors['card_bg'], fg=self.colors['text_gray']).pack(anchor='w', pady=(0,4))
        self.entry_cedula_nueva = tk.Entry(form, font=('Segoe UI', 10),
                                           bg=self.colors['input_bg'], fg=self.colors['text_light'],
                                           insertbackground=self.colors['text_light'],
                                           validate='key', validatecommand=(self.vcmd_numeros, '%P'))
        self.entry_cedula_nueva.pack(fill='x', pady=(0,8), ipady=6)
        self.entry_cedula_nueva.bind('<FocusOut>', lambda e: self._validar_cedula(self.entry_cedula_nueva, self.current_mensaje_label))
        self.entry_cedula_nueva.bind('<KeyRelease>', lambda e: self._validar_cedula(self.entry_cedula_nueva, self.current_mensaje_label))

        tk.Label(form, text="📝 Nombres", font=('Segoe UI', 9, 'bold'),
                 bg=self.colors['card_bg'], fg=self.colors['text_gray']).pack(anchor='w', pady=(0,4))
        self.entry_nombres_nuevo = tk.Entry(form, font=('Segoe UI', 10),
                                            bg=self.colors['input_bg'], fg=self.colors['text_light'],
                                            insertbackground=self.colors['text_light'],
                                            validate='key', validatecommand=(self.vcmd_letras, '%P'))
        self.entry_nombres_nuevo.pack(fill='x', pady=(0,8), ipady=6)
        self.entry_nombres_nuevo.bind('<FocusOut>', lambda e: self._validar_nombres(self.entry_nombres_nuevo, self.current_mensaje_label))
        self.entry_nombres_nuevo.bind('<KeyRelease>', lambda e: self._validar_nombres(self.entry_nombres_nuevo, self.current_mensaje_label))

        tk.Label(form, text="📝 Apellidos", font=('Segoe UI', 9, 'bold'),
                 bg=self.colors['card_bg'], fg=self.colors['text_gray']).pack(anchor='w', pady=(0,4))
        self.entry_apellidos_nuevo = tk.Entry(form, font=('Segoe UI', 10),
                                              bg=self.colors['input_bg'], fg=self.colors['text_light'],
                                              insertbackground=self.colors['text_light'],
                                              validate='key', validatecommand=(self.vcmd_letras, '%P'))
        self.entry_apellidos_nuevo.pack(fill='x', pady=(0,8), ipady=6)
        self.entry_apellidos_nuevo.bind('<FocusOut>', lambda e: self._validar_apellidos(self.entry_apellidos_nuevo, self.current_mensaje_label))
        self.entry_apellidos_nuevo.bind('<KeyRelease>', lambda e: self._validar_apellidos(self.entry_apellidos_nuevo, self.current_mensaje_label))

        tk.Label(form, text="💼 Cargo", font=('Segoe UI', 9, 'bold'),
                 bg=self.colors['card_bg'], fg=self.colors['text_gray']).pack(anchor='w', pady=(0,4))
        self.combo_cargo_nuevo = ttk.Combobox(form, values=Trabajador.CARGOS_VALIDOS, font=('Segoe UI', 10), state='readonly')
        self.combo_cargo_nuevo.pack(fill='x', pady=(0,14), ipady=6)

        self.current_mensaje_label = tk.Label(form, text="", font=('Segoe UI', 9), bg=self.colors['card_bg'])
        self.current_mensaje_label.pack(pady=4)

        self._crear_boton(form, "AGREGAR TRABAJADOR", self.agregar_trabajador, 'success').pack(fill='x', pady=(12,4))

    def agregar_trabajador(self):
        cedula = self.entry_cedula_nueva.get().strip()
        nombres = self.entry_nombres_nuevo.get().strip()
        apellidos = self.entry_apellidos_nuevo.get().strip()
        cargo = self.combo_cargo_nuevo.get().strip()

        if not cedula or not nombres or not apellidos or not cargo:
            self._mostrar_mensaje("⚠️ Complete todos los campos", 'warning')
            return
        if not cedula.isdigit():
            self._mostrar_mensaje("La cédula solo debe contener números", 'error')
            self.current_mensaje_label.config(text="❌ Cédula inválida", fg=self.colors['error'])
            return
        if not self._validar_nombres(self.entry_nombres_nuevo, self.current_mensaje_label):
            return
        if not self._validar_apellidos(self.entry_apellidos_nuevo, self.current_mensaje_label):
            return

        resultado, mensaje = self.nomina.agregar_trabajador(cedula, nombres, apellidos, cargo)
        self._mostrar_mensaje(mensaje, 'success' if resultado else 'error')
        if resultado:
            self.entry_cedula_nueva.delete(0, tk.END)
            self.entry_nombres_nuevo.delete(0, tk.END)
            self.entry_apellidos_nuevo.delete(0, tk.END)
            self.combo_cargo_nuevo.set('')
            self._actualizar_listas_combos()
            if hasattr(self, 'actualizar_lista_activos'):
                self.actualizar_lista_activos()

    def _mostrar_actualizar_cargo(self):
        self._limpiar_contenido()
        frame = tk.Frame(self.content_area, bg=self.colors['bg_main'])
        frame.pack(fill='both', expand=True)
        self.current_frame = frame
        self.current_mensaje_label = None

        center = tk.Frame(frame, bg=self.colors['bg_main'])
        center.pack(expand=True)
        card = tk.LabelFrame(center, text="⚙️ Gestión de Cargos", font=('Segoe UI', 12, 'bold'),
                             bg=self.colors['card_bg'], fg=self.colors['accent'], bd=2, relief='groove')
        card.pack(pady=30, padx=30, fill='x')
        form = tk.Frame(card, bg=self.colors['card_bg'])
        form.pack(padx=20, pady=15, fill='x')
        tk.Label(form, text="👤 Seleccionar Trabajador", font=('Segoe UI', 9, 'bold'),
                 bg=self.colors['card_bg'], fg=self.colors['text_gray']).pack(anchor='w', pady=(0,4))
        self.combo_actualizar_cargo = ttk.Combobox(form, font=('Segoe UI', 10), width=50)
        self.combo_actualizar_cargo.pack(fill='x', pady=(0,14), ipady=6)
        self.combo_actualizar_cargo.bind('<<ComboboxSelected>>', self._mostrar_cargo_actual)
        self.label_cargo_actual = tk.Label(form, text="", font=('Segoe UI', 9, 'italic'),
                                           bg=self.colors['card_bg'], fg=self.colors['text_gray'])
        self.label_cargo_actual.pack(anchor='w', pady=(0,8))
        tk.Label(form, text="💼 Nuevo Cargo", font=('Segoe UI', 9, 'bold'),
                 bg=self.colors['card_bg'], fg=self.colors['text_gray']).pack(anchor='w', pady=(0,4))
        self.combo_nuevo_cargo = ttk.Combobox(form, values=Trabajador.CARGOS_VALIDOS, font=('Segoe UI', 10), width=50, state='readonly')
        self.combo_nuevo_cargo.pack(fill='x', pady=(0,14), ipady=6)
        self.current_mensaje_label = tk.Label(form, text="", font=('Segoe UI', 9), bg=self.colors['card_bg'])
        self.current_mensaje_label.pack(pady=4)
        btn_frame = tk.Frame(form, bg=self.colors['card_bg'])
        btn_frame.pack(pady=8)
        self._crear_boton(btn_frame, "ACTUALIZAR CARGO", self.actualizar_cargo_func, 'info').pack(side='left', padx=4)
        self._crear_boton(btn_frame, "ELIMINAR TRABAJADOR", self.eliminar_trabajador_func, 'danger').pack(side='left', padx=4)
        self._actualizar_listas_combos()

    def _mostrar_cargo_actual(self, event=None):
        seleccion = self.combo_actualizar_cargo.get()
        if seleccion:
            cedula = seleccion.split(" - ")[0]
            t = self.nomina.trabajadores.get(cedula)
            if t:
                self.label_cargo_actual.config(text=f"Cargo actual: {t.cargo}")

    def actualizar_cargo_func(self):
        seleccion = self.combo_actualizar_cargo.get()
        nuevo_cargo = self.combo_nuevo_cargo.get().strip()
        if not seleccion or not nuevo_cargo:
            self._mostrar_mensaje("⚠️ Complete todos los campos", 'warning')
            return
        cedula = seleccion.split(" - ")[0]
        trabajador = self.nomina.trabajadores.get(cedula)
        if not trabajador:
            self._mostrar_mensaje("Trabajador no encontrado", 'error')
            return
        if trabajador.cargo == nuevo_cargo:
            self._mostrar_mensaje(f"El trabajador ya posee el cargo '{nuevo_cargo}'", 'warning')
            return
        resultado, mensaje = self.nomina.actualizar_cargo(cedula, nuevo_cargo)
        self._mostrar_mensaje(mensaje, 'success' if resultado else 'error')
        if resultado:
            self.combo_actualizar_cargo.set('')
            self.combo_nuevo_cargo.set('')
            self.label_cargo_actual.config(text="")
            self._actualizar_listas_combos()
            if hasattr(self, 'actualizar_lista_activos'):
                self.actualizar_lista_activos()

    def eliminar_trabajador_func(self):
        seleccion = self.combo_actualizar_cargo.get()
        if not seleccion:
            self._mostrar_mensaje("⚠️ Seleccione un trabajador", 'warning')
            return
        cedula = seleccion.split(" - ")[0]
        nombre = seleccion.split(" - ")[1]
        if messagebox.askyesno("Confirmar", f"¿Eliminar a {nombre}? Se borrarán todos sus registros."):
            resultado, mensaje = self.nomina.eliminar_trabajador(cedula)
            self._mostrar_mensaje(mensaje, 'success' if resultado else 'error')
            if resultado:
                self.combo_actualizar_cargo.set('')
                self.combo_nuevo_cargo.set('')
                self.label_cargo_actual.config(text="")
                self._actualizar_listas_combos()
                if hasattr(self, 'actualizar_lista_activos'):
                    self.actualizar_lista_activos()