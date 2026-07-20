import tkinter as tk
from tkinter import ttk
from datetime import datetime


class ActivosView:
    def _mostrar_activos(self):
        self._limpiar_contenido()
        frame = tk.Frame(self.content_area, bg=self.colors['bg_main'])
        frame.pack(fill='both', expand=True)
        self.current_frame = frame

        header = tk.Frame(frame, bg=self.colors['card_bg'], height=70)
        header.pack(fill='x', padx=15, pady=15)
        header.pack_propagate(False)
        header.config(highlightbackground=self.colors['border'], highlightthickness=1)
        header_inner = tk.Frame(header, bg=self.colors['card_bg'])
        header_inner.place(relx=0.5, rely=0.5, anchor='center')
        tk.Label(header_inner, text="👥", font=('Segoe UI', 22), bg=self.colors['card_bg'], fg=self.colors['accent']).pack(side='left', padx=(0,4))
        tk.Label(header_inner, text="Trabajadores Activos", font=('Segoe UI', 16, 'bold'),
                 bg=self.colors['card_bg'], fg=self.colors['text_light']).pack(side='left')

        canvas_container = tk.Frame(frame, bg=self.colors['bg_main'])
        canvas_container.pack(fill='both', expand=True, padx=15, pady=8)
        canvas = tk.Canvas(canvas_container, bg=self.colors['bg_main'], highlightthickness=0)
        h_scrollbar = ttk.Scrollbar(canvas_container, orient="horizontal", command=canvas.xview)
        v_scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=canvas.yview)
        canvas.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)

        self.activos_frame = tk.Frame(canvas, bg=self.colors['bg_main'])
        canvas.create_window((0,0), window=self.activos_frame, anchor="nw")
        self.activos_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.pack(side='left', fill='both', expand=True)
        h_scrollbar.pack(side='bottom', fill='x')
        v_scrollbar.pack(side='right', fill='y')

        self._crear_boton(frame, "ACTUALIZAR", self.actualizar_lista_activos, 'info').pack(pady=10)
        
        # Actualizar automáticamente cada 30 segundos
        self._programar_actualizacion_activos()
        self.actualizar_lista_activos()

    def _programar_actualizacion_activos(self):
        """Programa actualización automática cada 30 segundos."""
        if hasattr(self, 'current_frame') and self.current_frame and self.current_frame.winfo_exists():
            self.actualizar_lista_activos()
            self.root.after(30000, self._programar_actualizacion_activos)

    def actualizar_lista_activos(self):
        if not hasattr(self, 'activos_frame') or not self.activos_frame.winfo_exists():
            return
        for w in self.activos_frame.winfo_children():
            w.destroy()

        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        trabajando = []
        con_permiso = []

        for cedula, t in self.nomina.trabajadores.items():
            permiso = t.tiene_permiso_en_fecha(fecha_actual)
            if permiso:
                con_permiso.append((cedula, t, permiso))
            else:
                registro = t.get_registro_por_fecha(fecha_actual)
                if registro and not registro.hora_salida:
                    trabajando.append((cedula, t, registro))

        # Mostrar trabajadores trabajando
        if trabajando:
            sec_frame = tk.Frame(self.activos_frame, bg=self.colors['bg_main'])
            sec_frame.pack(fill='x', pady=4)
            tk.Label(sec_frame, text="✅ TRABAJANDO", font=('Segoe UI', 12, 'bold'),
                     bg=self.colors['bg_main'], fg=self.colors['success']).pack(anchor='w')
            cards_frame = tk.Frame(sec_frame, bg=self.colors['bg_main'])
            cards_frame.pack(fill='x', pady=2)
            for cedula, t, reg in trabajando:
                estado_text = f"Entrada: {self._formato_hora_12h(reg.hora_entrada)}"
                self._crear_tarjeta_trabajador(cards_frame, t, cedula, estado_text, self.colors['success'])

        # Mostrar trabajadores con permiso
        if con_permiso:
            sec_frame = tk.Frame(self.activos_frame, bg=self.colors['bg_main'])
            sec_frame.pack(fill='x', pady=4)
            tk.Label(sec_frame, text="🔴 CON PERMISO", font=('Segoe UI', 12, 'bold'),
                     bg=self.colors['bg_main'], fg=self.colors['error']).pack(anchor='w')
            cards_frame = tk.Frame(sec_frame, bg=self.colors['bg_main'])
            cards_frame.pack(fill='x', pady=2)
            for cedula, t, perm in con_permiso:
                self._crear_tarjeta_trabajador(cards_frame, t, cedula, f"Permiso: {perm.tipo}", self.colors['warning'])

        if not trabajando and not con_permiso:
            tk.Label(self.activos_frame, text="No hay trabajadores activos en este momento",
                     font=('Segoe UI', 14), bg=self.colors['bg_main'], fg=self.colors['text_gray']).pack(pady=40)

    def _crear_tarjeta_trabajador(self, parent, trabajador, cedula, estado_text, color_borde):
        """Crea una tarjeta más pequeña para trabajadores."""
        card = tk.Frame(parent, bg=self.colors['card_bg'], relief='ridge', bd=2,
                        highlightbackground=color_borde, highlightcolor=color_borde, highlightthickness=2,
                        width=180, height=90)  # Tamaño fijo más pequeño
        card.pack(side='left', padx=5, pady=3, fill='none')
        card.pack_propagate(False)  # Mantener tamaño fijo

        if "Entrada" in estado_text:
            emoji = "✅"
        else:
            emoji = "🔴"
        
        # Estado
        tk.Label(card, text=f"{emoji} {estado_text}", font=('Segoe UI', 9, 'bold'),
                 bg=self.colors['card_bg'], fg=color_borde).pack(pady=(4,0))

        # Nombre
        tk.Label(card, text=trabajador.nombre, font=('Segoe UI', 10, 'bold'),
                 bg=self.colors['card_bg'], fg=self.colors['text_light']).pack()
        
        # Cédula y cargo en una sola línea más compacta
        tk.Label(card, text=f"Cédula: {cedula}  |  {trabajador.cargo}", font=('Segoe UI', 7),
                 bg=self.colors['card_bg'], fg=self.colors['text_gray']).pack(pady=(0,4))