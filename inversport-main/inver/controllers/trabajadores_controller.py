from ..models import Nomina


class TrabajadoresController:
    def __init__(self, nomina: Nomina):
        self.nomina = nomina

    def agregar_trabajador(self, cedula, nombres, apellidos, cargo):
        return self.nomina.agregar_trabajador(cedula, nombres, apellidos, cargo)

    def actualizar_cargo(self, cedula, nuevo_cargo):
        return self.nomina.actualizar_cargo(cedula, nuevo_cargo)

    def eliminar_trabajador(self, cedula):
        return self.nomina.eliminar_trabajador(cedula)

    def listar_trabajadores(self):
        return self.nomina.get_trabajadores_lista()