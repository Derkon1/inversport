import tkinter as tk
from datetime import datetime
from ...views.components._calendario_popup import CalendarioPopup


class CalendarioMixin:

    def _abrir_calendario(self, target_entry, callback=None):
        """Abre el calendario popup para el Entry objetivo."""

        if hasattr(self, 'cal_popup') and self.cal_popup:
            try:
                self.cal_popup.cerrar()
            except:
                pass
            self.cal_popup = None

        self.calendar_target_entry = target_entry
        self.calendar_target_callback = callback

        try:
            selected = datetime.strptime(target_entry.get(), "%Y-%m-%d")
        except:
            selected = datetime.now()

        self.calendar_year = selected.year
        self.calendar_month = selected.month

        parent = target_entry.winfo_toplevel()
        self.cal_popup = CalendarioPopup(
            parent=parent,
            target_entry=target_entry,
            colors=self.colors,
            meses_es=self.meses_es,
            callback=self._on_calendar_selected
        )

    def _cerrar_calendario(self):
        if hasattr(self, 'cal_popup') and self.cal_popup:
            try:
                self.cal_popup.cerrar()
            except:
                pass
            self.cal_popup = None

    def _on_calendar_selected(self):
        
        if hasattr(self, '_actualizar_edad_expediente') and hasattr(self, 'entry_exp_fecha_nac'):
            try:
                self._actualizar_edad_expediente()
            except:
                pass

        if hasattr(self, '_validar_fechas_permiso') and hasattr(self, 'entry_fecha_inicio') and hasattr(self, 'entry_fecha_fin'):
            try:
                self._validar_fechas_permiso()
            except:
                pass

        if hasattr(self, 'calendar_target_callback') and self.calendar_target_callback:
            self.calendar_target_callback()