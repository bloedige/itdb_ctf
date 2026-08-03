import reflex as rx 
from itdb_ctf.components.form import toast_msg
from itdb_ctf.asociar import asociar_logic as asociar
from itdb_ctf.auth.auth_state import AuthState

class AsociarState(AuthState):
    tab:str = "asociar"   #gestionar / asciar"
    busqueda:str = ""
    id_categoria_filtro:str = ""
    id_dificultad_filtro:str = ""
    id_modo_filtro:str = ""
    aislados_bool:bool = False
    
    busqueda_gest:str = ""
    id_categoria_gest_filtro:str = ""
    id_dificultad_gest_filtro:str = ""
    id_modo_gest_filtro:str = ""
    eventos_gest:list[tuple[str,str]] = []   
    categorias:list[tuple[str,str]] = []
    modos:list[tuple[str,str]] = []
    dificultades:list[tuple[str,str]] = []
    eventos_dest:list[tuple[str,str]] = []
    
    retos_gest:list[dict] = []
    candidatos:list[dict] = []
    
    id_evento_gest:str = ""
    carrito:list[dict] = []
    prev_retos:list[dict] = []
    id_evento_dest:str = ""

    id_dialog: int = 0
    titulo_dialog:str = "" 
    dialog_bool:bool = False
    override_bool:bool = False
    id_modo_puntaje:str = ""
    puntaje_inicial:str = ""
    puntaje_minimo:str = ""
    modo_def:int = 0
    inicial_def:int = 0
    minimo_def:int = 0
    @rx.event
    def set_busqueda(self, v:str):
        self.busqueda = v
        return AsociarState.cargar_candidatos
    @rx.event
    def set_id_categoria_filtro(self, v:str):
        self.id_categoria_filtro = v
        return AsociarState.cargar_candidatos
    @rx.event
    def set_id_modo_filtro(self, v:str):
        self.id_modo_filtro = v
        return AsociarState.cargar_candidatos
    @rx.event
    def set_id_dificultad_filtro(self, v:str):
        self.id_dificultad_filtro = v
        return AsociarState.cargar_candidatos
    @rx.event
    def set_aislados_bool(self, v:bool):
        self.aislados_bool = v
        return AsociarState.cargar_candidatos
    @rx.event
    def set_id_evento_dest(self, v:str):
        self.id_evento_dest = v
        return [AsociarState.cargar_candidatos, AsociarState.cargar_destino]
    @rx.event
    def set_id_evento_gest(self, v:str):
        self.id_evento_gest = v
        return AsociarState.cargar_gestion
    @rx.event
    def set_busqueda_gest(self, v:str):
        self.busqueda_gest = v
        return AsociarState.cargar_gestion
    @rx.event
    def set_id_categoria_gest_filtro(self, v:str):
        self.id_categoria_gest_filtro = v
        return AsociarState.cargar_gestion
    @rx.event
    def set_id_dificultad_gest_filtro(self, v:str):
        self.id_dificultad_gest_filtro = v
        return AsociarState.cargar_gestion
    @rx.event
    def set_id_modo_gest_filtro(self, v:str):
        self.id_modo_gest_filtro = v
        return AsociarState.cargar_gestion
    @rx.event
    def set_id_modo_puntaje(self, v:str):
        self.id_modo_puntaje = v
    @rx.event
    def set_puntaje_inicial(self, v:str):
        self.puntaje_inicial = v
    @rx.event
    def set_puntaje_minimo(self, v:str):
        self.puntaje_minimo = v
    @rx.event
    def set_tab(self, v:str):
        self.tab = v
        self.carrito = []
        self.retos_gest=[]
        self.id_evento_gest = ""
    @rx.event
    def set_override_mode(self, v:str):
            if v == "ove":
                self.override_bool = True
            else:
                self.override_bool = False 

    @rx.var
    def ids_in_carrito(self) -> list[int]:
        return [item['id'] for item in self.carrito]
    
    @rx.var
    def activar_asociar(self) -> bool:
        return self.carrito == [] 
    
    @rx.var 
    def modo(self) -> bool:
        return self.tab == "gestionar"
    
    @rx.var
    def override(self) -> bool:
        return not self.override_bool
    
    @rx.var
    def evento_dinamico(self) -> bool:
        return asociar.modo_evento(int(self.id_evento_dest)) == "dinamico" if self.id_evento_dest else False

    @rx.var
    def reto_dinamico(self) -> bool:
        return asociar.es_dinamico(int(self.id_modo_puntaje)) if self.id_modo_puntaje else False

    def cargar_todo(self):
        guard = self.requiere_admin()
        if guard: return guard
        self.busqueda = self.busqueda_gest = ""
        self.dialog_bool = False
        self.override_bool = False
        self.id_evento_gest = ""
        self.retos_gest = []
        self.id_evento_dest = ""
        self.candidatos = []
        self.carrito = []
        self.tab = "asociar" 
        self.modo_def = 0
        self.inicial_def = 0
        self.minimo_def = 0
        catalogo = asociar.cargar_catalogos()
        self.categorias = catalogo["categorias"]
        self.modos = catalogo["modos"]
        self.id_modo_filtro = self.id_dificultad_filtro = self.id_categoria_filtro = ""
        self.dificultades = catalogo["dificultades"]    
        self.eventos_dest = catalogo["eventos_dest"]
        self.eventos_gest = catalogo["eventos_gest"]

    def cargar_candidatos(self):
        dest = int(self.id_evento_dest) if self.id_evento_dest else 0
        cat = int(self.id_categoria_filtro) if self.id_categoria_filtro else None
        mod =  int(self.id_modo_filtro) if self.id_modo_filtro else None
        dif = int(self.id_dificultad_filtro) if self.id_dificultad_filtro else None
        self.candidatos = asociar.retos_asociables(dest, self.busqueda, cat, dif, mod, self.aislados_bool)

    def cargar_destino(self):
        if self.id_evento_dest:
            self.prev_retos = asociar.prev_retos(int(self.id_evento_dest))
        else:
            self.prev_retos = []
        self.cargar_candidatos()
        
    @rx.event
    def open_dialog(self, id_reto:int, titulo:str, m_def:str, pi_def:int, pm_def:int | None=None):
        if not self.id_evento_dest:
            self.dialog_bool = False
            return rx.toast.warning("Seleccione evento detino.")
        self.id_dialog = id_reto
        self.titulo_dialog = titulo
        self.override_bool = False
        self.puntaje_inicial = str(pi_def)
        self.puntaje_minimo = str(pm_def) if pm_def is not None else ""
        self.id_modo_puntaje = m_def           
        self.inicial_def = pi_def
        self.minimo_def = pm_def if pm_def is not None else 0
        self.modo_def = int(m_def)
        self.dialog_bool = True

    def close_dialog(self):
        self.dialog_bool = self.override_bool = False
        self.id_dialog = 0
        self.titulo_dialog = ""
        self.id_modo_puntaje = self.puntaje_inicial = self.puntaje_minimo = ""
        self.modo_def = self.inicial_def = self.minimo_def = 0

    def confirmar_agregar(self):
        if any(item['id'] == self.id_dialog for item in self.carrito):
            return rx.toast.error(f"El reto {self.titulo_dialog} ya se encuetra en el carrito")

        inicial_in = int(self.puntaje_inicial) if self.puntaje_inicial.isdigit() else None
        minimo_in = int(self.puntaje_minimo) if self.puntaje_minimo.isdigit() else None

        if not self.evento_dinamico:
            id_modo = asociar.dinamico_estatico("estatico")
            inicial = inicial_in if self.override_bool else self.inicial_def
            minimo = None
        elif self.override_bool:
            id_modo = int(self.id_modo_puntaje) if self.id_modo_puntaje else self.modo_def
            inicial = inicial_in
            minimo = minimo_in if self.reto_dinamico else None
        else:
            id_modo = self.modo_def
            inicial = self.inicial_def
            minimo = self.minimo_def if self.reto_dinamico else None
        ok, msg = self.validar_campos(inicial, minimo, asociar.es_dinamico(id_modo))
        ok, msg = self.validar_campos(inicial, minimo, asociar.es_dinamico(id_modo))
        if not ok:
            return toast_msg(msg)
        self.carrito = self.carrito + [{
            "id":self.id_dialog,
            "titulo":self.titulo_dialog,
            "id_modo_puntaje":id_modo,
            "modo":asociar.modo_puntaje(id_modo),
            "puntaje_inicial":inicial,
            "puntaje_minimo":minimo,
        }]
        self.cargar_candidatos()
        self.dialog_bool = False
        return rx.toast.success(f"se agrego {self.titulo_dialog} "+(f" con: {inicial} {minimo} pts. (Override)" if self.override_bool else f"con: {inicial} {minimo} pts. (Default)"))

    def validar_campos(self, inicial, minimo, modo):
        if not self.evento_dinamico and modo:
            return False, "Evento estatico solo admite puntaje unico"
        if inicial is None or inicial <= 0:
                return False, "El puntaje inicial obligatorio mayor 0."
        if modo and self.evento_dinamico:
            if minimo is None or minimo <= 0:
                return False, "Puntaje minimo obligatorio mayor a 0 en modo dinamico."
            if minimo >= inicial:
                return False, "Puntaje minimo debe ser menor a el inicial."
        return True, ""
    @rx.event
    def quitar_carrito(self, id_reto:int):
        self.carrito = [i for i in self.carrito if i['id'] != id_reto]

    def vaciar_carrito(self):
        self.carrito = []

    def guardar_carrito(self):
        if not self.id_evento_dest:
            return rx.toast.warning("Seleccione un evento destino.")
        if not self.carrito:
            return rx.toast.warning("Sin retos para asociar a evento.")
        dest = int(self.id_evento_dest)
        exitos = 0
        fallos = []
        for item in self.carrito:
            try:
                asociar.asociar_reto(item['id'], dest, item['id_modo_puntaje'], item['puntaje_inicial'], item['puntaje_minimo'])
                exitos += 1
            except ValueError as e:
                fallos.append(f"{item['titulo']} : {e}")
        self.carrito = []
        self.cargar_destino()
        self.cargar_candidatos()
        return rx.toast.success(f"{exitos} reto(s) asociado(s)" + (f" Fallaron: {' '.join(fallos)}" if fallos else ""))

    def cargar_gestion(self):
        if self.id_evento_gest:
            gest = int(self.id_evento_gest) if self.id_evento_gest else 0
            cat = int(self.id_categoria_gest_filtro) if self.id_categoria_gest_filtro else None
            mod =  int(self.id_modo_gest_filtro) if self.id_modo_gest_filtro else None
            dif = int(self.id_dificultad_gest_filtro) if self.id_dificultad_gest_filtro else None
            self.retos_gest = asociar.retos_evento(gest, self.busqueda_gest, cat, dif, mod)
        else:
            self.retos_gest = []
    @rx.event
    def quitar_retos(self, id_reto):
        try:
            if asociar.quitar_reto(id_reto, int(self.id_evento_gest)):
                self.cargar_gestion()
                return rx.toast.success("Reto desvinculado de evento")
            else:
                return  rx.toast.error("No se encontro asociación")  
        except ValueError as e:
            self.cargar_gestion()
            return rx.toast.error(str(e))
        
#class GestionarAsociarState(AuthState):


class EditarAsociarState(AuthState):
    id_evento:int = 0
    id_edit:int = 0
    titulo_edit:str = ""
    id_modo_edit:str = ""
    inicial_def:str = ""
    minimo_def:str = ""
    puntaje_inicial_edit:str = ""
    puntaje_minimo_edit:str = ""
    edit_bool:bool = False
    @rx.event
    def set_id_modo_edit(self, v:str):
        self.id_modo_edit = v
    @rx.event
    def set_puntaje_inicial_edit(self, v:str):
        self.puntaje_inicial_edit = v
    @rx.event
    def set_puntaje_minimo_edit(self, v:str):
        self.puntaje_minimo_edit = v

    @rx.var
    def evento_edit_dinamico(self) -> bool:
        return asociar.modo_evento(int(self.id_evento)) == "dinamico" if self.id_evento else False
    @rx.var
    def reto_edit_dinamico(self) -> bool:
        return asociar.es_dinamico(int(self.id_modo_edit)) if self.id_modo_edit else False

    @rx.event
    def open_edit(self, id_contine:int, titulo:str):
        guard = self.requiere_admin()
        if guard: return guard
        contiene = asociar.obtener_contiene(id_contine)
        if  not contiene:
            return rx.toast.error("No se encontro el registro.")
        self.titulo_edit = titulo
        self.id_evento = contiene["id_evento"]
        self.id_edit = contiene["id_contiene"]
        self.id_modo_edit = str(contiene["id_modo_puntaje"])
        self.inicial_def = self.puntaje_inicial_edit = str(contiene["puntaje_inicial"])
        self.minimo_def = self.puntaje_minimo_edit = str(contiene["puntaje_minimo"]) if contiene["puntaje_minimo"] else ""
        self.edit_bool = True

    def close_edit(self):
        self.edit_bool = False
        self.titulo_edit = self.id_modo_edit = self.puntaje_inicial_edit = self.puntaje_minimo_edit= self.inicial_def= self.minimo_def = ""
        self.id_evento = self.id_edit = 0

    def validar_edit(self, inicial, minimo, modo_dinamico) -> tuple[bool, str]:
        if not self.evento_edit_dinamico and modo_dinamico:
            return False, "Evento estatico solo admite puntaje unico."
        if inicial is None or inicial <= 0:
            return False, "El puntaje inicial obligatorio mayor a 0."
        if modo_dinamico and self.evento_edit_dinamico:
            if minimo is None or minimo <= 0:
                return False, "Puntaje minimo obligatorio mayor a 0 en modo dinamico."
            if minimo >= inicial:
                return False, "Puntaje minimo debe ser menor al inicial."
        return True, ""
        
    async def guardar_edit_contiene(self):
        inicial = int(self.puntaje_inicial_edit) if self.puntaje_inicial_edit.isdigit() else None
        minimo = int(self.puntaje_minimo_edit) if self.puntaje_minimo_edit.isdigit() else None
        
        
        if not self.evento_edit_dinamico:
            id_modo = asociar.dinamico_estatico("estatico")
            minimo = None
        else:
            id_modo = int(self.id_modo_edit) if self.id_modo_edit.isdigit() else 0
            minimo = minimo if self.reto_edit_dinamico else None
        ok, msg = self.validar_edit(inicial, minimo, self.reto_edit_dinamico)
        if not ok:
            return toast_msg(msg)
        try:
            asociar.editar_contiene(self.id_edit, id_modo, inicial, minimo)
        except ValueError as e:
            return toast_msg(str(e))
        gestion = await self.get_state(AsociarState)
        gestion.cargar_gestion()
        self.edit_bool = False
        return rx.toast.success(f"{self.titulo_edit} actualizado.")
    