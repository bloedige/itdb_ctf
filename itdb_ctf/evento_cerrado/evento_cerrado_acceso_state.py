"""Control de acceso EN VIVO a las páginas de evento cerrado.

Un estudiante puede perder el acceso a un evento cerrado en cualquier momento
(un admin lo descalifica, el evento concluye…). Este state re-verifica
`acceso_evento_cerrado` cuando llega un mensaje al canal `itdb:insc:{id}` y baja
`acceso` a `False` → la página muestra el aviso y lo saca a `/eventos`.

Solo aplica a `codigo_rol == "user"`. El staff siempre tiene acceso.
"""

import reflex as rx

from itdb_ctf.auth.auth_state import AuthState
from itdb_ctf.evento_cerrado.evento_cerrado_logic import acceso_evento_cerrado
from itdb_ctf.websockets import canales, suscriptor


class EventoCerradoAccesoState(AuthState):
    acceso: bool = True
    motivo: str = ""
    streaming: bool = False
    tick_token: int = 0

    def _id_ev(self) -> int:
        try:
            return int(self.router.page.params.get("id_evento_cerrado", 0))
        except (TypeError, ValueError):
            return 0

    @rx.event
    def verificar(self):
        guard = self.requiere_login()
        if guard:
            return guard
        if self.codigo_rol != "user":
            self.acceso, self.motivo = True, ""
            return
        id_ev = self._id_ev()
        if not id_ev:
            self.acceso, self.motivo = True, ""
            return
        ok, msg = acceso_evento_cerrado(id_ev, self.id_usuario)
        self.acceso = ok
        self.motivo = msg or "No tenés acceso a este evento."

    @rx.event(background=True)
    async def escuchar_acceso(self):
        await suscriptor.escuchar(
            self,
            clave_getter=lambda s: s._id_ev() or None,
            canales_getter=lambda s: [canales.ch_inscripcion(s._id_ev())] if s._id_ev() else [],
            recargar=lambda s: s.verificar(),
        )

    @rx.event
    def parar_acceso(self):
        self.streaming = False
