import reflex as rx
from itdb_ctf.auth.auth_state import AuthState

class EventoCerradoPerfilState(AuthState):
    @rx.event
    def caragar_perfil(self):
        guard = self.requiere_login()
        if guard: return guard

# completar 