import reflex as rx 
from sqlmodel import Session,select
from itdb_ctf.db import engine
from itdb_ctf.models import(Categoria,Dificultad,ModoPuntaje,Evento)
from itdb_ctf.auth.auth_state import AuthState
from itdb_ctf.components.navbar import navbar
from itdb_ctf.components.form import select_calatog,input_box
from itdb_ctf.retos.reto_logic import crear_reto
from itdb_ctf.retos.archivo_logic import guardar_archivo

class AdminRetosState(AuthState):
    
    id_evento:str = ""
    
    titulo:str = ""
    descripcion:str = ""
    flag:str = ""
    puntaje_inicial:str = ""
    puntaje_minimo:str = ""
    id_categoria:str = "" 
    id_dificultad:str = ""
    id_modo_puntaje:str = ""
    mensaje:str = ""

    archivo_original:str = ""
    archivo_ruta:str = ""
    nombre_subido:str = ""

    def set_id_evento(self, v:str):
        self.id_evento=v

    def set_titulo(self, v:str):
        self.titulo=v

    def set_descripcion(self, v:str):
        self.descripcion=v

    def set_flag(self, v:str):
        self.flag=v

    def set_puntaje_inicial(self, v:str):
        self.puntaje_inicial=v

    def set_puntaje_minimo(self, v:str):
        self.puntaje_minimo=v

    def set_id_categoria(self,v:str):
        self.id_categoria=v

    def set_id_dificultad(self, v:str):
        self.id_dificultad=v

    def set_id_modo_puntaje(self, v:str):
        self.id_modo_puntaje=v

    categorias:list[tuple[str,str]]=[]
    dificultades:list[tuple[str,str]]=[]
    modos:list[tuple[str,str]]=[]
    eventos:list[tuple[str,str]]=[]

    def cargar_catalogos(self):
        guard=self.requiere_staff()
        if guard:
            return guard
        with Session(engine) as s:
            self.categorias=[(str(c.id_categoria),c.etiqueta) for c in s.exec(select(Categoria)).all()]
            self.dificultades=[(str(d.id_dificultad),d.etiqueta) for d in s.exec(select(Dificultad)).all()]
            self.modos=[(str(m.id_modo_puntaje),m.etiqueta) for m in s.exec(select(ModoPuntaje)).all()]
            self.eventos=[(str(e.id_evento),e.titulo) for e in s.exec(select(Evento).where(Evento.activo==True)).all()]

    async def subir_archivo(self,files:list[rx.UploadFile]):
        if not files:
            return
        archivo=files[0]
        contenido=await archivo.read()
        original, nombre_fisico = guardar_archivo(contenido,archivo.name)
        self.archivo_original=original
        self.archivo_ruta=nombre_fisico
        self.nombre_subido=original
        self.mensaje=f"Archivo '{original}' listo."


    def guardar_reto(self):
        if not (self.titulo and self.flag and self.puntaje_inicial):
            self.mensaje="Titulo, flag y puntaje inicial son obligatorios."
            return
        if not (self.id_categoria and self.id_dificultad and self.id_modo_puntaje and self.id_evento):
            self.mensaje="Seleccione dificultad, categoria, modo y evento."
            return
        try:
            crear_reto(
                id_evento=int(self.id_evento),
                id_usuario=self.id_usuario,
                id_categoria=int(self.id_categoria),
                id_dificultad=int(self.id_dificultad),
                id_modo_puntaje=int(self.id_modo_puntaje),
                titulo=self.titulo,
                descripcion=self.descripcion or None,
                flag=self.flag,
                puntaje_inicial=int(self.puntaje_inicial),
                puntaje_minimo=int(self.puntaje_minimo) if self.puntaje_minimo else None,
                archivo_original=self.archivo_original or None,
                archivo_ruta=self.archivo_ruta or None
            )
        except Exception as e:
            self.mensaje=f"Error: {e}"
            return
        self.mensaje=f"Reto {self.titulo} creado."
        self.titulo=self.descripcion=self.flag=""
        self.puntaje_inicial=self.puntaje_minimo=""
        self.archivo_original=self.archivo_ruta=self.nombre_subido=""
        self.id_evento=self.id_categoria=self.id_dificultad=self.id_modo_puntaje=""
    
    async def guardar_reto_completo(self, files:list[rx.UploadFile]):
        await self.subir_archivo(files)
        self.guardar_reto()

def admin_retos_page() -> rx.Component:
    
    return rx.vstack(
        navbar(),
        rx.center(
            rx.vstack(
                rx.heading("Crear Reto"),
                rx.input(placeholder="Titulo", value=AdminRetosState.titulo, on_change=AdminRetosState.set_titulo),
                rx.text_area(placeholder="Descripción", value=AdminRetosState.descripcion, on_change=AdminRetosState.set_descripcion),
                rx.input(placeholder="Flag de reto (se hashea)", value=AdminRetosState.flag, on_change=AdminRetosState.set_flag),
                rx.input(placeholder="Puntaje inicial", type="number", value=AdminRetosState.puntaje_inicial, on_change=AdminRetosState.set_puntaje_inicial),
                rx.input(placeholder="Puntaje minimo (opcional)", type="number", value=AdminRetosState.puntaje_minimo, on_change=AdminRetosState.set_puntaje_minimo),
                select_calatog(AdminRetosState.categorias, "Categoria", AdminRetosState.set_id_categoria),
                select_calatog(AdminRetosState.dificultades, "Dificultad", AdminRetosState.set_id_dificultad),
                select_calatog(AdminRetosState.modos, "Modo de puntaje", AdminRetosState.set_id_modo_puntaje),
                select_calatog(AdminRetosState.eventos, "Evento", AdminRetosState.set_id_evento),
                ## subida de archivos
                rx.upload(
                    rx.text("Arrastra o haz click para subir el archivo del reto."),
                    id="archivo_reto",
                    max_files=1,
                    border="1px dashed #888", padding="1em",
                ),         
                #rx.button("Subir archivo", on_click=AdminRetosState.subir_archivo(
                #    rx.upload_files(upload_id="archivo_reto")
                #)),
                rx.cond(
                    AdminRetosState.nombre_subido != "",
                    rx.text(f"Adjunto: {AdminRetosState.nombre_subido}",color="green")
                ),
                rx.button("Guardar Reto", on_click=AdminRetosState.guardar_reto_completo(rx.upload_files(upload_id="archivo_reto"))),
                rx.cond(AdminRetosState.mensaje != "", rx.text(AdminRetosState.mensaje)),
                spacing="3", width="400px",
            ),
            height="85vh"
        )
    )