# inver/views/main_view.py
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from pathlib import Path

from .base_view import BaseView
from .components import (
    RegistroView, ActivosView, PermisosView, HistorialView,
    NominasView, TrabajadoresView, ExpedienteView, CalendarioMixin
)
from .styles import ThemeManager
from .ui_utils import crear_boton, ToolTip
from ..models import Nomina
from ..utils.utils import formato_cop, parsear_cop


class AppNomina(
    BaseView,
    RegistroView,
    ActivosView,
    PermisosView,
    HistorialView,
    NominasView,
    TrabajadoresView,
    ExpedienteView,
    CalendarioMixin,
):
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gestión de Talento Humano")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 650)

        self.HORA_LIMITE = "17:22"

        self.vcmd_numeros = self.root.register(self._validar_solo_numeros)
        self.vcmd_letras = self.root.register(self._validar_solo_letras)
        self.vcmd_fecha = self.root.register(self._validar_fecha)
        self.vcmd_decimal = self.root.register(self._validar_decimal)
        self._cargar_iconos()

        self.nomina = Nomina()
        self.theme_manager = ThemeManager(mode='dark', root=root)
        self.colors = self.theme_manager.colors

        self.menu_buttons = []
        self.current_frame = None
        self.current_mensaje_label = None
        self.mensaje_timer = None

        self.meses_es = {
            1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
            5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
            9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
        }

        # Inicializar BaseView
        BaseView.__init__(self)

        self._setup_layout()
        self._crear_dashboard()
        self._mostrar_registro()
        self._configurar_estilos_ttk()
        self._actualizar_listas_combos()

    def _cargar_iconos(self):
        base_dir = Path(__file__).resolve().parent.parent.parent
        imagenes_dir = base_dir / "imagenes"

        try:
            from PIL import Image, ImageTk
            img = Image.open(imagenes_dir / "miniatura.png")
            self.icono = ImageTk.PhotoImage(img)
            self.root.iconphoto(True, self.icono)
        except Exception:
            pass

        self.logo_image_sidebar = None
        self.logo_canvas = None
        try:
            from PIL import Image, ImageTk
            img_logo = Image.open(imagenes_dir / "INVERSPORT.png")
            target_width = 140
            ratio = target_width / img_logo.width
            new_size = (target_width, int(img_logo.height * ratio))
            img_logo = img_logo.resize(new_size, Image.LANCZOS)
            self.logo_image_sidebar = ImageTk.PhotoImage(img_logo)
        except Exception as e:
            print(f"No se pudo cargar el logo: {e}")

    def _setup_layout(self):
        self.root.configure(bg=self.colors['bg_dark'])
        self.main_container = tk.Frame(self.root, bg=self.colors['bg_dark'])
        self.main_container.pack(fill='both', expand=True)

        self.sidebar = tk.Frame(self.main_container, bg=self.colors['bg_sidebar'], width=260)
        self.sidebar.pack(side='left', fill='y')
        self.sidebar.pack_propagate(False)

        self.content_area = tk.Frame(self.main_container, bg=self.colors['bg_main'])
        self.content_area.pack(side='right', fill='both', expand=True)

        self.status_bar = tk.Frame(self.root, bg=self.colors['bg_sidebar'], height=35)
        self.status_bar.pack(side='bottom', fill='x')
        self.status_bar.pack_propagate(False)

        self.hora_label = tk.Label(self.status_bar, font=('Segoe UI', 11, 'bold'),
                                   bg=self.colors['bg_sidebar'], fg=self.colors['accent'])
        self.hora_label.pack(side='right', padx=12, pady=4)

        self.fecha_label = tk.Label(self.status_bar, font=('Segoe UI', 9),
                                    bg=self.colors['bg_sidebar'], fg=self.colors['text_gray'])
        self.fecha_label.pack(side='right', padx=8)

        self.status_msg = tk.Label(self.status_bar, font=('Segoe UI', 9),
                                   bg=self.colors['bg_sidebar'], fg=self.colors['text_light'])
        self.status_msg.pack(side='left', padx=12)

        self._actualizar_reloj()

    def _actualizar_reloj(self):
        ahora = datetime.now()
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        self.fecha_label.config(text=f"{dias[ahora.weekday()]}, {ahora.day} de {meses[ahora.month-1]}")
        self.hora_label.config(text=ahora.strftime("%I:%M:%S %p"))
        self.root.after(1000, self._actualizar_reloj)

    def _crear_dashboard(self):
        logo_frame = tk.Frame(self.sidebar, bg=self.colors['bg_sidebar'], height=140)
        logo_frame.pack(fill='x', pady=(15, 8))
        logo_frame.pack_propagate(False)

        logo_bg = tk.Frame(logo_frame, bg=self.colors['bg_sidebar'], width=240, height=80)
        logo_bg.pack(pady=8)
        logo_bg.pack_propagate(False)

        if self.logo_image_sidebar:
            self.logo_canvas = tk.Canvas(logo_bg, width=240, height=80,
                                         bg=self.colors['bg_sidebar'], highlightthickness=0)
            self.logo_canvas.pack(expand=True, fill='both')
            self.logo_canvas.create_image(120, 40, image=self.logo_image_sidebar, anchor='center')
            self.logo_canvas.image = self.logo_image_sidebar

        tk.Label(logo_frame, text="Gestión de Talento", font=('Segoe UI', 12, 'bold'),
                 bg=self.colors['bg_sidebar'], fg=self.colors['text_light']).pack()
        tk.Label(logo_frame, text="Sistema de Control", font=('Segoe UI', 8),
                 bg=self.colors['bg_sidebar'], fg=self.colors['text_gray']).pack()

        tk.Frame(self.sidebar, bg=self.colors['border'], height=1).pack(fill='x', padx=16, pady=12)

        menu_items = [
            ("🎯", "Registro Diario", self._mostrar_registro),
            ("👥", "Trabajadores Activos", self._mostrar_activos),
            ("📋", "Permisos", self._mostrar_permisos),
            ("📊", "Historial", self._mostrar_historial),
            ("💰", "Nómina", self._mostrar_nomina_semanal),
            ("👤", "Agregar Trabajador", self._mostrar_agregar_trabajador),
            ("⚙️", "Actualizar Cargo", self._mostrar_actualizar_cargo),
            ("📁", "Expediente", self._mostrar_expediente),
        ]

        self.menu_buttons = []
        for icon, text, command in menu_items:
            btn_frame = tk.Frame(self.sidebar, bg=self.colors['bg_sidebar'])
            btn_frame.pack(fill='x', padx=10, pady=3)

            btn = tk.Button(btn_frame, text=f"  {icon}  {text}",
                            font=('Segoe UI', 10), bg=self.colors['bg_sidebar'],
                            fg=self.colors['text_gray'], anchor='w', padx=12, pady=8,
                            relief='flat', cursor='hand2', command=command)
            btn.pack(fill='x')

            def on_enter(e, b=btn):
                b.config(bg=self.colors['accent'], fg='white')
            def on_leave(e, b=btn):
                b.config(bg=self.colors['bg_sidebar'], fg=self.colors['text_gray'])

            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
            self.menu_buttons.append(btn)

        tk.Frame(self.sidebar, bg=self.colors['border'], height=1).pack(fill='x', padx=16, pady=12)

    def _configurar_estilos_ttk(self):
        self.theme_manager.configure_ttk_styles()