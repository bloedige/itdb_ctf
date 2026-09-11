import reflex as rx

from itdb_ctf.auth.auth_state import AuthState
from itdb_ctf.evento.evento_logic import id_evento_abierto
from itdb_ctf.scoreboard.scoreboard_logic import ranking_y_evolucion
from itdb_ctf.websockets import canales, suscriptor
from itdb_ctf.websockets.freeze_logic import corte_freeze


class ScoreboardState(AuthState):
    ranking: list[dict] = []
    evolucion_opcion: dict = {}
    streaming: bool = False
    tick_token: int = 0

    @rx.var
    def no_solves(self) -> bool:
        return len(self.ranking) == 0

    @rx.var
    def solves(self) -> bool:
        return len(self.ranking) > 0

    @rx.var
    def evolucion_vacia(self) -> bool:
        return not self.evolucion_opcion

    def _id_evento(self) -> int | None:
        id_route = self.router.page.params.get("id_evento_cerrado")
        return int(id_route) if id_route else id_evento_abierto()

    @rx.var
    def perfil_base(self) -> str:
        """Prefijo para el link "ver perfil" de una fila del ranking: dentro de
        un evento cerrado apunta a `/evento/{id}/perfil/{id_usuario}`, en el
        abierto a `/perfil/{id_usuario}`."""
        id_ev_cerrado = self.router.page.params.get("id_evento_cerrado")
        return f"/evento/{id_ev_cerrado}/perfil" if id_ev_cerrado else "/perfil"

    def _aplica_freeze(self) -> bool:
        """El corte de freeze aplica a estudiantes, o a staff con `?preview=1`
        (para que un admin vea el scoreboard tal como lo ve el jugador)."""
        if self.codigo_rol == "user":
            return True
        return self.router.page.params.get("preview") == "1"

    @rx.event
    def refresh_ranking(self):
        guard = self.requiere_login()
        if guard:
            return guard
        id_evento = self._id_evento()
        if not id_evento:
            self.ranking = []
            self.evolucion_opcion = {}
            return
        corte = corte_freeze(id_evento) if self._aplica_freeze() else None
        self.ranking, self.evolucion_opcion = ranking_y_evolucion(id_evento, corte)

    @rx.event
    def cargar_ranking(self):
        guard = self.requiere_login()
        if guard:
            return guard
        self.refresh_ranking()

    @rx.event(background=True)
    async def escuchar_scoreboard(self):
        """Suscripción Redis pub/sub (push). Degrada a polling si no hay Redis."""
        await suscriptor.escuchar(
            self,
            clave_getter=lambda s: s._id_evento(),
            canales_getter=lambda s: (
                [canales.ch_scoreboard(s._id_evento()), canales.ch_freeze(s._id_evento())]
                if s._id_evento() else []
            ),
            recargar=lambda s: s.refresh_ranking(),
        )

    @rx.event
    def stop_refresh(self):
        self.streaming = False
