# inver/views/components/historial.py
import tkinter as tk
from tkinter import ttk
from datetime import datetime


class HistorialView:
    def _mostrar_historial(self):
        self._limpiar_contenido()
        frame = tk.Frame(self.content_area, bg=self.colors['bg_main'])
        frame.pack(fill='both', expand=True)
        self.current_frame = frame
        self.current_mensaje_label = None

        header = tk.Frame(frame, bg=self.colors['bg_main'], height=80)
        header.pack(fill='x', padx=15, pady=15)
        header.pack_propagate(False)
        header.config(highlightbackground=self.colors['border'], highlightthickness=1)
        header_inner = tk.Frame(header, bg=self.colors['bg_main'])
        header_inner.place(relx=0.5, rely=0.5, anchor='center')
        tk.Label(header_inner, text="📊", font=('Segoe UI', 24), bg=self.colors['bg_main'], fg=self.colors['accent']).pack(side='left', padx=(0,4))
        tk.Label(header_inner, text="Historial de Trabajadores", font=('Segoe UI', 18, 'bold'),
                 bg=self.colors['bg_main'], fg=self.colors['accent']).pack(side='left')

        filter_frame = tk.Frame(frame, bg=self.colors['card_bg'])
        filter_frame.pack(fill='x', padx=15, pady=8)
        filter_frame.config(highlightbackground=self.colors['border'], highlightthickness=1)
        tk.Label(filter_frame, text="Trabajador:", font=('Segoe UI', 9, 'bold'),
                 bg=self.colors['card_bg'], fg=self.colors['text_light']).pack(side='left', padx=(8,4))
        self.combo_historial = ttk.Combobox(filter_frame, width=35, font=('Segoe UI', 9))
        self.combo_historial.pack(side='left', padx=(0,14))
        tk.Label(filter_frame, text="Fecha (YYYY-MM-DD):", font=('Segoe UI', 9, 'bold'),
                 bg=self.colors['card_bg'], fg=self.colors['text_light']).pack(side='left', padx=(8,4))
        self.entry_fecha_historial = tk.Entry(filter_frame, width=12, font=('Segoe UI', 9),
                              bg=self.colors['input_bg'], fg=self.colors['text_light'], insertbackground=self.colors['text_light'],
                              highlightbackground=self.colors['input_border'], highlightthickness=1)
        self.entry_fecha_historial.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_fecha_historial.pack(side='left', padx=(0,14))
        self._crear_boton(filter_frame, "BUSCAR", self.mostrar_historial, 'info').pack(side='left')

        frame_tabla = tk.Frame(frame, bg=self.colors['bg_main'])
        frame_tabla.pack(fill='both', expand=True, padx=15, pady=8)

        # Añadir columna de Estado (Permiso)
        self.tree_registros = ttk.Treeview(frame_tabla, columns=('Fecha','Entrada','Salida','Horas','Faltas','Estado'), show='headings', height=12)
        cols = [('Fecha',100), ('Entrada',100), ('Salida',100), ('Horas',80), ('Faltas',60), ('Estado',150)]
        for col, w in cols:
            self.tree_registros.heading(col, text=col)
            self.tree_registros.column(col, width=w, anchor='center')
        scroll_y = ttk.Scrollbar(frame_tabla, orient='vertical', command=self.tree_registros.yview)
        self.tree_registros.configure(yscrollcommand=scroll_y.set)
        scroll_y.pack(side='right', fill='y')
        self.tree_registros.pack(fill='both', expand=True, padx=8, pady=8)
        self._actualizar_listas_combos()

    def mostrar_historial(self):
        seleccion = self.combo_historial.get()
        if not seleccion:
            self._mostrar_mensaje("⚠️ Seleccione un trabajador", 'warning')
            return
        cedula = seleccion.split(" - ")[0]
        fecha = self.entry_fecha_historial.get()
        self._cargar_historial(cedula, fecha)

    def _calcular_falta(self, registro, fecha):
        """Calcula si un trabajador tuvo falta en una fecha específica."""
        if registro:
            return 0
            
        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
        hoy = datetime.now().date()
        
        # Solo contar faltas en días laborales (lunes a viernes)
        if fecha_obj.weekday() >= 5:  # Sábado o Domingo
            return 0
            
        # Si es hoy, verificar si ya pasó la hora límite
        if fecha_obj == hoy:
            hora_actual = datetime.now().time()
            hora_limite = datetime.strptime(self.HORA_LIMITE, "%H:%M").time()
            return 1 if hora_actual >= hora_limite else 0
        
        # Si es una fecha pasada, es falta
        if fecha_obj < hoy:
            return 1
            
        return 0

    def _cargar_historial(self, cedula, fecha):
        """Carga el historial desde la base de datos o lo calcula en memoria."""
        trabajador = self.nomina.trabajadores.get(cedula)
        if not trabajador:
            self._mostrar_mensaje("Trabajador no encontrado", 'error')
            return

        # Limpiar tabla
        for item in self.tree_registros.get_children():
            self.tree_registros.delete(item)

        # Verificar si el trabajador tiene permiso en esta fecha
        permiso = trabajador.tiene_permiso_en_fecha(fecha)
        if permiso:
            # Si tiene permiso, mostrar eso en el historial
            self.tree_registros.insert('', 'end', values=(
                fecha,
                '--',
                '--',
                '--',
                0,
                f'EN PERMISO ({permiso.tipo})'
            ))
            return

        # Obtener registro diario del trabajador
        registro = trabajador.get_registro_por_fecha(fecha)
        faltas = 0
        entrada_formateada = 'No registró'
        salida_formateada = '--'
        horas = '-'
        estado = ''

        # Intentar obtener del historial en la base de datos
        if hasattr(self.nomina, 'db_manager') and self.nomina.db_manager:
            id_registro = self.nomina.db_manager.obtener_id_registro_por_cedula(cedula, fecha)
            
            if id_registro:
                # Buscar en el historial
                historial = self.nomina.db_manager.obtener_historial_por_fecha(id_registro, fecha)
                
                if historial:
                    # Si existe en historial, usar esos datos
                    faltas = historial.get('faltas_injustificadas', 0)
                else:
                    # Si no existe en historial, calcular y guardar
                    faltas = self._calcular_falta(registro, fecha)
                    self.nomina.db_manager.guardar_historial(id_registro, fecha, faltas)
            else:
                # Si no hay registro diario, calcular falta
                faltas = self._calcular_falta(registro, fecha)

        # Si hay registro, formatear los datos
        if registro:
            entrada_formateada = self._formato_hora_12h(registro.hora_entrada)
            if registro.hora_salida:
                salida_formateada = self._formato_hora_12h(registro.hora_salida)
                horas = str(trabajador.get_horas_trabajadas_hoy() or 0)
                estado = 'FINALIZADO'
            else:
                salida_formateada = '--'
                horas = '-'
                estado = 'EN TRABAJO'
        else:
            if faltas > 0:
                estado = 'FALTA'
            else:
                estado = 'SIN REGISTRO'

        # Mostrar en el Treeview
        self.tree_registros.insert('', 'end', values=(
            fecha,
            entrada_formateada,
            salida_formateada,
            horas if horas != '-' else '0',
            faltas,
            estado
        ))

        # Si hay conexión a BD y no se guardó el historial, guardarlo ahora
        if hasattr(self.nomina, 'db_manager') and self.nomina.db_manager:
            id_registro = self.nomina.db_manager.obtener_id_registro_por_cedula(cedula, fecha)
            if id_registro:
                historial = self.nomina.db_manager.obtener_historial_por_fecha(id_registro, fecha)
                if not historial:
                    self.nomina.db_manager.guardar_historial(id_registro, fecha, faltas)