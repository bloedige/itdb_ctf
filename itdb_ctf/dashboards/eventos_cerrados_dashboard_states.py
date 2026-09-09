import reflex as rx

from itdb_ctf.auth.auth_state import AuthState
from itdb_ctf.scoreboard.scoreboard_logic import scoreboard, opcion_evolucion
from itdb_ctf.dashboards import dashboard_metricas_logic as m
from itdb_ctf.dashboards.eventos_cerrados_dashboard_logic import (
    listar_eventos_cerrados,
    info_evento,
    actividad_evento,
    feed_resoluciones,
)


class EventosCerradosDashboardState(AuthState):
    eventos: list[list[str]] = []
    id_sel: str = ""
    info: dict = {}
    resumen: dict = {}
    categoria: list[dict] = []
    dificultad: list[dict] = []
    actividad: list[dict] = []
    ranking: list[dict] = []
    evol_opcion: dict = {}
    feed: list[dict] = []

    @rx.var
    def hay_eventos(self) -> bool:
        return len(self.eventos) > 0

    @rx.var
    def hay_seleccion(self) -> bool:
        return bool(self.info.get("hay_evento"))

    @rx.var
    def evento_activo(self) -> bool:
        return self.info.get("estado") == "activo"

    @rx.var
    def esta_congelado(self) -> bool:
        return bool(self.info.get("freeze"))

    @rx.var
    def hay_ranking(self) -> bool:
        return len(self.ranking) > 0

    @rx.var
    def hay_feed(self) -> bool:
        return len(self.feed) > 0

    def _recargar(self):
        if not self.id_sel:
            self.info = {}
            self.resumen = {}
            self.categoria = self.dificultad = self.actividad = []
            self.ranking = self.feed = []
            self.evol_opcion = {}
            return
        id_ev = int(self.id_sel)
        self.info = info_evento(id_ev)
        self.resumen = m.resumen_evento(id_ev)
        self.categoria = m.desglose_categoria(id_ev)
        self.dificultad = m.desglose_dificultad(id_ev)
        self.actividad = actividad_evento(id_ev)
        self.feed = feed_resoluciones(id_ev)
        self.ranking = scoreboard(id_ev)[:10]
        self.evol_opcion = opcion_evolucion(id_ev, top=10)

    @rx.event
    def cargar_todo(self):
        guard = self.requiere_admin()
        if guard:
            return guard
        self.eventos = [list(t) for t in listar_eventos_cerrados()]
        ids = {e[0] for e in self.eventos}
        if self.id_sel not in ids:
            self.id_sel = self.eventos[0][0] if self.eventos else ""
        self._recargar()

    @rx.event
    def set_evento(self, v: str):
        self.id_sel = v
        self._recargar()

    @rx.event
    def actualizar(self):
        return EventosCerradosDashboardState.cargar_todo

    @rx.event
    def congelar(self):
        """Placeholder: aún no congela el scoreboard."""
        pass
