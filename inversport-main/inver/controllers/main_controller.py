from ..models import Nomina
from ..views import AppNomina


class MainController:
    def __init__(self, root):
        self.root = root
        self.nomina = Nomina()
        self.app = AppNomina(root)
        self.app.nomina = self.nomina

    def run(self):
        self.root.mainloop()