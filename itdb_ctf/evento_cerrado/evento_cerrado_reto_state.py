import reflex as rx
from itdb_ctf.auth.auth_state import AuthState
from itdb_ctf.evento.evento_logic import obtener_evento
from itdb_ctf.catalogo.catalogo_logic import cargar_catalogos, listar_retos, listar_pistas
from itdb_ctf.core.envio_logic import enviar_flag
from itdb_ctf.core.compra_logic import adquirir_pista
from itdb_ctf.evento_cerrado.evento_cerrado_logic import acceso_evento_cerrado
from itdb_ctf.components.form import toast_msg, success_msg
from itdb_ctf.websockets import canales, suscriptor
from itdb_ctf.websockets.suscriptor import SuscriptorMixin

class EventoCerradoRetoState (SuscriptorMixin, AuthState):
    acceso:bool = False
    motivo:str = ""
    titulo:str = ""
    retos:list[dict] = []
    id_categoria_filtro:str = ""
    id_dificultad_filtro:str = ""
    categorias:list[tuple[str,str]] = ""
    dificultades:list[tuple[str,str]] = ""

    def _id_ev(self) -> int:
        try:
            return int(self.router.page.params.get("id_evento_cerrado", 0))
        except (TypeError, ValueError):
            return 0

    @rx.event(background=True)
    async def escuchar_retos(self):
        await suscriptor.escuchar(
            self,
            clave_getter=lambda s: s._id_ev() or None,
            canales_getter=lambda s: [canales.ch_evento(s._id_ev())] if s._id_ev() else [],
            recargar=lambda s: s.cargar_retos(),
        )

    @rx.event
    def parar_retos(self):
        self.streaming = False

    @rx.event
    def set_id_categoria_filtro(self, v:str):
        self.id_categoria_filtro = v
        return EventoCerradoRetoState.cargar_retos

    @rx.event
    def set_id_dificultad_filtro(self, v:str):
        self.id_dificultad_filtro = v
        return EventoCerradoRetoState.cargar_retos

    @rx.event
    def cargar_retos(self):
        guard = self.requiere_login()
        if guard: return guard
        id_ev = int(self.router.page.params.get("id_evento_cerrado", 0))
        ok, msg = acceso_evento_cerrado(id_ev, self.id_usuario)
        self.acceso = ok
        self.motivo = msg
        if not ok:
            self.retos = []
            self.categorias = self.dificultades = []
            return
        ev = obtener_evento(id_ev)
        self.titulo = ev.titulo if ev else ""
        catalogos = cargar_catalogos()
        self.categorias = catalogos["categorias"]
        self.dificultades = catalogos["dificultades"]
        cat = int(self.id_categoria_filtro) if self.id_categoria_filtro else None
        dif = int(self.id_dificultad_filtro) if self.id_dificultad_filtro else None
        self.retos = listar_retos(self.id_usuario, id_ev, cat, dif)

class EventoCerradoEnvioFlagState(AuthState):
    flag:str = ""

    @rx.event
    def set_flag(self, v:str):
        self.flag = v

    @rx.event
    def drop_flag(self):
        self.flag = ""

    @rx.event
    async def enviar_flag(self,id_reto:int):
        guard = self.requiere_login()
        if guard: return guard
        if self.codigo_rol != "user": #llevar esta parte a logic
            return rx.toast.error("Solo estudiantes pueden enviar flags.")
        if not self.flag:
            return toast_msg("Ingresa una flag.")
        id_ev = int(self.router.page.params.get("id_evento_cerrado", 0))
        if not id_ev:
            return toast_msg("Evento no disponible")
        ok, msg = enviar_flag(self.id_usuario, id_reto, id_ev, self.flag)
        if not ok:
            return toast_msg(msg)
        self.drop_flag()
        catalogo = await self.get_state(EventoCerradoRetoState)
        catalogo.cargar_retos()
        return success_msg(msg)

class EventoCerradoListarPistaState(SuscriptorMixin, AuthState):
    pistas: list[dict] = []
    id_reto_abierto: int = 0

    def _id_ev(self) -> int:
        try:
            return int(self.router.page.params.get("id_evento_cerrado", 0))
        except (TypeError, ValueError):
            return 0

    @rx.event
    def cargar_pistas(self, id_reto:int):
        self.id_reto_abierto = id_reto
        id_ev = self._id_ev()
        if not id_ev:
            self.pistas = []
            return
        self.pistas = listar_pistas(self.id_usuario, id_ev, id_reto)

    def _recargar_abierto(self):
        if self.id_reto_abierto:
            self.cargar_pistas(self.id_reto_abierto)

    @rx.event(background=True)
    async def escuchar_pistas_cerrado(self):
        await suscriptor.escuchar(
            self,
            clave_getter=lambda s: s._id_ev() or None,
            canales_getter=lambda s: [canales.ch_evento(s._id_ev())] if s._id_ev() else [],
            recargar=lambda s: s._recargar_abierto(),
        )

    @rx.event
    def parar_pistas_cerrado(self):
        self.streaming = False

    @rx.event
    def comprar_pista(self, id_reto:int, id_pista:int):
        guard = self.requiere_login()
        if guard: return guard
        if self.codigo_rol != "user":#llevar esta parte a logic
            return toast_msg("Solo estudiantes pueden comprar pistas.")
        id_ev = int(self.router.page.params.get("id_evento_cerrado", 0))
        if not id_ev:
            return toast_msg("Evento inexistente.")
        ok, msg = adquirir_pista(self.id_usuario, id_ev, id_reto, id_pista)
        if not ok:
            return toast_msg(msg)
        self.cargar_pistas(id_reto)
        return success_msg(msg)
            

        