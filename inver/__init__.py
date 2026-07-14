# inver/__init__.py
from .models import Trabajador, Nomina, RegistroEntrada, RegistroProduccion, Permiso
from .views import AppNomina
from .controllers import MainController

__all__ = [
    'Trabajador', 'Nomina', 'RegistroEntrada', 'RegistroProduccion', 'Permiso',
    'AppNomina', 'MainController'
]