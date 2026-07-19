from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class Expediente:
    fecha_nacimiento: Optional[str] = None
    edad: Optional[int] = None
    direccion: str = ""
    telefono: str = ""
    correo: str = ""
    hijos: int = 0
    contacto_emergencia: Dict[str, str] = None
    condiciones_medicas: str = ""
    foto_path: str = ""

    def __post_init__(self):
        if self.contacto_emergencia is None:
            self.contacto_emergencia = {"nombre": "", "parentesco": "", "telefono": ""}