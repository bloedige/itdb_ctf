import reflex as rx

from itdb_ctf.auth.auth_state import AuthState
from itdb_ctf.evento.evento_logic import id_evento_abierto
from itdb_ctf.catalogo.catalogo_logic import inscrito
from itdb_ctf.perfil.perfil_logic import (
    participa,
    perfil_datos,
    retos_resueltos,
    distribucion_categorias,
    reparto_puntos,
    aciertos_errores,
)
from itdb_ctf.scoreboard.scoreboard_logic import opcion_evolucion_usuario
from itdb_ctf.websockets.freeze_logic import corte_freeze


class PerfilBaseState(AuthState):
    datos: dict = {}
    resueltos: list[dict] = []
    distribucion: list[dict] = []
    reparto: list[dict] = []
    evolucion_opcion: dict = {}
    envios: list[dict] = []

    @rx.var
    def hay_datos(self) -> bool:
        return bool(self.datos.get("inscrito"))

    @rx.var
    def sin_resueltos(self) -> bool:
        return len(self.resueltos) == 0

    @rx.var
    def sin_distribucion(self) -> bool:
        return len(self.distribucion) == 0

    @rx.var
    def sin_reparto(self) -> bool:
        return len(self.reparto) == 0

    @rx.var
    def sin_evolucion(self) -> bool:
        return not self.evolucion_opcion

    @rx.var
    def sin_envios(self) -> bool:
        return len(self.envios) == 0

    def _sin_datos(self):
        self.datos = {"inscrito": False}
        self.resueltos = []
        self.distribucion = []
        self.reparto = []
        self.evolucion_opcion = {}
        self.envios = []

    def _cargar(self, id_evento: int):
        # el freeze congela la curva propia del estudiante (no la del staff)
        corte = corte_freeze(id_evento) if self.codigo_rol == "user" else None
        self.datos = perfil_datos(self.id_usuario, id_evento)
        self.resueltos = retos_resueltos(self.id_usuario, id_evento)
        self.distribucion = distribucion_categorias(self.id_usuario, id_evento)
        self.reparto = reparto_puntos(self.id_usuario, id_evento)
        self.evolucion_opcion = opcion_evolucion_usuario(id_evento, self.id_usuario, corte)
        self.envios = aciertos_errores(self.id_usuario, id_evento)


class PerfilGeneralState(PerfilBaseState):
    @rx.event
    def cargar_perfil(self):
        guard = self.requiere_login()
        if guard:
            return guard
        id_ev = id_evento_abierto()
        if not id_ev or not inscrito(self.id_usuario, id_ev):
            self._sin_datos()
            return
        self._cargar(id_ev)


class PerfilEventoCerradoState(PerfilBaseState):
    @rx.event
    def cargar_perfil(self):
        guard = self.requiere_login()
        if guard:
            return guard
        id_ev = int(self.router.page.params.get("id_evento_cerrado", 0))
        if not participa(self.id_usuario, id_ev):
            self._sin_datos()
            return
        self._cargar(id_ev)


class PerfilPublicoBaseState(PerfilBaseState):
    """Perfil de OTRO usuario, visto desde el link del scoreboard. Reusa
    `perfil_contenido` (con `mostrar_email=False`) cargando por el `id_usuario`
    de la URL en vez de `self.id_usuario`."""

    def _id_objetivo(self) -> int:
        # OJO: el segmento de ruta se llama `id_objetivo`, no `id_usuario` — ese
        # nombre ya lo usa `AuthState.id_usuario` (el propio usuario logueado) y
        # Reflex no deja que un arg de ruta dinámica choque con un var existente.
        try:
            return int(self.router.page.params.get("id_objetivo", 0))
        except (TypeError, ValueError):
            return 0

    def _cargar_para(self, id_evento: int, id_usuario: int):
        corte = corte_freeze(id_evento) if self.codigo_rol == "user" else None
        self.datos = perfil_datos(id_usuario, id_evento)
        self.resueltos = retos_resueltos(id_usuario, id_evento)
        self.distribucion = distribucion_categorias(id_usuario, id_evento)
        self.reparto = reparto_puntos(id_usuario, id_evento)
        self.evolucion_opcion = opcion_evolucion_usuario(id_evento, id_usuario, corte)
        self.envios = aciertos_errores(id_usuario, id_evento)


class PerfilPublicoAbiertoState(PerfilPublicoBaseState):
    @rx.event
    def cargar_perfil_publico(self):
        guard = self.requiere_login()
        if guard:
            return guard
        id_ev = id_evento_abierto()
        id_usr = self._id_objetivo()
        if not id_ev or not id_usr or not inscrito(id_usr, id_ev):
            self._sin_datos()
            return
        self._cargar_para(id_ev, id_usr)


class PerfilPublicoCerradoState(PerfilPublicoBaseState):
    @rx.event
    def cargar_perfil_publico(self):
        guard = self.requiere_login()
        if guard:
            return guard
        id_ev = int(self.router.page.params.get("id_evento_cerrado", 0))
        id_usr = self._id_objetivo()
        if not id_ev or not id_usr or not participa(id_usr, id_ev):
            self._sin_datos()
            return
        self._cargar_para(id_ev, id_usr)
