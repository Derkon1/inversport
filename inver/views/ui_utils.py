# inver/views/ui_utils.py
import tkinter as tk

BOTON_ANCHO = 20


def crear_boton(parent, texto, comando, tipo='primary', colors=None, ancho=BOTON_ANCHO):
    if colors is None:
        colors = {
            'primary': '#0077ff',
            'success': '#10b981',
            'danger': '#ef4444',
            'warning': '#f59e0b',
            'info': '#3b82f6'
        }
    colores = {
        'primary': colors.get('accent', '#0077ff'),
        'success': colors.get('success', '#10b981'),
        'danger': colors.get('error', '#ef4444'),
        'warning': colors.get('warning', '#f59e0b'),
        'info': colors.get('info', '#3b82f6')
    }
    color = colores.get(tipo, colores['primary'])
    return tk.Button(parent, text=texto, command=comando,
                     bg=color, fg='white', font=('Segoe UI', 9, 'bold'),
                     relief='flat', padx=8, pady=4)


def darken_color(hex_color):
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f'#{max(0, r-40):02x}{max(0, g-40):02x}{max(0, b-40):02x}'


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind('<Enter>', self.show_tip)
        widget.bind('<Leave>', self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("Segoe UI", 9))
        label.pack()

    def hide_tip(self, event=None):
        if self.tip_window:
            self.tip_window.destroy()
        self.tip_window = None