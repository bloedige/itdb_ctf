import reflex as rx
import asyncio
from itdb_ctf.auth.auth_state import AuthState
from itdb_ctf.evento.evento_logic import id_evento_abierto
from itdb_ctf.scoreboard.scoreboard_logic import scoreboard, opcion_evolucion

REFRESH = 5

class ScoreboardState(AuthState):
    ranking:list[dict] = []
    evolucion_opcion: dict = {}
    streaming:bool = False
    tick_token:int = 0

    @rx.var
    def no_solves(self) -> bool:
        return len(self.ranking) == 0
    @rx.var
    def solves(self) -> bool:
        return len(self.ranking) > 0

    @rx.var
    def evolucion_vacia(self) -> bool:
        return not self.evolucion_opcion

    @rx.event
    def refresh_ranking(self):
        guard = self.requiere_login()
        if guard: return guard
        id_route = self.router.page.params.get("id_evento_cerrado")
        if id_route:
            id_evento = int(id_route)
        else:
            id_evento =  id_evento_abierto()
        if not id_evento:
            self.ranking = []
            self.evolucion_opcion = {}
            return
        self.ranking = scoreboard(id_evento)
        self.evolucion_opcion = opcion_evolucion(id_evento, top=10)

    @rx.event
    def cargar_ranking(self):
        guard = self.requiere_login()
        if guard: return guard
        self.refresh_ranking()

    @rx.event(background=True)
    async def auto_refresh(self):
        async with self:
            self.tick_token += 1
            token = self.tick_token
            self.streaming = True
        while True:
            await asyncio.sleep(REFRESH)
            async with self:
                if not self.streaming or token != self.tick_token:
                    return
                self.refresh_ranking()

    @rx.event
    def stop_refresh(self):
        self.streaming = False