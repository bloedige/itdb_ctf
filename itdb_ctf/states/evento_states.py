import reflex as rx
from datetime import datetime
from sqlmodel import Session, select
from itdb_ctf.db import engine
from itdb_ctf.models import ModoPuntaje, Modalidad
from itdb_ctf.auth.auth_state import AuthState
from itdb_ctf.evento.evento_logic import crear_evento, editar_evento, obtener_evento, activar_desactivar_evento, listar_evento, freeze_scoreboard

class CreaEventoState(AuthState):
    titulo: str = ""
    descripcion: str = ""
    id_modalidad: str = ""
    id_modo_puntaje: str = ""
    fec_inicio: str = ""
    fec_fin: str = ""
    auto_inscripcion: bool = False
    mensaje: str = ""
    
    modalidades: list[tuple[str,str]] = []
    modos: list[tuple[str,str]] = []
     
    dialog_bool:bool = False

    def set_titulo(self, v:str):
        self.titulo = v
    def set_descripcion(self, v:str):
        self.descripcion = v
    def set_id_modalidad(self, v:str):
        self.id_modalidad = v
    def set_id_modo_puntaje(self, v:str):
        self.id_modo_puntaje = v
    def set_fec_inicio(self, v:str):
        self.fec_inicio = v
    def set_fec_fin(self, v:str):
        self.fec_fin = v
    def set_auto_inscripcion(self, v:bool):
        self.auto_inscripcion = v
    def set_drop_mensaje(self):
        self.mensaje = ""
    def open_close_dialog(self):
        self.dialog_bool = not self.dialog_bool
    

    @rx.var
    def modalidad_abierto(self) -> bool:
        if not self.modalidades or not self.id_modalidad:
            return True
        for id_m, et in self.modalidades:
            if id_m == self.id_modalidad:
                return et == "abierto"
        return True

    def cargar_catalogos(self):
        guard = self.requiere_staff()
        if guard: return guard
        with Session(engine) as s:
            self.modalidades = [(str(m.id_modalidad),m.etiqueta) for m in s.exec(select(Modalidad)).all()]
            self.modos = [(str(mp.id_modo_puntaje), mp.etiqueta) for mp in s.exec(select(ModoPuntaje)).all()]

    async def guardar_evento(self) -> bool:
        fi = datetime.fromisoformat(self.fec_inicio) if self.fec_inicio else None
        ff = datetime.fromisoformat(self.fec_fin) if self.fec_fin else None
        try:
            crear_evento(
                id_usuario=self.id_usuario,
                id_modalidad=int(self.id_modalidad),
                id_modo_puntaje=int(self.id_modo_puntaje),
                titulo=self.titulo,
                descripcion=self.descripcion or None,
                fec_inicio=fi,
                fec_fin=ff,
                auto_inscripcion=self.auto_inscripcion,
            )
        except ValueError as e:
            self.mensaje = str(e)
            return False
        except Exception as e:
            self.mensaje = f"error. {e}"
            return False
        self.mensaje = f"Evento {self.titulo} creado."
        return True

    async def guardar_evento_completo(self):
        if not self.validar_campos():
            return
        if await self.guardar_evento():
            listar = await self.get_state(ListarEventoState)
            listar.cargar_lista()
            self.limpiar()
            self.open_close_dialog()
            return rx.toast.success(self.mensaje)
        

    def limpiar(self):
        self.titulo = self.descripcion = ""
        self.id_modalidad = self.id_modo_puntaje = ""
        self.fec_inicio = self.fec_fin = ""
        self.auto_inscripcion = False

    def validar_campos(self) -> bool:
        if not (self.titulo and self.descripcion):
            self.mensaje = "Se requiere llenar campos."
            return False
        if not self.titulo:
            self.mensaje = "Se requiere un titulo."
            return False
        if not self.id_modalidad:
            self.mensaje = "Se require una modalidad."
            return False
        if not self.id_modo_puntaje:
            self.mensaje = "Se requiere un modo de puntaje."
            return False
        return True
    
class ListarEventoState(AuthState):
    lista: list[dict] = []
    busqueda: str = ""

    def set_busqueda(self, v:str):
        self.busqueda = v
        return ListarEventoState.cargar_lista
    
    def cargar_lista(self):
        guard = self.requiere_staff()
        if guard: return guard
        eventos = listar_evento()
        if self.busqueda:
            b = self.busqueda.lower()
            eventos = [e for e in eventos if b in e['titulo'].lower()]
        self.lista = eventos
    
    def arternar_activo(self, id_evento:int):
        guard = self.requiere_staff()
        if guard: return guard
        activar_desactivar_evento(id_evento)
        self.cargar_lista()

class EditarEventoState(AuthState):
    id_evento:int = 0
    titulo:str = ""
    descripcion:str = ""
    id_modalidad:str = ""
    id_modo_puntaje:str = ""
    fec_inicio:str = ""
    fec_fin:str = ""
    auto_inscripcion:bool = False
    mensaje:str = ""
    
    modalidades: list[tuple[str,str]] = []
    modos: list[tuple[str,str]] = []

    dialog_bool: bool =  False
   

    def set_titulo(self, v:str):
        self.titulo = v
    def set_descripcion(self, v:str):
        self.descripcion = v
    def set_id_modalidad(self, v:str):
        self.id_modalidad = v
    def set_id_modo_puntaje(self, v:str):
        self.id_modo_puntaje = v
    def set_fec_inicio(self, v:str):
        self.fec_inicio = v
    def set_fec_fin(self, v:str):
        self.fec_fin = v
    def set_auto_inscripcion(self, v:bool):
        self.auto_inscripcion = v
    def set_drop_mensaje(self):
        self.mensaje = ""
    def open_close_dialog(self):
        self.dialog_bool = not self.dialog_bool

    @rx.var
    def modalidad_abierto(self) -> bool:
        if not self.modalidades or not self.id_modalidad:
            return True
        for id_m, et in self.modalidades:
            if id_m == self.id_modalidad:
                return et == "abierto"
        return True

    
    def cargar_evento(self, id_evento:int):
        guard = self.requiere_staff()
        if guard: return guard
        with Session(engine) as s:
            self.modalidades = [(str(m.id_modalidad), m.etiqueta) for m in s.exec(select(Modalidad)).all()]
            self.modos = [(str(mp.id_modo_puntaje),mp.etiqueta)for mp in s.exec(select(ModoPuntaje)).all()]
        ev = obtener_evento(id_evento)
        if not ev: 
            self.mensaje = "Evento 404" 
            return
        self.titulo = ev.titulo
        self.descripcion = ev.descripcion or ""
        self.id_modalidad = str(ev.id_modalidad)
        self.id_modo_puntaje = str(ev.id_modo_puntaje)
        self.fec_inicio = ev.fec_inicio.strftime("%Y-%m-%dT%H:%M") if ev.fec_inicio else ""
        self.fec_fin = ev.fec_fin.strftime("%Y-%m-%dT%H:%M") if ev.fec_fin else ""
        self.auto_inscripcion = bool(ev.auto_inscripcion)
        self.mensaje = ""

    async def guardar(self):
        fi = datetime.fromisoformat(self.fec_inicio) if self.fec_inicio else None
        ff = datetime.fromisoformat(self.fec_fin) if self.fec_fin else None
        values = {
            "titulo":self.titulo,
            "descripcion":self.descripcion,
            "id_modalidad":int(self.id_modalidad),
            "id_modo_puntaje":int(self.id_modo_puntaje),
            "fec_inicio":fi,
            "fec_fin":ff,
            "auto_inscripcion":self.auto_inscripcion,
        }
        try:
            editar_evento(self.id_evento, values)
        except ValueError as e:
            self.mensaje = str(e)
            return
        except Exception as e:
            self.mensaje = f"error: {e}"
            return
        return True 

    async def guardar_edit_completo(self):
        if not self.validar_campos():
            return
        if await self.guardar():
            listar = await self.get_state(ListarEventoState)
            listar.cargar_lista()
            self.open_close_dialog()
            self.limpiar()
            self.set_drop_mensaje()
            return rx.toast.success("Datos de evento Actualizado")

    def validar_campos(self) -> bool:
        if not (self.titulo and self.id_modalidad):
            self.mensaje = "Se requiere llenar campos."
        if not self.titulo:
            self.mensaje = "Se requiere un titulo."
            return False
        if not self.id_modalidad:
            self.mensaje = " Se require una modalidad."
            return False
        if not self.id_modo_puntaje:
            self.mensaje = " Se requiere un modo de puntaje."
            return False
        return True
    
    def limpiar(self):
        self.titulo = self.descripcion = ""
        self.id_modalidad = self.id_modo_puntaje = ""
        self.fec_inicio = self.fec_fin = ""
        self.auto_inscripcion = False