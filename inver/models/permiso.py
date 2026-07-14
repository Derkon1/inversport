# inver/models/permiso.py
from dataclasses import dataclass, field
from datetime import datetime
import re
from typing import Optional


@dataclass
class Permiso:
    tipo: str
    dias: int
    motivo: str
    fecha_inicio: str
    fecha_fin: str
    id_permiso: Optional[int] = None

    def __post_init__(self):
        try:
            inicio = datetime.strptime(self.fecha_inicio, "%Y-%m-%d").date()
            fin = datetime.strptime(self.fecha_fin, "%Y-%m-%d").date()
            if fin < inicio:
                raise ValueError("La fecha fin no puede ser anterior a la fecha inicio")
            dias_calculados = (fin - inicio).days + 1
            if dias_calculados != self.dias:
                raise ValueError(f"Los días ({self.dias}) no coinciden con el rango de fechas ({dias_calculados} días)")
            if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$', self.motivo):
                raise ValueError("El motivo solo puede contener letras y espacios")
        except ValueError as e:
            raise ValueError(f"Error en el permiso: {e}")

    def cubre_fecha(self, fecha: str) -> bool:
        fecha_actual = datetime.strptime(fecha, "%Y-%m-%d").date()
        inicio = datetime.strptime(self.fecha_inicio, "%Y-%m-%d").date()
        fin = datetime.strptime(self.fecha_fin, "%Y-%m-%d").date()
        return inicio <= fecha_actual <= fin

    def __str__(self) -> str:
        return f"{self.tipo} | {self.dias} días | {self.fecha_inicio} -> {self.fecha_fin} | Motivo: {self.motivo}"