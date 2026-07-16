# inver/views/styles.py
import tkinter as tk
from tkinter import ttk
from typing import List, Optional


class ThemeManager:
    """
    Gestor de temas para la aplicación.
    Paleta monocromática: blanco, negro y grises.
    """

    THEMES = {
        'dark': {
            # Colores base
            'bg_dark': '#f0f2f5',           # Fondo general gris muy claro
            'bg_sidebar': '#949494',         # Sidebar negro profundo
            'bg_main': '#e4e4e5',            # Fondo principal gris muy claro
            
            # Tarjetas
            'card_bg': '#949494',            # Fondo de tarjetas blanco
            'card_hover': '#e8e8ee',         # Hover gris claro
            
            # Acentos
            'accent': '#000000',             # Gris oscuro (títulos, botones)
            'accent_hover': '#ffffff',       # Negro para hover
            'accent_light': '#ffffff',       # Gris medio para detalles
            
            # Estados
            'success': '#006600',            # Verde suave para éxito
            'warning': '#4b1c71',            # Dorado suave para advertencia
            'error': '#B71C1C',              # Rojo oscuro para error
            'info': '#1c4c96',               # Azul oscuro para info
            
            # Textos - NOMBRES COMPATIBLES
            'text_primary': '#000',       # permisos texto titulos
            'text_secondary': '#000',     # Texto secundario (gris)
            'text_light': '#000',         # titulos actualizar cargo
            'text_white': '#000',         # gestion de talento
            
            # ALIAS para compatibilidad
            'text_gray': '#000',          # Alias de text_secondary
            'text_light_color': '#9a9aaa',   # Alias de text_light
            
            # Bordes y inputs
            'border': '#000',             # Borde gris suave
            'input_bg': '#ffffff',           # Fondo de inputs blanco
            'input_border': '#000',       # Borde de inputs
            'shadow': '#00000010',           # Sombra sutil
            'white': '#ffffff',
        }
    }

    def __init__(self, mode: str = 'dark', root: Optional[tk.Tk] = None):
        self.mode = mode
        self.colors = self.THEMES[mode]
        self.root = root
        self.style = ttk.Style() if root else None
        self.menu_buttons: List[tk.Button] = []
        self._hover_bindings: List[tuple] = []

    def toggle(self) -> str:
        """Cambia entre modo claro y oscuro, devuelve el nuevo modo."""
        self.mode = 'light' if self.mode == 'dark' else 'dark'
        self.colors = self.THEMES[self.mode]
        return self.mode

    def get_color(self, key: str) -> str:
        """Devuelve el color correspondiente a la clave."""
        return self.colors.get(key, self.colors['bg_main'])

    def configure_ttk_styles(self):
        """Configura los estilos de ttk usando los colores actuales."""
        if not self.style:
            return
        style = self.style
        style.theme_use('clam')
        style.configure('TCombobox',
                        fieldbackground=self.colors['input_bg'],
                        background=self.colors['card_bg'],
                        foreground=self.colors['text_primary'],
                        selectbackground=self.colors['accent'],
                        selectforeground='white')
        style.map('TCombobox',
                  fieldbackground=[('readonly', self.colors['input_bg'])])
        style.configure('TScrollbar',
                        background=self.colors['card_bg'],
                        troughcolor=self.colors['bg_main'],
                        arrowcolor=self.colors['text_secondary'])
        
        style.configure('TNotebook.Tab',
                        background=self.colors['card_bg'],
                        foreground=self.colors['text_primary'],
                        padding=[12, 4])
        style.map('TNotebook.Tab',
                  background=[('selected', self.colors['accent'])],
                  foreground=[('selected', 'white')])

        style.configure('Treeview',
                        background=self.colors['input_bg'],
                        foreground=self.colors['text_primary'],
                        fieldbackground=self.colors['input_bg'],
                        rowheight=25)
        style.map('Treeview', background=[('selected', self.colors['accent'])])
        style.configure('Treeview.Heading', anchor='center')
        style.configure('Treeview', anchor='center')
        style.configure('TEntry',
                        fieldbackground=self.colors['input_bg'],
                        foreground=self.colors['text_primary'],
                        bordercolor=self.colors['input_border'],
                        lightcolor=self.colors['input_border'],
                        darkcolor=self.colors['input_border'],
                        borderwidth=1,
                        relief='solid')

    def apply_theme_to_widgets(self, widget: tk.Widget):
        try:
            if isinstance(widget, (tk.Frame, tk.LabelFrame, tk.Label, tk.Button, tk.Entry, tk.Text, tk.Canvas)):
                if isinstance(widget, (tk.Frame, tk.LabelFrame)):
                    # Determinar el fondo según el padre
                    if widget.master == self.root or widget.master == getattr(self, 'main_container', None):
                        bg = self.colors['bg_main']
                    elif widget.master == getattr(self, 'sidebar', None):
                        bg = self.colors['bg_sidebar']
                    else:
                        bg = self.colors['card_bg']
                elif isinstance(widget, (tk.Entry, tk.Text)):
                    bg = self.colors['input_bg']
                elif isinstance(widget, tk.Canvas):
                    if widget.master == getattr(self, 'sidebar', None):
                        bg = self.colors['bg_sidebar']
                    else:
                        bg = self.colors['card_bg']
                else:
                    bg = self.colors['bg_main']
                
                fg = self.colors['text_primary']
                
                if hasattr(widget, 'config'):
                    try:
                        # Para etiquetas en el sidebar, usar blanco
                        if isinstance(widget, tk.Label) and widget.master == getattr(self, 'sidebar', None):
                            fg = self.colors['text_white']
                        elif isinstance(widget, tk.Label):
                            if widget.master == getattr(self, 'sidebar', None):
                                fg = self.colors['text_white']
                            elif hasattr(widget, '_secondary'):
                                fg = self.colors['text_secondary']
                            else:
                                fg = self.colors['text_primary']
                        
                        widget.config(bg=bg, fg=fg)
                    except tk.TclError:
                        pass
                    
                    if isinstance(widget, tk.Entry):
                        widget.config(insertbackground=self.colors['text_primary'],
                                     highlightbackground=self.colors['input_border'],
                                     highlightcolor=self.colors['accent'],
                                     highlightthickness=1,
                                     relief='solid',
                                     bd=1)
        except:
            pass

        for child in widget.winfo_children():
            self.apply_theme_to_widgets(child)

    def register_menu_buttons(self, buttons: List[tk.Button]):
        self.menu_buttons = buttons

    def update_menu_buttons(self):
        for btn in self.menu_buttons:
            btn.config(bg=self.colors['bg_sidebar'], fg=self.colors['text_light'])
            btn.unbind("<Enter>")
            btn.unbind("<Leave>")
            def on_enter(e, b=btn):
                b.config(bg=self.colors['accent'], fg=self.colors['text_white'])
            def on_leave(e, b=btn):
                b.config(bg=self.colors['bg_sidebar'], fg=self.colors['text_light'])
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)

    def apply_theme(self, root: tk.Widget = None, menu_buttons: List[tk.Button] = None):
        if root is None and self.root is not None:
            root = self.root
        if root:
            self.configure_ttk_styles()
            self.apply_theme_to_widgets(root)
        if menu_buttons is not None:
            self.menu_buttons = menu_buttons
        if self.menu_buttons:
            self.update_menu_buttons()