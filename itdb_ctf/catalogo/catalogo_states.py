import reflex as rx
from itdb_ctf.auth.auth_state import AuthState
from itdb_ctf.components.form import toast_msg, success_msg
from itdb_ctf.evento.evento_logic import id_evento_abierto
from itdb_ctf.catalogo.envio_logic import enviar_flag
from itdb_ctf.catalogo.puntaje_logic import calcular_puntaje
from itdb_ctf.catalogo.catalogo_logic import cargar_catalogos, listar_retos, inscrito

class CatalogoState(AuthState):
    retos:list[dict] = []
    id_categoria_filtro:str = ""
    id_dificultad_filtro:str = ""
    categorias:list[tuple[str,str]] = []
    dificultades:list[tuple[str,str]] = []

    @rx.event
    def set_id_categoria_filtro(self, v:str):
        self.id_categoria_filtro = v
        return CatalogoState.cargar_retos

    @rx.event
    def set_id_dificultad_filtro(self, v:str):
        self.id_dificultad_filtro = v  
        return CatalogoState.cargar_retos

    def cargar_retos(self):
        guard = self.requiere_login()
        if guard: return guard
        id_evento = id_evento_abierto()
        if not id_evento or not inscrito(self.id_usuario, id_evento):
            self.retos = []
            self.categorias = self.dificultades = []
            return 
        catalogos = cargar_catalogos()
        self.categorias = catalogos["categorias"]
        self.dificultades = catalogos["dificultades"]
        cat = int(self.id_categoria_filtro) if self.id_categoria_filtro else None
        dif = int(self.id_dificultad_filtro) if self.id_dificultad_filtro else None
        self.retos = listar_retos(self.id_usuario, id_evento, cat, dif)


class EnvioFlagState(AuthState):
    flag: str = ""

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
        if not self.flag:
            return toast_msg("Escribe una flag.")
        id_evento = id_evento_abierto()
        if not id_evento:
            return rx.toast.error("Evento no disponible.")
        ok, msg = enviar_flag(self.id_usuario, id_reto, id_evento,self.flag)
        if not ok:
            return toast_msg(msg)
        self.flag = ""
        catalogo = await self.get_state(CatalogoState)
        catalogo.cargar_retos()
        return success_msg(msg)  
