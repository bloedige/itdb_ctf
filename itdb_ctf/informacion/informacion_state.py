import reflex as rx
from itdb_ctf.auth.auth_state import AuthState
from itdb_ctf.informacion.informacion_logic import obterner_info_abierto

class InformacionState(AuthState):

    desc:str = ""

    @rx.event
    def cargar_info(self):
        guard = self.requiere_login()
        if guard: return guard
        self.desc = obterner_info_abierto()
