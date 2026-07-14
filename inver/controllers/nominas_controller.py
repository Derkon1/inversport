# inver/controllers/nominas_controller.py
from ..models import Nomina, RegistroProduccion


class NominasController:
    def __init__(self, nomina: Nomina):
        self.nomina = nomina

    def agregar_produccion(self, cedula, fecha, ticket, referencia, color, pares, pedido, precio):
        registro = RegistroProduccion(fecha, ticket, referencia, color, pares, pedido, precio)
        self.nomina.agregar_produccion(cedula, registro)

    def obtener_produccion(self, cedula):
        return self.nomina.obtener_produccion(cedula)

    def modificar_produccion(self, cedula, indice, registro):
        return self.nomina.modificar_produccion(cedula, indice, registro)

    def eliminar_produccion(self, cedula, indice):
        return self.nomina.eliminar_produccion(cedula, indice)