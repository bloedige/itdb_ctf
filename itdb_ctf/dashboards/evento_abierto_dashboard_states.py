import reflex as rx

from itdb_ctf.auth.auth_state import AuthState
from itdb_ctf.evento.evento_logic import id_evento_abierto
from itdb_ctf.scoreboard.scoreboard_logic import scoreboard, scoreboard_graph
from itdb_ctf.dashboards.evento_abierto_dashboard_logic import (
    resumen_abierto,
    desglose_categoria,
    desglose_dificultad,
    actividad_diaria,
    inscripciones_por_mes,
    ranking_retos_resoluciones,
)


class EventoAbiertoDashboardState(AuthState):
    resumen: dict = {}
    categoria: list[dict] = []
    dificultad: list[dict] = []
    actividad: list[dict] = []
    inscripciones_mes: list[dict] = []
    ranking: list[dict] = []
    evol_data: list[dict] = []
    evol_series: list[dict] = []
    ranking_retos: list[dict] = []

    @rx.var
    def hay_evento(self) -> bool:
        return bool(self.resumen.get("hay_evento"))

    @rx.var
    def hay_ranking(self) -> bool:
        return len(self.ranking) > 0

    @rx.var
    def retos_mas_resueltos(self) -> list[dict]:
        """Top 10 con más resoluciones (los más fáciles en la práctica)."""
        return sorted(
            self.ranking_retos,
            key=lambda r: (-r["resoluciones"], r["puntaje"]),
        )[:10]

    @rx.var
    def retos_mas_dificiles(self) -> list[dict]:
        """Top 10 con menos resoluciones (los más difíciles / sin resolver)."""
        return sorted(
            self.ranking_retos,
            key=lambda r: (r["resoluciones"], -r["puntaje"]),
        )[:10]

    @rx.event
    def cargar_dashboard(self):
        guard = self.requiere_admin()
        if guard:
            return guard
        self.resumen = resumen_abierto()
        self.categoria = desglose_categoria()
        self.dificultad = desglose_dificultad()
        self.actividad = actividad_diaria()
        self.inscripciones_mes = inscripciones_por_mes()
        self.ranking_retos = ranking_retos_resoluciones()
        id_ev = id_evento_abierto()
        if id_ev:
            self.ranking = scoreboard(id_ev)[:10]
            self.evol_data, self.evol_series = scoreboard_graph(id_ev, top=10)
        else:
            self.ranking = []
            self.evol_data, self.evol_series = [], []

    @rx.event
    def actualizar(self):
        return EventoAbiertoDashboardState.cargar_dashboard
