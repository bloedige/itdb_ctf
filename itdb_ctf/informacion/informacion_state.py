import reflex as rx
from itdb_ctf.auth.auth_state import AuthState
from itdb_ctf.informacion.informacion_logic import obterner_info_abierto
from itdb_ctf.evento.evento_logic import id_evento_abierto
from itdb_ctf.websockets import canales, suscriptor
from itdb_ctf.websockets.suscriptor import SuscriptorMixin

class InformacionState(SuscriptorMixin, AuthState):

    desc:str = ""

    @rx.event
    def cargar_info(self):
        guard = self.requiere_login()
        if guard: return guard
        self.desc = obterner_info_abierto()

    @rx.event(background=True)
    async def escuchar_info(self):
        await suscriptor.escuchar(
            self,
            clave_getter=lambda s: id_evento_abierto(),
            canales_getter=lambda s: (
                [canales.ch_evento(id_evento_abierto())] if id_evento_abierto() else []
            ),
            recargar=lambda s: s.cargar_info(),
        )

    @rx.event
    def parar_info(self):
        self.streaming = False
