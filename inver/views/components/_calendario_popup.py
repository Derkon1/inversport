# inver/views/components/_calendario_popup.py
import calendar
import tkinter as tk
from datetime import datetime


class CalendarioPopup:
    """Popup para seleccionar fecha."""
    
    def __init__(self, parent, target_entry, colors, meses_es, callback=None):
        self.parent = parent
        self.target_entry = target_entry
        self.colors = colors
        self.meses_es = meses_es
        self.callback = callback

        try:
            selected = datetime.strptime(target_entry.get(), "%Y-%m-%d")
        except:
            selected = datetime.now()
        self.year = selected.year
        self.month = selected.month

        self.popup = tk.Toplevel(parent)
        self.popup.transient(parent)
        self.popup.title("Seleccionar fecha")
        self.popup.resizable(False, False)
        self.popup.configure(bg=self.colors['bg_dark'])
        self.popup.grab_set()
        self.popup.protocol("WM_DELETE_WINDOW", self.cerrar)

        self.parent.bind('<Unmap>', self._on_parent_unmap)
        self._actualizar()

    def _on_parent_unmap(self, event):
        """Cierra el popup cuando la ventana principal se minimiza."""
        self.cerrar()

    def _actualizar(self):
        for child in self.popup.winfo_children():
            child.destroy()

        header = tk.Frame(self.popup, bg=self.colors['bg_dark'])
        header.pack(fill='x', padx=4, pady=(4, 0))

        tk.Button(header, text="◀◀", width=6, height=1,
                  command=self._year_anterior, bg=self.colors['card_bg'], fg=self.colors['text_light'], relief='flat',
                  anchor='center', justify='center').pack(side='left')
        tk.Button(header, text="◀", width=6, height=1,
                  command=self._mes_anterior, bg=self.colors['card_bg'], fg=self.colors['text_light'], relief='flat',
                  anchor='center', justify='center').pack(side='left')

        mes_texto = self.meses_es.get(self.month, '')
        tk.Label(header, text=f"{mes_texto} {self.year}",
                 bg=self.colors['bg_dark'], fg=self.colors['text_light'], font=('Segoe UI', 10, 'bold')).pack(side='left', padx=4)

        tk.Button(header, text="▶", width=6, height=1,
                  command=self._mes_siguiente, bg=self.colors['card_bg'], fg=self.colors['text_light'], relief='flat',
                  anchor='center', justify='center').pack(side='left')
        tk.Button(header, text="▶▶", width=6, height=1,
                  command=self._year_siguiente, bg=self.colors['card_bg'], fg=self.colors['text_light'], relief='flat',
                  anchor='center', justify='center').pack(side='left')

        year_frame = tk.Frame(self.popup, bg=self.colors['bg_dark'])
        year_frame.pack(fill='x', padx=4, pady=2)
        tk.Label(year_frame, text="Año:", bg=self.colors['bg_dark'], fg=self.colors['text_gray']).pack(side='left')
        self.entry_cal_year = tk.Entry(year_frame, width=4, font=('Segoe UI', 9),
                                       bg=self.colors['input_bg'], fg=self.colors['text_light'],
                                       insertbackground=self.colors['text_light'])
        self.entry_cal_year.insert(0, str(self.year))
        self.entry_cal_year.pack(side='left', padx=2)
        self.entry_cal_year.bind('<Return>', self._cambiar_year)
        self.entry_cal_year.bind('<FocusOut>', self._cambiar_year)

        week_frame = tk.Frame(self.popup, bg=self.colors['bg_dark'])
        week_frame.pack(padx=4, pady=4)
        for dow in ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']:
            tk.Label(week_frame, text=dow, width=4, bg=self.colors['bg_dark'],
                     fg=self.colors['text_gray'], font=('Segoe UI', 8, 'bold')).grid(row=0, column=['Lun','Mar','Mié','Jue','Vie','Sáb','Dom'].index(dow))

        month_days = calendar.monthcalendar(self.year, self.month)
        for r, week in enumerate(month_days, start=1):
            for c, day in enumerate(week):
                if day == 0:
                    tk.Label(week_frame, text='', width=3, bg=self.colors['bg_dark']).grid(row=r, column=c)
                else:
                    btn = tk.Button(week_frame, text=str(day), width=3, height=1,
                                    command=lambda d=day: self._seleccionar(d),
                                    bg=self.colors['card_bg'], fg=self.colors['text_light'], relief='flat',
                                    font=('Segoe UI', 8),
                                    anchor='center', justify='center')
                    btn.grid(row=r, column=c, padx=1, pady=1)

        footer = tk.Frame(self.popup, bg=self.colors['bg_dark'])
        footer.pack(fill='x', padx=4, pady=(0, 4))
        tk.Button(footer, text="Cancelar", width=10, height=1, command=self.cerrar,
                  bg=self.colors['card_bg'], fg=self.colors['text_light'], relief='flat',
                  anchor='center', justify='center').pack(side='right')

    def _year_anterior(self):
        self.year -= 1
        self._actualizar()

    def _year_siguiente(self):
        self.year += 1
        self._actualizar()

    def _mes_anterior(self):
        if self.month == 1:
            self.month = 12
            self.year -= 1
        else:
            self.month -= 1
        self._actualizar()

    def _mes_siguiente(self):
        if self.month == 12:
            self.month = 1
            self.year += 1
        else:
            self.month += 1
        self._actualizar()

    def _cambiar_year(self, event=None):
        try:
            nuevo = int(self.entry_cal_year.get())
            if 1900 <= nuevo <= 2100:
                self.year = nuevo
                self._actualizar()
            else:
                self.entry_cal_year.delete(0, tk.END)
                self.entry_cal_year.insert(0, str(self.year))
        except ValueError:
            self.entry_cal_year.delete(0, tk.END)
            self.entry_cal_year.insert(0, str(self.year))

    def _seleccionar(self, day):
        fecha = datetime(self.year, self.month, day).strftime("%Y-%m-%d")
        if self.target_entry and self.target_entry.winfo_exists():
            estado_anterior = self.target_entry.cget('state')
            try:
                self.target_entry.config(state='normal')
                self.target_entry.delete(0, tk.END)
                self.target_entry.insert(0, fecha)
            finally:
                self.target_entry.config(state=estado_anterior)
        
        # Ejecutar callback de forma segura
        if self.callback:
            try:
                self.callback()
            except Exception as e:
                print(f"Error en callback del calendario: {e}")
        
        # Cerrar el popup (usando after para evitar problemas de destrucción)
        self.parent.after(10, self.cerrar)

    def cerrar(self):
        """Cierra el popup y limpia el binding."""
        try:
            self.parent.unbind('<Unmap>')
        except:
            pass
        if self.popup and self.popup.winfo_exists():
            self.popup.destroy()