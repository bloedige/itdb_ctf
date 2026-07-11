import reflex as rx 
from sqlmodel import select, Session
from itdb_ctf.db import engine
from itdb_ctf.models import Evento, ModoPuntaje, Categoria, Dificultad
from itdb_ctf.asociar import asociar_logic as asociar

from itdb_ctf.auth.auth_state import AuthState

class AsociarState(AuthState):
    tab:str = "asociar"   #gestionar / asciar
    id_categoria_filtro:str = ""
    id_modo_filtro:str = ""
    id_dificultad_filtro:str = ""
    aislados_bool:bool = False

    categorias:list[tuple[str,str]] = []
    modos:list[tuple[str,str]] = []
    dificultades:list[tuple[str,str]] = []
    eventos_dest:list[tuple[str,str]] = []
    eventos_gest:list[tuple[str,str]] = []

    candidatos:list[dict] = []
    retos_gest:list[dict] = []
    id_evento_gest:str = ""

    carrito:list[dict] = []
    retos_dest:list[dict] = []
    id_evento_dest:str = ""

    id_dialog: int = 0
    titulo_dialog:str = "" 
    override_bool:bool = False
    override_valor:str = ""
    pts_init_dialog:int = 0

    def set_id_categoria_filtro(self, v:str):
        self.id_categoria_filtro = v
        return AsociarState.cargar_candidatos
    def set_id_modo_filtro(self, v:str):
        self.id_modo_filtro = v
        return AsociarState.cargar_candidatos
    def set_id_dificultad_filtro(self, v:str):
        self.id_dificultad_filtro = v
        return AsociarState.cargar_candidatos
    def set_aislados_bool(self, v:bool):
        self.aislados_bool = v
        return AsociarState.cargar_candidatos
    def set_id_evento_dest(self, v:str):
        self.id_evento_dest = v
        return AsociarState.cargar_destino
    def set_id_evento_gest(self, v:str):
        self.id_evento_gest = v
        return AsociarState.cargar_gestion
    
    def set_override_valor(self, v:str):
        self.override_valor = v

    def set_tab(self, v:str):
        self.tab = v
        self.carrito = []
        self.retos_gest=[]
        self.id_evento_gest = ""

    @rx.var
    def ids_in_carrito(self) -> list[int]:
        return[item['id'] for item in self.carrito]
    
    @rx.var
    def activar_asociar(self) -> bool:
        return True if self.carrito == [] else False
    
    @rx.var 
    def modo(self) -> bool:
        return False if self.tab == "asociar" else True
    
    @rx.var
    def override(self) -> bool:
        return not self.override_bool

    def cargar_todo(self):
        guard = self.requiere_staff()
        if guard: return guard
        self.id_evento_gest = ""
        self.retos_gest = []
        self.id_evento_dest = ""
        self.retos_dest = []
        self.carrito = []
        self.tab = "asociar" 
        with Session(engine) as s:
            self.categorias = [(str(c.id_categoria),c.etiqueta)for c in s.exec(select(Categoria)).all()] 
            self.modos = [(str(m.id_modo_puntaje),m.etiqueta)for m in s.exec(select(ModoPuntaje)).all()]
            self.dificultades = [(str(d.id_dificultad),d.etiqueta)for d in s.exec(select(Dificultad)).all()]
            dest, gest = [], []
            for ev in s.exec(select(Evento)).all():
                est = asociar.estado_evento(ev)
                if est in ("abierto","futuro"):
                    dest.append((str(ev.id_evento),ev.titulo))
                if est == "futuro":
                    gest.append((str(ev.id_evento),ev.titulo))
            self.eventos_dest = dest
            self.eventos_gest = gest
        self.cargar_candidatos()

    def cargar_candidatos(self):
        dest = int(self.id_evento_dest) if self.id_evento_dest else 0
        cat = int(self.id_categoria_filtro) if self.id_categoria_filtro else None
        mod =  int(self.id_modo_filtro) if self.id_modo_filtro else None
        dif = int(self.id_dificultad_filtro) if self.id_dificultad_filtro else None
        self.candidatos = asociar.retos_asociables(dest, cat, mod, dif, aislados=self.aislados_bool)

    def cargar_destino(self):
        if self.id_evento_dest:
            self.retos_dest = asociar.retos_evento(self.id_evento_dest)
        else:
            self.retos_dest= []
        self.cargar_candidatos()

    def open_dialog(self, id_reto:int, titulo:str, puntaje_inicial ):
        self.id_dialog = id_reto
        self.titulo_dialog = titulo
        self.override_bool = False
        self.override_valor = ""
        self.pts_init_dialog = puntaje_inicial

    def set_override_mode(self, v:str):
        if v == "ove":
            self.override_bool = True
        else:
            self.override_bool = False 
            self.override_valor = ""

    def confirmar_agregar(self):
        if any(item['id'] == self.id_dialog for item in self.carrito):
            return rx.toast.error(f"El reto {self.titulo_dialog} ya se encuetra en el carrito")
        ov = int(self.override_valor) if (self.override_valor and self.override_bool) else None
        self.carrito = self.carrito + [{
            "id":self.id_dialog,
            "titulo":self.titulo_dialog,
            "override":ov,
            "default":self.pts_init_dialog
        }]
        return rx.toast.success(f"se agrego {self.titulo_dialog} "+(f"con: {ov} pts. (Override)" if ov else f"con: {self.pts_init_dialog} pts. (Default)"))

    def quitar_carrito(self, id_reto:int):
        self.carrito = [i for i in self.carrito if i['id'] != id_reto]

    def vaciar_carrito(self):
        self.carrito = []

    def guardar_carrito(self):
        if not self.id_evento_dest:
            return rx.toast.warning("Seleccione un evento destino.")
        if not self.carrito:
            return rx.toast.info("Sin retos para asociar a evento.")
        dest = int(self.id_evento_dest)
        exitos = 0
        fallos = []
        for item in self.carrito:
            try:
                asociar.asociar_reto(item['id'], dest, item['override'])
                exitos += 1
            except ValueError as e:
                fallos.append(f"{item['titulo']} : {e}")
        self.carrito = []
        self.cargar_destino()
        self.cargar_candidatos()
        return rx.toast.info(f"{exitos} reto(s) asociado(s)" + (f" Fallaron: {' '.join(fallos)}" if fallos else ""))

    def cargar_gestion(self):
        if self.id_evento_gest:
            self.retos_gest = asociar.retos_evento(int(self.id_evento_gest))
        else:
            self.retos_gest = []

    def quitar_retos(self, id_reto):
        try:
            if asociar.quitar_reto(id_reto, int(self.id_evento_gest)):
                self.cargar_gestion()
                toast = rx.toast.success("Reto desvinculado de evento")
            else:
                toast =  rx.toast.error("No se encontro asociación")  
        except ValueError as e:
            self.cargar_gestion()
            toast = rx.toast.error(str(e))

        return toast
