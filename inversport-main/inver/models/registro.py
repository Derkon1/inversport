from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RegistroEntrada:
    fecha: str
    hora_entrada: str
    hora_salida: Optional[str] = None

    def __str__(self) -> str:
        if self.hora_salida:
            return f"{self.fecha} | Entrada: {self.hora_entrada} | Salida: {self.hora_salida}"
        return f"{self.fecha} | Entrada: {self.hora_entrada} | En turno"


@dataclass
class RegistroProduccion:
    fecha: str
    ticket: str
    referencia: str
    color: str
    pares: int
    pedido: int
    precio: float
    id_produccion: Optional[int] = None

    def __post_init__(self):
        self.total = self.pares * self.precio