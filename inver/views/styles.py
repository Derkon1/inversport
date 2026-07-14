# inver/views/styles.py
import tkinter as tk
from tkinter import ttk
from typing import List, Optional


class ThemeManager:
    """
    Gestor de temas para la aplicación.
    Contiene paletas de colores, configuración de estilos ttk,
    y métodos para aplicar el tema a toda la interfaz.
    """

    THEMES = {
        'dark': {
            'bg_dark': '#0a0e1a',
            'bg_sidebar': '#0f1423',
            'bg_main': '#131a2c',
            'card_bg': '#1a2335',
            'card_hover': '#1f2a40',
            'accent': '#0077ff',
            'accent_hover': '#005fcc',
            'success': '#10b981',
            'warning': '#f59e0b',
            'error': '#ef4444',
            'info': '#3b82f6',
            'text_light': '#f3f4f6',
            'text_gray': '#9ca3af',
            'border': '#1f2937',
            'input_bg': '#0f1423',
            'placeholder': '#6b7280'
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
                        foreground=self.colors['text_light'],
                        selectbackground=self.colors['accent'],
                        selectforeground='white')
        style.map('TCombobox',
                  fieldbackground=[('readonly', self.colors['input_bg'])])
        style.configure('TScrollbar',
                        background=self.colors['card_bg'],
                        troughcolor=self.colors['bg_main'],
                        arrowcolor=self.colors['text_gray'])
        
        style.configure('TNotebook.Tab',
                        background=self.colors['card_bg'],
                        foreground=self.colors['text_light'],
                        padding=[12, 4])
        style.map('TNotebook.Tab',
                  background=[('selected', self.colors['accent'])],
                  foreground=[('selected', 'white')])

        style.configure('Treeview',
                        background=self.colors['input_bg'],
                        foreground=self.colors['text_light'],
                        fieldbackground=self.colors['input_bg'],
                        rowheight=25)
        style.map('Treeview', background=[('selected', self.colors['accent'])])
        style.configure('Treeview.Heading', anchor='center')
        style.configure('Treeview', anchor='center')
        style.configure('TEntry',
                        fieldbackground=self.colors['input_bg'],
                        foreground=self.colors['text_light'],
                        bordercolor=self.colors['border'],
                        lightcolor=self.colors['border'],
                        darkcolor=self.colors['border'],
                        borderwidth=1,
                        relief='solid')

    def apply_theme_to_widgets(self, widget: tk.Widget):
        try:
            if isinstance(widget, (tk.Frame, tk.LabelFrame, tk.Label, tk.Button, tk.Entry, tk.Text, tk.Canvas)):
                if isinstance(widget, (tk.Frame, tk.LabelFrame)):
                    bg = self.colors['card_bg'] if widget.master != self.root else self.colors['bg_main']
                elif isinstance(widget, (tk.Entry, tk.Text)):
                    bg = self.colors['input_bg']
                elif isinstance(widget, tk.Canvas):
                    bg = self.colors['bg_sidebar'] if widget.master == self.root else self.colors['card_bg']
                else:
                    bg = self.colors['bg_main']
                fg = self.colors['text_light']
                if hasattr(widget, 'config'):
                    try:
                        widget.config(bg=bg, fg=fg)
                    except tk.TclError:
                        pass
                    if isinstance(widget, tk.Entry):
                        widget.config(insertbackground=fg)
                        if self.mode == 'light':
                            widget.config(highlightbackground=self.colors['border'],
                                          highlightcolor=self.colors['accent'],
                                          highlightthickness=1,
                                          relief='solid',
                                          bd=1)
                        else:
                            widget.config(highlightthickness=0, relief='flat', bd=0)
        except:
            pass

        for child in widget.winfo_children():
            self.apply_theme_to_widgets(child)

    def register_menu_buttons(self, buttons: List[tk.Button]):
        self.menu_buttons = buttons

    def update_menu_buttons(self):
        for btn in self.menu_buttons:
            btn.config(bg=self.colors['bg_sidebar'], fg=self.colors['text_gray'])
            btn.unbind("<Enter>")
            btn.unbind("<Leave>")
            def on_enter(e, b=btn):
                b.config(bg=self.colors['accent'], fg='white')
            def on_leave(e, b=btn):
                b.config(bg=self.colors['bg_sidebar'], fg=self.colors['text_gray'])
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