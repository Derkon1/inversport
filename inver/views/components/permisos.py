# inver/views/components/permisos.py
import tkinter as tk
from tkinter import ttk, messagebox
import re
from datetime import datetime
from ...views.ui_utils import ToolTip
from ...models import Permiso


class PermisosView:
    def _mostrar_permisos(self):
        self._limpiar_contenido()
        frame = tk.Frame(self.content_area, bg=self.colors['bg_main'])
        frame.pack(fill='both', expand=True)
        self.current_frame = frame

        notebook = ttk.Notebook(frame)
        notebook.pack(fill='both', expand=True, padx=15, pady=15)

        tab_nuevo = tk.Frame(notebook, bg=self.colors['bg_main'])
        notebook.add(tab_nuevo, text="📌 Registrar Permiso")
        self._crear_form_permiso(tab_nuevo)

        tab_activos = tk.Frame(notebook, bg=self.colors['bg_main'])
        notebook.add(tab_activos, text="📋 Permisos Registrados")
        self._crear_tab_permisos_activos(tab_activos)

        self._actualizar_listas_combos()
        self._actualizar_permisos_activos()

    def _crear_form_permiso(self, parent):
        card = tk.LabelFrame(parent, text="📋 Nuevo Permiso", font=('Segoe UI', 11, 'bold'),
                             bg=self.colors['card_bg'], fg=self.colors['accent'], bd=2, relief='groove')
        card.pack(fill='x', padx=30, pady=20)
        form = tk.Frame(card, bg=self.colors['card_bg'])
        form.pack(padx=15, pady=15, fill='x')

        tk.Label(form, text="👤 Trabajador", font=('Segoe UI', 9, 'bold'),
                 bg=self.colors['card_bg'], fg=self.colors['text_gray']).pack(anchor='w', pady=(0,4))
        self.combo_permiso_trabajador = ttk.Combobox(form, font=('Segoe UI', 10), width=50)
        self.combo_permiso_trabajador.pack(fill='x', pady=(0,10), ipady=4)
        ToolTip(self.combo_permiso_trabajador, "Seleccione el trabajador al que se le otorgará el permiso")

        row2 = tk.Frame(form, bg=self.colors['card_bg'])
        row2.pack(fill='x', pady=6)
        tk.Label(row2, text="📌 Tipo", font=('Segoe UI', 9, 'bold'),
                 bg=self.colors['card_bg'], fg=self.colors['text_gray']).pack(side='left', padx=(0,8))
        self.combo_tipo_permiso = ttk.Combobox(row2, values=['Médico', 'Personal', 'Familiar', 'Estudio', 'Vacaciones', 'Otro'],
                                               width=18, font=('Segoe UI', 10))
        self.combo_tipo_permiso.pack(side='left', padx=(0,14))
        tk.Label(row2, text="⏱️ Días", font=('Segoe UI', 9, 'bold'),
                 bg=self.colors['card_bg'], fg=self.colors['text_gray']).pack(side='left', padx=(0,8))
        self.entry_dias_permiso = tk.Entry(row2, width=8, font=('Segoe UI', 10),
                           bg=self.colors['input_bg'], fg=self.colors['text_light'], insertbackground=self.colors['text_light'])
        self.entry_dias_permiso.pack(side='left')
        self.entry_dias_permiso.bind('<FocusOut>', lambda e: self._validar_numero_entero(self.entry_dias_permiso, 'Días'))
        self.entry_dias_permiso.bind('<KeyRelease>', lambda e: self._validar_fechas_permiso())

        row3 = tk.Frame(form, bg=self.colors['card_bg'])
        row3.pack(fill='x', pady=6)
        tk.Label(row3, text="📅 Inicio", font=('Segoe UI', 9, 'bold'),
                 bg=self.colors['card_bg'], fg=self.colors['text_gray']).pack(side='left', padx=(0,8))
        self.entry_fecha_inicio = tk.Entry(row3, width=12, font=('Segoe UI', 10),
                                   bg=self.colors['input_bg'], fg=self.colors['text_light'], insertbackground=self.colors['text_light'],
                                   state='readonly', readonlybackground=self.colors['input_bg'])
        self.entry_fecha_inicio.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_fecha_inicio.pack(side='left', padx=(0,4))
        self.entry_fecha_inicio.bind('<Button-1>', lambda e: self._abrir_calendario(self.entry_fecha_inicio))
        tk.Button(row3, text='📅', width=2, height=1, command=lambda: self._abrir_calendario(self.entry_fecha_inicio),
                  bg=self.colors['accent'], fg='white', relief='flat', anchor='center', justify='center').pack(side='left', padx=(0,8))
        tk.Label(row3, text="📅 Fin", font=('Segoe UI', 9, 'bold'),
                 bg=self.colors['card_bg'], fg=self.colors['text_gray']).pack(side='left', padx=(0,8))
        self.entry_fecha_fin = tk.Entry(row3, width=12, font=('Segoe UI', 10),
                                bg=self.colors['input_bg'], fg=self.colors['text_light'], insertbackground=self.colors['text_light'],
                                state='readonly', readonlybackground=self.colors['input_bg'])
        self.entry_fecha_fin.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_fecha_fin.pack(side='left', padx=(0,4))
        self.entry_fecha_fin.bind('<Button-1>', lambda e: self._abrir_calendario(self.entry_fecha_fin))
        tk.Button(row3, text='📅', width=2, height=1, command=lambda: self._abrir_calendario(self.entry_fecha_fin),
                  bg=self.colors['accent'], fg='white', relief='flat', anchor='center', justify='center').pack(side='left')

        self.entry_fecha_inicio.bind('<ButtonRelease-1>', lambda e: self._validar_fechas_permiso())
        self.entry_fecha_fin.bind('<ButtonRelease-1>', lambda e: self._validar_fechas_permiso())

        tk.Label(form, text="💬 Motivo (descripción)", font=('Segoe UI', 9, 'bold'),
                 bg=self.colors['card_bg'], fg=self.colors['text_gray']).pack(anchor='w', pady=(8,4))
        self.entry_motivo = tk.Entry(form, font=('Segoe UI', 10),
                         bg=self.colors['input_bg'], fg=self.colors['text_light'], insertbackground=self.colors['text_light'])
        self.entry_motivo.pack(fill='x', pady=(0,14), ipady=6)
        self.entry_motivo.bind('<FocusOut>', lambda e: self._validar_motivo(self.entry_motivo, self.current_mensaje_label))
        self.entry_motivo.bind('<KeyRelease>', lambda e: self._validar_motivo(self.entry_motivo, self.current_mensaje_label))

        self.current_mensaje_label = tk.Label(form, text="", font=('Segoe UI', 9), bg=self.colors['card_bg'])
        self.current_mensaje_label.pack(pady=4)
        self._crear_boton(form, "REGISTRAR PERMISO", self.registrar_permiso, 'warning').pack(pady=8)

    def _validar_fechas_permiso(self):
        """Valida que las fechas del permiso sean correctas."""
        if not hasattr(self, 'entry_fecha_inicio') or not hasattr(self, 'entry_fecha_fin'):
            return True
            
        try:
            inicio = self.entry_fecha_inicio.get()
            fin = self.entry_fecha_fin.get()
            dias_str = self.entry_dias_permiso.get().strip() if hasattr(self, 'entry_dias_permiso') else ""
        except:
            return True
            
        if inicio and fin and dias_str:
            try:
                d_inicio = datetime.strptime(inicio, "%Y-%m-%d")
                d_fin = datetime.strptime(fin, "%Y-%m-%d")
                if d_fin < d_inicio:
                    self._mostrar_mensaje("La fecha de fin no puede ser anterior a la fecha de inicio", 'warning')
                    return False
                dias_calculados = (d_fin - d_inicio).days + 1
                dias_ingresados = int(dias_str)
                if dias_calculados != dias_ingresados:
                    self._mostrar_mensaje(f"Los días ({dias_ingresados}) no coinciden con el rango de fechas ({dias_calculados} días)", 'warning')
                    return False
            except ValueError:
                self._mostrar_mensaje("Formato de fecha inválido. Use YYYY-MM-DD", 'error')
                return False
        return True

    def registrar_permiso(self):
        if not self._validar_fechas_permiso():
            return
        seleccion = self.combo_permiso_trabajador.get()
        if not seleccion:
            self._mostrar_mensaje("⚠️ Seleccione un trabajador", 'warning')
            return
        cedula = seleccion.split(" - ")[0]
        tipo = self.combo_tipo_permiso.get()
        dias = self.entry_dias_permiso.get()
        motivo = self.entry_motivo.get()
        fecha_inicio = self.entry_fecha_inicio.get()
        fecha_fin = self.entry_fecha_fin.get()
        if not tipo or not dias or not motivo:
            self._mostrar_mensaje("⚠️ Complete todos los campos", 'warning')
            return
        if not self._validar_motivo(self.entry_motivo, self.current_mensaje_label):
            return
        try:
            dias = int(dias)
            if dias <= 0:
                self._mostrar_mensaje("Los días deben ser un número positivo", 'warning')
                return
        except ValueError:
            self._mostrar_mensaje("⚠️ Días inválidos (debe ser un número entero)", 'error')
            return
        resultado, mensaje = self.nomina.registrar_permiso(cedula, tipo, dias, motivo, fecha_inicio, fecha_fin)
        self._mostrar_mensaje(mensaje, 'success' if resultado else 'error')
        if resultado:
            self.combo_tipo_permiso.set('')
            self.entry_dias_permiso.delete(0, tk.END)
            self.entry_motivo.delete(0, tk.END)
            if hasattr(self, 'actualizar_lista_activos'):
                self.actualizar_lista_activos()
            self._actualizar_permisos_activos()

    def _crear_tab_permisos_activos(self, parent):
        frame = tk.Frame(parent, bg=self.colors['bg_main'])
        frame.pack(fill='both', expand=True, padx=8, pady=8)

        tk.Label(frame, text="Permisos Registrados", font=('Segoe UI', 11, 'bold'),
                 bg=self.colors['bg_main'], fg=self.colors['text_light']).pack(anchor='w')

        self.tree_permisos_activos = ttk.Treeview(frame, columns=('Trabajador', 'Tipo', 'Inicio', 'Fin', 'Días', 'Motivo'),
                                                  show='headings', height=10)
        cols = [('Trabajador', 180), ('Tipo', 100), ('Inicio', 100), ('Fin', 100), ('Días', 60), ('Motivo', 200)]
        for col, w in cols:
            self.tree_permisos_activos.heading(col, text=col)
            self.tree_permisos_activos.column(col, width=w, anchor='center')
        self.tree_permisos_activos.pack(fill='both', expand=True)

        btn_frame = tk.Frame(frame, bg=self.colors['bg_main'])
        btn_frame.pack(fill='x', pady=4)

        self._crear_boton(btn_frame, "ACTUALIZAR", self._actualizar_permisos_activos, 'info').pack(side='left', padx=4)
        self._crear_boton(btn_frame, "MODIFICAR", self._modificar_permiso, 'warning').pack(side='left', padx=4)
        self._crear_boton(btn_frame, "ELIMINAR", self._eliminar_permiso, 'danger').pack(side='left', padx=4)

    def _actualizar_permisos_activos(self):
        if not hasattr(self, 'tree_permisos_activos') or not self.tree_permisos_activos.winfo_exists():
            return
        for item in self.tree_permisos_activos.get_children():
            self.tree_permisos_activos.delete(item)

        for cedula, t in self.nomina.trabajadores.items():
            for idx, p in enumerate(t.permisos):
                self.tree_permisos_activos.insert('', 'end', values=(
                    t.nombre,
                    p.tipo,
                    p.fecha_inicio,
                    p.fecha_fin,
                    p.dias,
                    p.motivo
                ), tags=(cedula, str(idx)))

    def _modificar_permiso(self):
        seleccion = self.tree_permisos_activos.selection()
        if not seleccion:
            self._mostrar_mensaje("Seleccione un permiso para modificar", 'warning')
            return
        item = seleccion[0]
        tags = self.tree_permisos_activos.item(item, 'tags')
        if not tags or len(tags) < 2:
            self._mostrar_mensaje("Error: permiso no válido", 'error')
            return
        cedula = tags[0]
        indice = int(tags[1])
        trabajador = self.nomina.trabajadores.get(cedula)
        if not trabajador:
            self._mostrar_mensaje("Trabajador no encontrado", 'error')
            return
        if indice < 0 or indice >= len(trabajador.permisos):
            self._mostrar_mensaje("Permiso no encontrado", 'error')
            return
        permiso = trabajador.permisos[indice]
        self._abrir_dialogo_modificar_permiso(cedula, indice, permiso)

    def _abrir_dialogo_modificar_permiso(self, cedula, indice, permiso):
        dialog = tk.Toplevel(self.root)
        dialog.title("Modificar Permiso")
        dialog.geometry("480x380")
        dialog.configure(bg=self.colors['bg_dark'])
        dialog.grab_set()
        dialog.transient(self.root)

        def on_root_unmap(e):
            dialog.destroy()
        self.root.bind('<Unmap>', on_root_unmap)
        dialog.bind('<Destroy>', lambda e: self.root.unbind('<Unmap>', on_root_unmap))

        trabajador = self.nomina.trabajadores.get(cedula)
        if not trabajador:
            messagebox.showerror("Error", "Trabajador no encontrado")
            dialog.destroy()
            return

        main_frame = tk.Frame(dialog, bg=self.colors['bg_dark'])
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)

        tk.Label(main_frame, text=f"Modificando permiso de: {trabajador.nombre}", font=('Segoe UI', 11, 'bold'),
                 bg=self.colors['bg_dark'], fg=self.colors['text_light']).pack(anchor='w', pady=(0,8))

        tk.Label(main_frame, text="Tipo:", font=('Segoe UI', 9), bg=self.colors['bg_dark'], fg=self.colors['text_gray']).pack(anchor='w')
        tipo_var = tk.StringVar(value=permiso.tipo)
        combo_tipo = ttk.Combobox(main_frame, textvariable=tipo_var, values=self.nomina.TIPOS_PERMISO_VALIDOS, font=('Segoe UI', 9))
        combo_tipo.pack(fill='x', pady=(0,8))

        tk.Label(main_frame, text="Días:", font=('Segoe UI', 9), bg=self.colors['bg_dark'], fg=self.colors['text_gray']).pack(anchor='w')
        dias_var = tk.StringVar(value=str(permiso.dias))
        entry_dias = tk.Entry(main_frame, textvariable=dias_var, font=('Segoe UI', 9),
                              bg=self.colors['input_bg'], fg=self.colors['text_light'], insertbackground=self.colors['text_light'])
        entry_dias.pack(fill='x', pady=(0,8))

        fecha_frame = tk.Frame(main_frame, bg=self.colors['bg_dark'])
        fecha_frame.pack(fill='x', pady=(0,8))
        tk.Label(fecha_frame, text="Inicio:", font=('Segoe UI', 9), bg=self.colors['bg_dark'], fg=self.colors['text_gray']).pack(side='left')
        fecha_inicio_var = tk.StringVar(value=permiso.fecha_inicio)
        entry_inicio = tk.Entry(fecha_frame, textvariable=fecha_inicio_var, width=12, font=('Segoe UI', 9),
                                bg=self.colors['input_bg'], fg=self.colors['text_light'], insertbackground=self.colors['text_light'])
        entry_inicio.pack(side='left', padx=(4,4))
        tk.Button(fecha_frame, text='📅', width=10, height=1, command=lambda: self._abrir_calendario(entry_inicio),
                  bg=self.colors['accent'], fg='white', relief='flat', anchor='center', justify='center').pack(side='left', padx=(0,8))
        tk.Label(fecha_frame, text="Fin:", font=('Segoe UI', 9), bg=self.colors['bg_dark'], fg=self.colors['text_gray']).pack(side='left')
        fecha_fin_var = tk.StringVar(value=permiso.fecha_fin)
        entry_fin = tk.Entry(fecha_frame, textvariable=fecha_fin_var, width=12, font=('Segoe UI', 9),
                             bg=self.colors['input_bg'], fg=self.colors['text_light'], insertbackground=self.colors['text_light'])
        entry_fin.pack(side='left', padx=(4,4))
        tk.Button(fecha_frame, text='📅', width=10, height=1, command=lambda: self._abrir_calendario(entry_fin),
                  bg=self.colors['accent'], fg='white', relief='flat', anchor='center', justify='center').pack(side='left')

        tk.Label(main_frame, text="Motivo:", font=('Segoe UI', 9), bg=self.colors['bg_dark'], fg=self.colors['text_gray']).pack(anchor='w')
        motivo_var = tk.StringVar(value=permiso.motivo)
        entry_motivo = tk.Entry(main_frame, textvariable=motivo_var, font=('Segoe UI', 9),
                                bg=self.colors['input_bg'], fg=self.colors['text_light'], insertbackground=self.colors['text_light'])
        entry_motivo.pack(fill='x', pady=(0,8))

        label_estado = tk.Label(main_frame, text="", font=('Segoe UI', 9), bg=self.colors['bg_dark'], fg=self.colors['error'])
        label_estado.pack(pady=4)

        def guardar():
            tipo = tipo_var.get().strip()
            dias_str = dias_var.get().strip()
            motivo = motivo_var.get().strip()
            fecha_inicio = fecha_inicio_var.get().strip()
            fecha_fin = fecha_fin_var.get().strip()

            if not tipo or not dias_str or not motivo or not fecha_inicio or not fecha_fin:
                label_estado.config(text="Complete todos los campos", fg=self.colors['error'])
                return
            if tipo not in self.nomina.TIPOS_PERMISO_VALIDOS:
                label_estado.config(text="Tipo inválido", fg=self.colors['error'])
                return
            try:
                dias = int(dias_str)
                if dias <= 0:
                    label_estado.config(text="Días debe ser positivo", fg=self.colors['error'])
                    return
            except ValueError:
                label_estado.config(text="Días debe ser número entero", fg=self.colors['error'])
                return
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', motivo):
                label_estado.config(text="Motivo solo letras y espacios", fg=self.colors['error'])
                return
            try:
                d_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
                d_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
                if d_fin < d_inicio:
                    label_estado.config(text="Fecha fin no puede ser anterior a inicio", fg=self.colors['error'])
                    return
                dias_calc = (d_fin - d_inicio).days + 1
                if dias_calc != dias:
                    label_estado.config(text=f"Días ({dias}) no coinciden con rango ({dias_calc})", fg=self.colors['error'])
                    return
            except ValueError as e:
                label_estado.config(text=f"Formato fecha inválido: {e}", fg=self.colors['error'])
                return

            try:
                nuevo_permiso = Permiso(tipo, dias, motivo, fecha_inicio, fecha_fin)
            except ValueError as e:
                label_estado.config(text=f"Error: {e}", fg=self.colors['error'])
                return

            resultado, mensaje = self.nomina.modificar_permiso(cedula, indice, nuevo_permiso)
            if resultado:
                dialog.destroy()
                self._mostrar_mensaje(mensaje, 'success')
                self._actualizar_permisos_activos()
                if hasattr(self, 'actualizar_lista_activos'):
                    self.actualizar_lista_activos()
            else:
                label_estado.config(text=mensaje, fg=self.colors['error'])

        btn_frame = tk.Frame(main_frame, bg=self.colors['bg_dark'])
        btn_frame.pack(pady=8)
        self._crear_boton(btn_frame, "GUARDAR", guardar, 'success').pack(side='left', padx=4)
        self._crear_boton(btn_frame, "CANCELAR", dialog.destroy, 'danger').pack(side='left', padx=4)

    def _eliminar_permiso(self):
        seleccion = self.tree_permisos_activos.selection()
        if not seleccion:
            self._mostrar_mensaje("Seleccione un permiso para eliminar", 'warning')
            return
        item = seleccion[0]
        tags = self.tree_permisos_activos.item(item, 'tags')
        if not tags or len(tags) < 2:
            self._mostrar_mensaje("Error: permiso no válido", 'error')
            return
        cedula = tags[0]
        indice = int(tags[1])

        if not messagebox.askyesno("Confirmar", "¿Eliminar este permiso?"):
            return

        resultado, mensaje = self.nomina.eliminar_permiso(cedula, indice)
        self._mostrar_mensaje(mensaje, 'success' if resultado else 'error')
        if resultado:
            self._actualizar_permisos_activos()
            if hasattr(self, 'actualizar_lista_activos'):
                self.actualizar_lista_activos()