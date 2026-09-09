import reflex as rx

from itdb_ctf.auth.auth_state import AuthState
from itdb_ctf.dashboards.retos_dashboard_logic import (
    resumen_retos,
    listar_eventos_opciones,
    retos_desglose_categoria,
    retos_desglose_dificultad,
    retos_por_modo,
    retos_creados_por_mes,
    retos_resoluciones_por_evento,
    retos_por_autor,
)


class RetosDashboardState(AuthState):
    resumen: dict = {}
    categoria: list[dict] = []
    dificultad: list[dict] = []
    modo: list[dict] = []
    creados_mes: list[dict] = []
    eventos: list[dict] = []
    autores: list[dict] = []

    eventos_opciones: list[list[str]] = []
    id_evento_sel: str = "todos"
    mis_retos: bool = False

    @rx.var
    def sin_eventos(self) -> bool:
        return len(self.eventos) == 0

    @rx.var
    def es_autor(self) -> bool:
        return self.codigo_rol == "autor"

    @rx.var
    def es_global(self) -> bool:
        return self.id_evento_sel == "todos"

    @rx.var
    def solo_mios(self) -> bool:
        return self.mis_retos or self.codigo_rol == "autor"

    @rx.var
    def mostrar_autores(self) -> bool:
        return not self.solo_mios

    def _cargar(self):
        id_ev = None if self.id_evento_sel == "todos" else int(self.id_evento_sel)
        id_au = self.id_usuario if self.solo_mios else None
        self.resumen = resumen_retos(id_ev, id_au)
        self.categoria = retos_desglose_categoria(id_ev, id_au)
        self.dificultad = retos_desglose_dificultad(id_ev, id_au)
        self.modo = retos_por_modo(id_ev, id_au)
        self.creados_mes = retos_creados_por_mes(id_ev, id_au)
        self.eventos = retos_resoluciones_por_evento(id_ev, id_au)
        self.autores = retos_por_autor(id_ev) if not self.solo_mios else []

    @rx.event
    def cargar_dashboard(self):
        guard = self.requiere_staff()
        if guard:
            return guard
        self.eventos_opciones = [list(t) for t in listar_eventos_opciones()]
        self._cargar()

    @rx.event
    def set_evento(self, v: str):
        self.id_evento_sel = v
        self._cargar()

    @rx.event
    def set_mis_retos(self, v: bool):
        self.mis_retos = v
        self._cargar()
