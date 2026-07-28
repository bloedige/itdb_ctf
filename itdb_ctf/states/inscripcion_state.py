import reflex as rx
from sqlmodel import Session, select
from itdb_ctf.db import engine
from itdb_ctf.auth.auth_state import AuthState
from itdb_ctf.models import EstadoInscripcion, MetodoAuth
from itdb_ctf.inscripcion import inscripcion_logic as insc

class InscripcionState(AuthState):

    id_evento_car:str = ""
    id_evento_ges:str = ""
    eventos:list[tuple[str, str]] = []
    tab = "inscribir" # /gestionar

    busqueda_ins:str = ""
    id_metodo_filtro:str = ""
    candidatos:list[dict] = []
    carrito:list[dict] = []

    busqueda_ges:str = ""
    id_estado_filtro:str = ""
    participantes:list[dict] = []

    metodos:list[tuple[str,str]] = []
    estados:list[tuple[str,str]] = []

    id_evento_csv:str = ""
    csv_nombre:str = ""
    csv_contenido:bytes = b""
    csv_dialog:bool = False
    csv_analize:bool = False
    prev_nuevos:list[dict] = []
    prev_existentes:list[dict] = []
    prev_omitidos:list[dict] = []


    def set_id_evento_car(self, v:str):
        self.id_evento_car = v
        return InscripcionState.cargar_datos
    
    def set_id_evento_ges(self, v:str):
        self.id_evento_ges = v
        return InscripcionState.cargar_datos
    
    def set_tab(self, v:str):
        self.tab = v
        return InscripcionState.cargar_datos
    
    def set_busqueda_ins(self, v:str):
        self.busqueda_ins = v
        return InscripcionState.cargar_datos
    
    def set_busqueda_ges(self, v:str):
        self.busqueda_ges = v
        return InscripcionState.cargar_datos
    
    def set_id_metodo_filtro(self, v:str):
        self.id_metodo_filtro = v               
        return InscripcionState.cargar_datos
    
    def set_id_estado_filtro(self, v:str):
        self.id_estado_filtro = v               
        return InscripcionState.cargar_datos
    
    def set_id_evento_csv(self, v:str):
        self.id_evento_csv = v
    
    @rx.var
    def ids_carrito(self) -> list[int]:
        return [c["id_usuario"]for c in self.carrito]
    
    @rx.var
    def carrito_vacio(self) -> bool:
        return len(self.carrito) == 0
    
    @rx.var
    def modo(self) -> bool:
        return self.tab == "gestionar"
    
    @rx.var
    def csv_total_incribir(self) -> int:
        return len(self.prev_nuevos) + len(self.prev_existentes)

    @rx.var
    def csv_datos(self) -> bool:
        return self.csv_total_incribir > 0
    
    def open_close_dialog_csv(self):
        self.csv_dialog = not self.csv_dialog
    
    def cargar_todo(self):
        guard = self.requiere_admin()
        if guard: return guard
        self.id_evento_ges = ""
        self.id_evento_car = ""
        self.carrito = []
        self.participantes = []
        self.candidatos = []
        self.eventos = insc.eventos_inscribibles()
        with Session(engine) as s:
            self.metodos=[("", "Todos")] + [(str(m.id_metodo_auth), m.etiqueta) for m in s.exec(select(MetodoAuth)).all()]
            self.estados=[("", "Todos")] + [(str(e.id_estado_inscripcion), e.etiqueta) for e in s.exec(select(EstadoInscripcion)).all()]

    def cargar_datos(self):
        guard = self.requiere_admin()
        if guard: return guard
        self.candidatos = []
        self.participantes = []
        if self.id_evento_car:
            self.cargar_candidatos()
        if self.id_evento_ges:
            self.cargar_participantes()
        
    def cargar_candidatos(self):
        if not self.id_evento_car:
            self.candidatos = []
            return
        met = int(self.id_metodo_filtro) if self.id_metodo_filtro else None
        self.candidatos = insc.candidatos(int(self.id_evento_car), self.busqueda_ins, met)

    def cargar_participantes(self):
        if not self.id_evento_ges:
            self.participantes = []
            return
        est =  int(self.id_estado_filtro) if self.id_estado_filtro else None
        self.participantes = insc.participantes(int(self.id_evento_ges), self.busqueda_ges, est)

    def agregar_carrito(self, id_usuario:int, nombre:str, email:str):
        if id_usuario in [c['id_usuario'] for c in self.carrito]:
            return
        self.carrito = self.carrito + [{"id_usuario":id_usuario, "nombre":nombre, "email_inst":email}]

    def quitar_carrito(self, id_usuario:int):
        self.carrito = [c for c in self.carrito if c['id_usuario']!= id_usuario]

    def vaciar_carrito(self):
        self.carrito = []

    def guardar_carrito(self):
        guard = self.requiere_admin()
        if guard: return guard
        if not self.id_evento_car:
            return rx.toast.warning("Seleccione un evento")
        if not self.carrito:
            return rx.toast.warning("sin usuarios para incribir a evento")
        ids = [c['id_usuario']for c in self.carrito]
        ok, errors = insc.inscribir_lote(ids, int(self.id_evento_car))
        self.carrito = []
        self.cargar_datos()
        if errors:
            return rx.toast.warning(f"{ok} inscritos, {len(errors)} con error")
        return rx.toast.success(f"{ok} estudiantes inscritos")
    
    def quitar(self, id_participa:int):
        guard = self.requiere_admin()
        if guard: return guard
        try:
            insc.quitar_incripcion(id_participa)
        except ValueError as e:
            return rx.toast.error(str(e))
        self.cargar_datos()
        return rx.toast.success("Inscripcion anulada")
    
    def descalificar(self, id_paticipa:int):
        guard = self.requiere_admin()
        if guard: return guard
        try:
            est = insc.alternar_estado(id_paticipa)
        except ValueError as e:
            return rx.toast.error(str(e))
        self.cargar_datos()
        return rx.toast.success(f"Partciapnte descalificado" if est =="descalificado" else "Participante rehabilitado")
    
    async def on_drop_csv(self, file:list[rx.UploadFile]):
        if not file:
            return
        self.csv_analize = False
        csv = file[0]
        self.csv_nombre = csv.name
        self.csv_contenido = await csv.read()

    def analizar_csv(self):
        guard = self.requiere_admin()
        if guard: return guard
        if not self.id_evento_csv:
            return rx.toast.error("Seleccione evento.")
        if not self.csv_contenido:
            return rx.toast.error("Subir archivo csv.")
        correos = insc.parsear_cvs(self.csv_contenido)
        if not correos:
            return rx.toast.error("CSV sin correos validos.")
        reporte = insc.analizar_correos(correos, int(self.id_evento_csv))
        self.prev_nuevos = reporte["nuevos"]
        self.prev_existentes = reporte["existentes"]
        self.prev_omitidos = reporte["omitidos"]
        self.csv_analize = True

    def confirmar_csv(self):
        guard = self.requiere_admin()
        if guard: return guard
        ok, errors = insc.confirmar_csv(self.prev_nuevos, self.prev_existentes, int(self.id_evento_csv))
        self.cerrar_csv()
        self.cargar_datos()
        if errors:
            return rx.toast.warning(f"{ok} inscritos, {len(errors)} con error")
        return rx.toast.success(f"{ok} incritos desde CSV" )
    
    def cerrar_csv(self):
        self.open_close_dialog_csv()
        self.csv_nombre = self.id_evento_csv = ""
        self.csv_analize = False
        self.prev_nuevos = self.prev_existentes = self.prev_omitidos = []
        self.csv_contenido = b""