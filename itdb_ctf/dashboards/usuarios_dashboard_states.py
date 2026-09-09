import reflex as rx

from itdb_ctf.auth.auth_state import AuthState
from itdb_ctf.dashboards.usuarios_dashboard_logic import (
    resumen_usuarios,
    usuarios_por_rol,
    usuarios_por_metodo,
    registros_por_mes,
    top_solvers,
    usuarios_sin_participar,
    descalificados_lista,
    autores_por_retos,
    listar_eventos_opciones,
)


class UsuariosDashboardState(AuthState):
    resumen: dict = {}
    roles: list[dict] = []
    metodos: list[dict] = []
    registros_mes: list[dict] = []
    solvers: list[dict] = []
    sin_participar: list[dict] = []
    descalificados: list[dict] = []
    autores: list[dict] = []

    eventos_opciones: list[list[str]] = []
    id_evento_sel: str = "todos"

    @rx.var
    def es_global(self) -> bool:
        return self.id_evento_sel == "todos"

    @rx.var
    def sin_solvers(self) -> bool:
        return len(self.solvers) == 0

    @rx.var
    def sin_descalificados(self) -> bool:
        return len(self.descalificados) == 0

    @rx.var
    def todos_participan(self) -> bool:
        return len(self.sin_participar) == 0

    @rx.var
    def sin_autores(self) -> bool:
        return len(self.autores) == 0

    def _cargar(self):
        id_ev = None if self.id_evento_sel == "todos" else int(self.id_evento_sel)
        # padrón — siempre global
        self.roles = usuarios_por_rol()
        self.metodos = usuarios_por_metodo()
        self.registros_mes = registros_por_mes()
        self.sin_participar = usuarios_sin_participar()
        # participación — filtrado por evento
        self.resumen = resumen_usuarios(id_ev)
        self.solvers = top_solvers(id_ev)
        self.descalificados = descalificados_lista(id_ev)
        self.autores = autores_por_retos(id_ev)

    @rx.event
    def cargar_dashboard(self):
        guard = self.requiere_admin()
        if guard:
            return guard
        self.eventos_opciones = [list(t) for t in listar_eventos_opciones()]
        self._cargar()

    @rx.event
    def set_evento(self, v: str):
        self.id_evento_sel = v
        self._cargar()
