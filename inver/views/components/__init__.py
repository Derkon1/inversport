# inver/views/components/__init__.py
from .registro import RegistroView
from .activos import ActivosView
from .permisos import PermisosView
from .historial import HistorialView
from .nominas import NominasView
from .trabajadores import TrabajadoresView
from .expediente import ExpedienteView
from .calendario import CalendarioMixin

__all__ = [
    'RegistroView', 'ActivosView', 'PermisosView', 'HistorialView',
    'NominasView', 'TrabajadoresView', 'ExpedienteView', 'CalendarioMixin'
]