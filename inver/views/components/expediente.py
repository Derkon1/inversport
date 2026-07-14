# inver/views/components/expediente.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from datetime import datetime
import re


class ExpedienteView:
    def _mostrar_expediente(self):
        self._limpiar_contenido()
        frame = tk.Frame(self.content_area, bg=self.colors['bg_main'])
        frame.pack(fill='both', expand=True)
        self.current_frame = frame

        header = tk.Frame(frame, bg=self.colors['card_bg'], height=50)
        header.pack(fill='x', padx=12, pady=8)
        header.pack_propagate(False)
        header.config(highlightbackground=self.colors['border'], highlightthickness=1)
        header_inner = tk.Frame(header, bg=self.colors['card_bg'])
        header_inner.place(relx=0.5, rely=0.5, anchor='center')
        tk.Label(header_inner, text="📁", font=('Segoe UI', 20), bg=self.colors['card_bg'], fg='white').pack(side='left', padx=(0,4))
        tk.Label(header_inner, text="Expediente de Trabajadores", font=('Segoe UI', 14, 'bold'),
                 bg=self.colors['card_bg'], fg='white').pack(side='left')

        main_panel = tk.Frame(frame, bg=self.colors['bg_main'])
        main_panel.pack(fill='both', expand=True, padx=12, pady=4)

        sel_frame = tk.Frame(main_panel, bg=self.colors['card_bg'])
        sel_frame.pack(fill='x', pady=(0,8))
        sel_frame.config(highlightbackground=self.colors['border'], highlightthickness=1)

        tk.Label(sel_frame, text="👤 Seleccionar trabajador:", font=('Segoe UI', 8, 'bold'),
                 bg=self.colors['card_bg'], fg=self.colors['text_light']).pack(side='left', padx=6, pady=3)

        self.combo_expediente = ttk.Combobox(sel_frame, font=('Segoe UI', 9), width=35)
        self.combo_expediente.pack(side='left', padx=4, pady=3)
        self.combo_expediente.bind('<<ComboboxSelected>>', self._on_expediente_selected)

        self.label_exp_estado = tk.Label(sel_frame, text="", font=('Segoe UI', 8, 'bold'),
                                         bg=self.colors['card_bg'], fg=self.colors['text_gray'])
        self.label_exp_estado.pack(side='left', padx=8, pady=3)

        card_exp = tk.Frame(main_panel, bg=self.colors['card_bg'], relief='ridge', bd=2)
        card_exp.pack(fill='both', expand=True, padx=12, pady=4)
        card_exp.config(highlightbackground=self.colors['border'], highlightthickness=1)

        panel_izquierda = tk.Frame(card_exp, bg=self.colors['card_bg'])
        panel_izquierda.pack(side='left', fill='both', expand=True, padx=6, pady=6)

        foto_frame = tk.Frame(panel_izquierda, bg=self.colors['card_bg'])
        foto_frame.pack(pady=6, padx=8, anchor='center')

        self.foto_canvas = tk.Canvas(foto_frame, width=110, height=110,
                                     bg=self.colors['input_bg'], highlightthickness=1,
                                     highlightbackground=self.colors['border'])
        self.foto_canvas.pack(side='top', pady=(0, 4))
        self.foto_canvas.create_text(55, 55, text="Sin foto", fill=self.colors['text_gray'], font=('Segoe UI', 9))

        info_frame = tk.Frame(foto_frame, bg=self.colors['card_bg'])
        info_frame.pack(side='top', fill='x', pady=(4, 2))

        self.label_exp_nombres = tk.Label(info_frame, text="", font=('Segoe UI', 12, 'bold'),
                                          bg=self.colors['card_bg'], fg=self.colors['text_light'])
        self.label_exp_nombres.pack(anchor='center')

        self.label_exp_apellidos = tk.Label(info_frame, text="", font=('Segoe UI', 12, 'bold'),
                                            bg=self.colors['card_bg'], fg=self.colors['text_light'])
        self.label_exp_apellidos.pack(anchor='center')

        self.label_exp_cedula_cargo = tk.Label(panel_izquierda, text="", font=('Segoe UI', 9),
                                               bg=self.colors['card_bg'], fg=self.colors['text_gray'])
        self.label_exp_cedula_cargo.pack(anchor='center', pady=(0, 4))

        btn_frame_foto = tk.Frame(panel_izquierda, bg=self.colors['card_bg'])
        btn_frame_foto.pack(pady=(4, 6))
        self._crear_boton(btn_frame_foto, "Cargar foto", self._cargar_foto_expediente, 'info').pack(anchor='center')

        self.label_exp_foto_path = tk.Label(panel_izquierda, text="", font=('Segoe UI', 7),
                                            bg=self.colors['card_bg'], fg=self.colors['text_gray'])
        self.label_exp_foto_path.pack(anchor='center', pady=(0, 6))

        form_frame = tk.Frame(panel_izquierda, bg=self.colors['card_bg'])
        form_frame.pack(fill='x', pady=6)

        label_width = 120
        form_frame.columnconfigure(0, weight=0, minsize=label_width)
        form_frame.columnconfigure(1, weight=1, minsize=180)
        entry_width = 22

        tk.Label(form_frame, text="Fecha nacimiento:", font=('Segoe UI', 8, 'bold'),
                 bg=self.colors['card_bg'], fg=self.colors['text_gray'], anchor='e', justify='right').grid(row=0, column=0, sticky='e', pady=2, padx=(0,6))
        date_frame = tk.Frame(form_frame, bg=self.colors['card_bg'])
        date_frame.grid(row=0, column=1, sticky='ew', pady=2)
        date_frame.columnconfigure(0, weight=1)
        self.entry_exp_fecha_nac = tk.Entry(date_frame, width=entry_width, font=('Segoe UI', 8),
                                            bg=self.colors['input_bg'], fg=self.colors['text_light'],
                                            insertbackground=self.colors['text_light'],
                                            state='readonly', readonlybackground=self.colors['input_bg'])
        self.entry_exp_fecha_nac.grid(row=0, column=0, sticky='ew', padx=(0,3))
        tk.Button(date_frame, text='📅', width=6, height=1, command=lambda: self._abrir_calendario(self.entry_exp_fecha_nac),
                  bg=self.colors['accent'], fg='white', relief='flat', font=('Segoe UI', 7),
                  anchor='center', justify='center').grid(row=0, column=1, sticky='e')

        tk.Label(form_frame, text="Edad:", font=('Segoe UI', 8, 'bold'),
                 bg=self.colors['card_bg'], fg=self.colors['text_gray'], anchor='e', justify='right').grid(row=1, column=0, sticky='e', pady=2, padx=(0,6))
        self.entry_exp_edad = tk.Entry(form_frame, width=entry_width, font=('Segoe UI', 8, 'bold'),
                                       bg=self.colors['input_bg'], fg=self.colors['accent'],
                                       insertbackground=self.colors['text_light'], state='readonly',
                                       readonlybackground=self.colors['input_bg'])
        self.entry_exp_edad.grid(row=1, column=1, sticky='ew', pady=2)

        tk.Label(form_frame, text="Dirección:", font=('Segoe UI', 8, 'bold'),
                 bg=self.colors['card_bg'], fg=self.colors['text_gray'], anchor='e', justify='right').grid(row=2, column=0, sticky='e', pady=2, padx=(0,6))
        self.entry_exp_direccion = tk.Entry(form_frame, width=entry_width, font=('Segoe UI', 8),
                                            bg=self.colors['input_bg'], fg=self.colors['text_light'],
                                            insertbackground=self.colors['text_light'])
        self.entry_exp_direccion.grid(row=2, column=1, sticky='ew', pady=2)

        tk.Label(form_frame, text="Teléfono:", font=('Segoe UI', 8, 'bold'),
                 bg=self.colors['card_bg'], fg=self.colors['text_gray'], anchor='e', justify='right').grid(row=3, column=0, sticky='e', pady=2, padx=(0,6))
        self.entry_exp_telefono = tk.Entry(form_frame, width=entry_width, font=('Segoe UI', 8),
                                           bg=self.colors['input_bg'], fg=self.colors['text_light'],
                                           insertbackground=self.colors['text_light'],
                                           validate='key', validatecommand=(self.vcmd_numeros, '%P'))
        self.entry_exp_telefono.grid(row=3, column=1, sticky='ew', pady=2)

        tk.Label(form_frame, text="Correo electrónico:", font=('Segoe UI', 8, 'bold'),
                 bg=self.colors['card_bg'], fg=self.colors['text_gray'], anchor='e', justify='right').grid(row=4, column=0, sticky='e', pady=2, padx=(0,6))
        self.entry_exp_correo = tk.Entry(form_frame, width=entry_width, font=('Segoe UI', 8),
                                         bg=self.colors['input_bg'], fg=self.colors['text_light'],
                                         insertbackground=self.colors['text_light'])
        self.entry_exp_correo.grid(row=4, column=1, sticky='ew', pady=2)

        tk.Label(form_frame, text="Número de hijos:", font=('Segoe UI', 8, 'bold'),
                 bg=self.colors['card_bg'], fg=self.colors['text_gray'], anchor='e', justify='right').grid(row=5, column=0, sticky='e', pady=2, padx=(0,6))
        self.entry_exp_hijos = tk.Entry(form_frame, width=entry_width, font=('Segoe UI', 8),
                                        bg=self.colors['input_bg'], fg=self.colors['text_light'],
                                        insertbackground=self.colors['text_light'],
                                        validate='key', validatecommand=(self.vcmd_numeros, '%P'))
        self.entry_exp_hijos.grid(row=5, column=1, sticky='ew', pady=2)

        panel_derecha = tk.Frame(card_exp, bg=self.colors['card_bg'], relief='groove', bd=2)
        panel_derecha.pack(side='right', fill='both', expand=True, padx=6, pady=6)
        panel_derecha.config(highlightbackground=self.colors['border'], highlightthickness=1)

        tk.Label(panel_derecha, text="Datos de emergencia y salud", font=('Segoe UI', 10, 'bold'),
                 bg=self.colors['card_bg'], fg=self.colors['accent']).pack(anchor='w', padx=8, pady=(6, 4))

        emerg_frame = tk.Frame(panel_derecha, bg=self.colors['card_bg'])
        emerg_frame.pack(fill='x', padx=8, pady=4)

        emerg_frame.columnconfigure(0, weight=0, minsize=100)
        emerg_frame.columnconfigure(1, weight=1, minsize=160)

        tk.Label(emerg_frame, text="Nombre:", font=('Segoe UI', 8, 'bold'),
                 bg=self.colors['card_bg'], fg=self.colors['text_gray'], anchor='e', justify='right').grid(row=0, column=0, sticky='e', pady=1, padx=(0,6))
        self.entry_exp_emerg_nombre = tk.Entry(emerg_frame, width=entry_width, font=('Segoe UI', 8),
                                               bg=self.colors['input_bg'], fg=self.colors['text_light'],
                                               insertbackground=self.colors['text_light'],
                                               validate='key', validatecommand=(self.vcmd_letras, '%P'))
        self.entry_exp_emerg_nombre.grid(row=0, column=1, sticky='ew', pady=1)

        tk.Label(emerg_frame, text="Parentesco:", font=('Segoe UI', 8, 'bold'),
                 bg=self.colors['card_bg'], fg=self.colors['text_gray'], anchor='e', justify='right').grid(row=1, column=0, sticky='e', pady=1, padx=(0,6))
        self.entry_exp_emerg_parentesco = tk.Entry(emerg_frame, width=entry_width, font=('Segoe UI', 8),
                                                   bg=self.colors['input_bg'], fg=self.colors['text_light'],
                                                   insertbackground=self.colors['text_light'],
                                                   validate='key', validatecommand=(self.vcmd_letras, '%P'))
        self.entry_exp_emerg_parentesco.grid(row=1, column=1, sticky='ew', pady=1)

        tk.Label(emerg_frame, text="Teléfono:", font=('Segoe UI', 8, 'bold'),
                 bg=self.colors['card_bg'], fg=self.colors['text_gray'], anchor='e', justify='right').grid(row=2, column=0, sticky='e', pady=1, padx=(0,6))
        self.entry_exp_emerg_telefono = tk.Entry(emerg_frame, width=entry_width, font=('Segoe UI', 8),
                                                 bg=self.colors['input_bg'], fg=self.colors['text_light'],
                                                 insertbackground=self.colors['text_light'],
                                                 validate='key', validatecommand=(self.vcmd_numeros, '%P'))
        self.entry_exp_emerg_telefono.grid(row=2, column=1, sticky='ew', pady=1)

        tk.Label(panel_derecha, text="Condiciones médicas / Alergias", font=('Segoe UI', 9, 'bold'),
                 bg=self.colors['card_bg'], fg=self.colors['text_gray']).pack(anchor='w', padx=8, pady=(6, 2))

        self.var_exp_condiciones = tk.StringVar(value='si')
        opt_frame = tk.Frame(panel_derecha, bg=self.colors['card_bg'])
        opt_frame.pack(anchor='w', padx=8, pady=(1, 3))

        tk.Radiobutton(opt_frame, text="Sí, tengo alergias o condiciones médicas",
                       variable=self.var_exp_condiciones, value='si',
                       bg=self.colors['card_bg'], fg=self.colors['text_light'],
                       selectcolor=self.colors['input_bg'], activebackground=self.colors['card_bg'],
                       command=self._actualizar_estado_condiciones).pack(anchor='w')
        tk.Radiobutton(opt_frame, text="No, no tengo alergias ni condiciones",
                       variable=self.var_exp_condiciones, value='no',
                       bg=self.colors['card_bg'], fg=self.colors['text_light'],
                       selectcolor=self.colors['input_bg'], activebackground=self.colors['card_bg'],
                       command=self._actualizar_estado_condiciones).pack(anchor='w')

        self.entry_exp_condiciones_container = tk.Frame(panel_derecha, bg=self.colors['card_bg'])
        self.entry_exp_condiciones_container.pack(fill='x', padx=8, pady=(0, 4))

        self.entry_exp_condiciones = tk.Text(self.entry_exp_condiciones_container, height=3, width=30, font=('Segoe UI', 8),
                                             bg=self.colors['input_bg'], fg=self.colors['text_light'],
                                             insertbackground=self.colors['text_light'], wrap='word',
                                             state='disabled')
        self.entry_exp_condiciones.pack(fill='both', expand=True)
        self._actualizar_estado_condiciones()

        btn_frame = tk.Frame(main_panel, bg=self.colors['bg_main'])
        btn_frame.pack(fill='x', pady=6)

        self._crear_boton(btn_frame, "GUARDAR", self._guardar_expediente, 'success').pack(side='left', padx=3)
        self._crear_boton(btn_frame, "VER", self._ver_expediente_popup, 'info').pack(side='left', padx=3)
        self._crear_boton(btn_frame, "ELIMINAR", self._eliminar_expediente, 'danger').pack(side='left', padx=3)
        self._crear_boton(btn_frame, "LIMPIAR", self._limpiar_formulario_expediente, 'warning').pack(side='left', padx=3)

        self._expediente_cedula_actual = None
        self._actualizar_listas_combos()

    def _actualizar_estado_condiciones(self):
        if self.var_exp_condiciones.get() == 'si':
            self.entry_exp_condiciones_container.pack(fill='x', padx=8, pady=(0,4))
            self.entry_exp_condiciones.config(state='normal')
        else:
            self.entry_exp_condiciones.delete('1.0', tk.END)
            self.entry_exp_condiciones.config(state='disabled')
            self.entry_exp_condiciones_container.pack_forget()

    def _on_expediente_selected(self, event=None):
        seleccion = self.combo_expediente.get()
        if not seleccion:
            return
        cedula = seleccion.split(" - ")[0]
        self._cargar_expediente_por_cedula(cedula)

    def _cargar_expediente_por_cedula(self, cedula):
        trabajador = self.nomina.trabajadores.get(cedula)
        if not trabajador:
            self._mostrar_mensaje("Trabajador no encontrado", 'error')
            return

        self._expediente_cedula_actual = cedula
        self.label_exp_nombres.config(text=trabajador.nombres)
        self.label_exp_apellidos.config(text=trabajador.apellidos)
        self.label_exp_cedula_cargo.config(text=f"Cédula: {cedula}  |  Cargo: {trabajador.cargo}")

        self.entry_exp_fecha_nac.config(state='normal')
        self.entry_exp_fecha_nac.delete(0, tk.END)
        if trabajador.fecha_nacimiento:
            self.entry_exp_fecha_nac.insert(0, trabajador.fecha_nacimiento)
        self.entry_exp_fecha_nac.config(state='readonly')

        self.entry_exp_edad.config(state='normal')
        self.entry_exp_edad.delete(0, tk.END)
        if trabajador.edad:
            self.entry_exp_edad.insert(0, str(trabajador.edad))
        self.entry_exp_edad.config(state='readonly')

        self.entry_exp_direccion.delete(0, tk.END)
        self.entry_exp_direccion.insert(0, trabajador.direccion)

        self.entry_exp_telefono.delete(0, tk.END)
        self.entry_exp_telefono.insert(0, trabajador.telefono)

        self.entry_exp_correo.delete(0, tk.END)
        self.entry_exp_correo.insert(0, trabajador.correo)

        self.entry_exp_hijos.delete(0, tk.END)
        self.entry_exp_hijos.insert(0, str(trabajador.hijos) if trabajador.hijos > 0 else "")

        self.entry_exp_emerg_nombre.delete(0, tk.END)
        self.entry_exp_emerg_nombre.insert(0, trabajador.contacto_emergencia.get("nombre", ""))

        self.entry_exp_emerg_parentesco.delete(0, tk.END)
        self.entry_exp_emerg_parentesco.insert(0, trabajador.contacto_emergencia.get("parentesco", ""))

        self.entry_exp_emerg_telefono.delete(0, tk.END)
        self.entry_exp_emerg_telefono.insert(0, trabajador.contacto_emergencia.get("telefono", ""))

        condiciones_texto = (trabajador.condiciones_medicas or '').strip()
        if condiciones_texto and condiciones_texto.lower() != 'ninguna':
            self.var_exp_condiciones.set('si')
            self.entry_exp_condiciones_container.pack(fill='x', padx=8, pady=(0,4))
            self.entry_exp_condiciones.delete('1.0', tk.END)
            self.entry_exp_condiciones.insert('1.0', condiciones_texto)
            self.entry_exp_condiciones.config(state='normal')
        else:
            self.var_exp_condiciones.set('no')
            self.entry_exp_condiciones.delete('1.0', tk.END)
            self.entry_exp_condiciones.config(state='disabled')
            self.entry_exp_condiciones_container.pack_forget()

        self._mostrar_foto_en_canvas(trabajador.foto_path)

        if trabajador.tiene_expediente():
            self.label_exp_estado.config(text="✅ Expediente completo", fg=self.colors['success'])
        else:
            self.label_exp_estado.config(text="⚠️ Sin expediente", fg=self.colors['warning'])

    def _mostrar_foto_en_canvas(self, foto_path):
        self.foto_canvas.delete("all")
        if foto_path and os.path.exists(foto_path):
            try:
                from PIL import Image, ImageTk
                img = Image.open(foto_path)
                img.thumbnail((110, 110), Image.LANCZOS)
                self.foto_tk = ImageTk.PhotoImage(img)
                self.foto_canvas.create_image(55, 55, image=self.foto_tk, anchor='center')
                self.label_exp_foto_path.config(text=os.path.basename(foto_path))
            except Exception as e:
                self.foto_canvas.create_text(55, 55, text="Sin foto", fill=self.colors['text_gray'], font=('Segoe UI', 9))
                self.label_exp_foto_path.config(text="")
        else:
            self.foto_canvas.create_text(55, 55, text="Sin foto", fill=self.colors['text_gray'], font=('Segoe UI', 9))
            self.label_exp_foto_path.config(text="")

    def _actualizar_edad_expediente(self, event=None):
        """Actualiza la edad del trabajador basada en la fecha de nacimiento."""
        # Verificar que el widget existe
        if not hasattr(self, 'entry_exp_fecha_nac') or not hasattr(self, 'entry_exp_edad'):
            return
            
        try:
            fecha_str = self.entry_exp_fecha_nac.get().strip()
            if not fecha_str:
                return
            nac = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            hoy = datetime.now().date()
            edad = hoy.year - nac.year - ((hoy.month, hoy.day) < (nac.month, nac.day))
            self.entry_exp_edad.config(state='normal')
            self.entry_exp_edad.delete(0, tk.END)
            self.entry_exp_edad.insert(0, str(edad))
            self.entry_exp_edad.config(state='readonly')
        except:
            try:
                self.entry_exp_edad.config(state='normal')
                self.entry_exp_edad.delete(0, tk.END)
                self.entry_exp_edad.config(state='readonly')
            except:
                pass

    def _cargar_foto_expediente(self):
        if not self._expediente_cedula_actual:
            self._mostrar_mensaje("Primero seleccione un trabajador", 'warning')
            return
        trabajador = self.nomina.trabajadores.get(self._expediente_cedula_actual)
        if not trabajador:
            self._mostrar_mensaje("Trabajador no encontrado", 'error')
            return

        ruta = filedialog.askopenfilename(filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp")])
        if ruta:
            try:
                from PIL import Image, ImageTk
                img = Image.open(ruta)
                img.thumbnail((110, 110), Image.LANCZOS)
                self.foto_tk = ImageTk.PhotoImage(img)
                self.foto_canvas.delete("all")
                self.foto_canvas.create_image(55, 55, image=self.foto_tk, anchor='center')
                trabajador.foto_path = ruta
                self.label_exp_foto_path.config(text=os.path.basename(ruta))
                self._mostrar_mensaje("Foto cargada correctamente", 'success')
            except Exception as e:
                self._mostrar_mensaje(f"Error al cargar imagen: {e}", 'error')

    def _guardar_expediente(self):
        if not self._expediente_cedula_actual:
            self._mostrar_mensaje("Primero seleccione un trabajador", 'warning')
            return

        trabajador = self.nomina.trabajadores.get(self._expediente_cedula_actual)
        if not trabajador:
            self._mostrar_mensaje("Trabajador no encontrado", 'error')
            return

        fecha_nac = self.entry_exp_fecha_nac.get().strip()
        direccion = self.entry_exp_direccion.get().strip()
        telefono = self.entry_exp_telefono.get().strip()
        correo = self.entry_exp_correo.get().strip()
        hijos_str = self.entry_exp_hijos.get().strip()
        emerg_nombre = self.entry_exp_emerg_nombre.get().strip()
        emerg_parentesco = self.entry_exp_emerg_parentesco.get().strip()
        emerg_telefono = self.entry_exp_emerg_telefono.get().strip()
        
        if self.var_exp_condiciones.get() == 'si':
            condiciones = self.entry_exp_condiciones.get('1.0', tk.END).strip()
            if not condiciones:
                self._mostrar_mensaje("Describa las condiciones médicas o alergias", 'error')
                return
        else:
            condiciones = 'Ninguna'

        if not fecha_nac:
            self._mostrar_mensaje("La fecha de nacimiento es obligatoria", 'error')
            return
        if not direccion:
            self._mostrar_mensaje("La dirección es obligatoria", 'error')
            return
        if not telefono:
            self._mostrar_mensaje("El teléfono es obligatorio", 'error')
            return
        if not correo:
            self._mostrar_mensaje("El correo electrónico es obligatorio", 'error')
            return
        if not hijos_str:
            self._mostrar_mensaje("El número de hijos es obligatorio (ingrese 0 si no tiene)", 'error')
            return
        if not emerg_nombre:
            self._mostrar_mensaje("El nombre del contacto de emergencia es obligatorio", 'error')
            return
        if not emerg_parentesco:
            self._mostrar_mensaje("El parentesco del contacto de emergencia es obligatorio", 'error')
            return
        if not emerg_telefono:
            self._mostrar_mensaje("El teléfono del contacto de emergencia es obligatorio", 'error')
            return

        try:
            datetime.strptime(fecha_nac, "%Y-%m-%d")
        except ValueError:
            self._mostrar_mensaje("Formato de fecha inválido (YYYY-MM-DD)", 'error')
            return

        if not telefono.isdigit():
            self._mostrar_mensaje("El teléfono solo debe contener números", 'error')
            return
        if not emerg_telefono.isdigit():
            self._mostrar_mensaje("El teléfono de emergencia solo debe contener números", 'error')
            return

        if not hijos_str.isdigit():
            self._mostrar_mensaje("El número de hijos debe ser un número entero", 'error')
            return
        hijos = int(hijos_str)

        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', correo):
            self._mostrar_mensaje("Formato de correo inválido", 'error')
            return
        
        trabajador.fecha_nacimiento = fecha_nac
        trabajador.direccion = direccion
        trabajador.telefono = telefono
        trabajador.correo = correo
        trabajador.hijos = hijos
        trabajador.contacto_emergencia = {
            "nombre": emerg_nombre,
            "parentesco": emerg_parentesco,
            "telefono": emerg_telefono
        }
        trabajador.condiciones_medicas = condiciones
        trabajador.calcular_edad()

        # Guardar en base de datos si está disponible
        if hasattr(self.nomina, 'db_manager') and self.nomina.db_manager:
            if self.nomina.db_manager.guardar_expediente(self._expediente_cedula_actual, trabajador):
                self._mostrar_mensaje(f"Expediente de {trabajador.nombre} guardado correctamente", 'success')
                self.label_exp_estado.config(text="✅ Expediente completo", fg=self.colors['success'])
                self._cargar_expediente_por_cedula(self._expediente_cedula_actual)
            else:
                self._mostrar_mensaje("Error al guardar el expediente en la base de datos", 'error')
        else:
            self._mostrar_mensaje(f"Expediente de {trabajador.nombre} guardado correctamente (sin BD)", 'success')
            self.label_exp_estado.config(text="✅ Expediente completo", fg=self.colors['success'])
            self._cargar_expediente_por_cedula(self._expediente_cedula_actual)

    def _eliminar_expediente(self):
        if not self._expediente_cedula_actual:
            self._mostrar_mensaje("Primero seleccione un trabajador", 'warning')
            return

        trabajador = self.nomina.trabajadores.get(self._expediente_cedula_actual)
        if not trabajador:
            self._mostrar_mensaje("Trabajador no encontrado", 'error')
            return

        if not trabajador.tiene_expediente():
            self._mostrar_mensaje("Este trabajador no tiene expediente", 'warning')
            return

        if not messagebox.askyesno("Confirmar", f"¿Eliminar el expediente de {trabajador.nombre}?"):
            return

        trabajador.limpiar_expediente()
        
        # Eliminar de base de datos si está disponible
        if hasattr(self.nomina, 'db_manager') and self.nomina.db_manager:
            self.nomina.db_manager.eliminar_expediente(self._expediente_cedula_actual)
            
        self._mostrar_mensaje(f"Expediente de {trabajador.nombre} eliminado", 'success')
        self.label_exp_estado.config(text="⚠️ Sin expediente", fg=self.colors['warning'])
        self._limpiar_formulario_expediente()

    def _limpiar_formulario_expediente(self):
        self.label_exp_nombres.config(text="")
        self.label_exp_apellidos.config(text="")
        self.label_exp_cedula_cargo.config(text="")
        self.entry_exp_fecha_nac.config(state='normal')
        self.entry_exp_fecha_nac.delete(0, tk.END)
        self.entry_exp_fecha_nac.config(state='readonly')
        self.entry_exp_edad.config(state='normal')
        self.entry_exp_edad.delete(0, tk.END)
        self.entry_exp_edad.config(state='readonly')
        self.entry_exp_direccion.delete(0, tk.END)
        self.entry_exp_telefono.delete(0, tk.END)
        self.entry_exp_correo.delete(0, tk.END)
        self.entry_exp_hijos.delete(0, tk.END)
        self.entry_exp_emerg_nombre.delete(0, tk.END)
        self.entry_exp_emerg_parentesco.delete(0, tk.END)
        self.entry_exp_emerg_telefono.delete(0, tk.END)
        self.var_exp_condiciones.set('no')
        self.entry_exp_condiciones.delete('1.0', tk.END)
        self.entry_exp_condiciones.config(state='disabled')
        self.entry_exp_condiciones_container.pack_forget()
        self.foto_canvas.delete("all")
        self.foto_canvas.create_text(55, 55, text="Sin foto", fill=self.colors['text_gray'], font=('Segoe UI', 9))
        self.label_exp_foto_path.config(text="")
        self.label_exp_estado.config(text="", fg=self.colors['text_gray'])
        self._expediente_cedula_actual = None

    def _ver_expediente_popup(self):
        if not self._expediente_cedula_actual:
            seleccion = self.combo_expediente.get()
            if seleccion:
                cedula = seleccion.split(" - ")[0]
                self._cargar_expediente_por_cedula(cedula)
            else:
                self._mostrar_mensaje("Primero seleccione un trabajador", 'warning')
                return

        trabajador = self.nomina.trabajadores.get(self._expediente_cedula_actual)
        if not trabajador:
            self._mostrar_mensaje("Trabajador no encontrado", 'error')
            return

        if not trabajador.tiene_expediente():
            self._mostrar_mensaje("Este trabajador no tiene expediente completo para ver", 'warning')
            return

        ventana = tk.Toplevel(self.root)
        ventana.title(f"Expediente de {trabajador.nombres} {trabajador.apellidos}")
        ventana.geometry("700x520")
        ventana.configure(bg=self.colors['bg_dark'])
        ventana.grab_set()
        ventana.transient(self.root)

        def on_root_unmap(e):
            try:
                ventana.destroy()
            except:
                pass
                
        # Guardar la referencia al binding para poder eliminarlo correctamente
        binding_id = self.root.bind('<Unmap>', on_root_unmap)
        
        def on_ventana_destroy(e):
            try:
                self.root.unbind('<Unmap>', binding_id)
            except:
                pass
                
        ventana.bind('<Destroy>', on_ventana_destroy)

        main_frame = tk.Frame(ventana, bg=self.colors['bg_main'])
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)

        tk.Label(main_frame, text=f"Expediente de {trabajador.nombres} {trabajador.apellidos}",
                 font=('Segoe UI', 14, 'bold'),
                 bg=self.colors['bg_main'], fg=self.colors['text_light']).pack(anchor='w', pady=(0,8))

        datos_frame = tk.Frame(main_frame, bg=self.colors['bg_main'])
        datos_frame.pack(fill='both', expand=True)

        izquierda = tk.Frame(datos_frame, bg=self.colors['bg_main'])
        izquierda.pack(side='left', fill='both', expand=True, padx=(0,10))

        foto_frame = tk.Frame(izquierda, bg=self.colors['bg_main'])
        foto_frame.pack(anchor='w', pady=4)
        if trabajador.foto_path and os.path.exists(trabajador.foto_path):
            try:
                from PIL import Image, ImageTk
                img = Image.open(trabajador.foto_path)
                img.thumbnail((110, 110), Image.LANCZOS)
                foto_tk = ImageTk.PhotoImage(img)
                lbl_foto = tk.Label(foto_frame, image=foto_tk, bg=self.colors['bg_main'])
                lbl_foto.image = foto_tk
                lbl_foto.pack(side='left')
            except:
                tk.Label(foto_frame, text="📷", font=('Segoe UI', 40), bg=self.colors['bg_main']).pack(side='left')
        else:
            tk.Label(foto_frame, text="📷", font=('Segoe UI', 40), bg=self.colors['bg_main']).pack(side='left')

        info_foto = tk.Frame(foto_frame, bg=self.colors['bg_main'])
        info_foto.pack(side='left', padx=8)

        tk.Label(info_foto, text=f"{trabajador.nombres}", font=('Segoe UI', 12, 'bold'),
                 bg=self.colors['bg_main'], fg=self.colors['text_light']).pack(anchor='w')
        tk.Label(info_foto, text=f"{trabajador.apellidos}", font=('Segoe UI', 12, 'bold'),
                 bg=self.colors['bg_main'], fg=self.colors['text_light']).pack(anchor='w')

        tk.Label(izquierda, text=f"Cédula: {trabajador.cedula}  |  Cargo: {trabajador.cargo}",
                 font=('Segoe UI', 9), bg=self.colors['bg_main'], fg=self.colors['text_gray']).pack(anchor='w', pady=2)

        info_personal = [
            ("Fecha de nacimiento", trabajador.fecha_nacimiento),
            ("Edad", trabajador.edad),
            ("Dirección", trabajador.direccion),
            ("Teléfono", trabajador.telefono),
            ("Correo", trabajador.correo),
            ("Número de hijos", trabajador.hijos if trabajador.hijos > 0 else "0"),
        ]
        for label, valor in info_personal:
            if valor:
                tk.Label(izquierda, text=f"{label}: {valor}", font=('Segoe UI', 9),
                         bg=self.colors['bg_main'], fg=self.colors['text_light']).pack(anchor='w', pady=1)

        derecha = tk.Frame(datos_frame, bg=self.colors['card_bg'], relief='groove', bd=2)
        derecha.pack(side='right', fill='both', expand=True, padx=(10,0), pady=4)
        derecha.config(highlightbackground=self.colors['border'], highlightthickness=1)

        tk.Label(derecha, text="Datos de emergencia y salud", font=('Segoe UI', 11, 'bold'),
                 bg=self.colors['card_bg'], fg=self.colors['accent']).pack(anchor='w', padx=10, pady=(8,4))

        ce = trabajador.contacto_emergencia
        if ce.get('nombre'):
            tk.Label(derecha, text=f"Nombre: {ce['nombre']}", font=('Segoe UI', 9),
                     bg=self.colors['card_bg'], fg=self.colors['text_light']).pack(anchor='w', padx=10, pady=1)
        if ce.get('parentesco'):
            tk.Label(derecha, text=f"Parentesco: {ce['parentesco']}", font=('Segoe UI', 9),
                     bg=self.colors['card_bg'], fg=self.colors['text_light']).pack(anchor='w', padx=10, pady=1)
        if ce.get('telefono'):
            tk.Label(derecha, text=f"Teléfono: {ce['telefono']}", font=('Segoe UI', 9),
                     bg=self.colors['card_bg'], fg=self.colors['text_light']).pack(anchor='w', padx=10, pady=1)

        if trabajador.condiciones_medicas:
            tk.Label(derecha, text="Condiciones médicas:", font=('Segoe UI', 9, 'bold'),
                     bg=self.colors['card_bg'], fg=self.colors['text_gray']).pack(anchor='w', padx=10, pady=(8,2))
            tk.Label(derecha, text=trabajador.condiciones_medicas, font=('Segoe UI', 9),
                     bg=self.colors['card_bg'], fg=self.colors['text_light'], wraplength=250, justify='left').pack(anchor='w', padx=10, pady=2)

        self._crear_boton(main_frame, "CERRAR", ventana.destroy, 'danger').pack(pady=10)