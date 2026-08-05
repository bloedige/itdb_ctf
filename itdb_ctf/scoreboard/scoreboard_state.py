import reflex as rx
from itdb_ctf.auth.auth_state import AuthState
from itdb_ctf.evento.evento_logic import id_evento_abierto
from itdb_ctf.scoreboard.scoreboard_logic import scoreboard, scoreboard_graph

class ScoreboardState(AuthState):
    ranking:list[dict] = []
    grafica: list[dict] = []
    lineas: list[str] = []

    @rx.var
    def no_solves(self) -> bool:
        return len(self.ranking) == 0
    
    @rx.var
    def solves(self) -> bool:
        return len(self.ranking) > 0

    @rx.event
    def cargar_ranking(self):
        guard = self.requiere_login()
        if guard: return guard
        id_evento = id_evento_abierto()
        if not id_evento:
            self.ranking = []
            self.grafica = []
            self.lineas = []
            return
        self.ranking = scoreboard(id_evento)
        self.grafica, self.lineas = scoreboard_graph(id_evento)