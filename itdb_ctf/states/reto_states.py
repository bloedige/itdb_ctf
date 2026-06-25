import reflex as rx 
from sqlmodel import Session,select
from itdb_ctf.db import engine
from itdb_ctf.models import Categoria,Dificultad,ModoPuntaje,Evento,Reto
from itdb_ctf.auth.auth_state import AuthState
from itdb_ctf.retos.reto_logic import crear_reto, activar_desactivar_reto, editar_reto, puede_editar
from itdb_ctf.retos.archivo_logic import guardar_archivo

class CrearRetosState(AuthState):
    
    # ---Campos de formulario
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
    # ---Datos de archivo subido
    archivo_original:str = ""
    archivo_ruta:str = ""
    nombre_subido:str = ""
    # --- Catalogos de opciones 
    categorias:list[tuple[str,str]]=[]
    dificultades:list[tuple[str,str]]=[]
    modos:list[tuple[str,str]]=[]
    eventos:list[tuple[str,str]]=[]

    # ---setters

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
        self.limpiar()

    async def guardar_reto_completo(self, files:list[rx.UploadFile]):
        await self.subir_archivo(files)
        self.guardar_reto()

    def limpiar(self):
        self.titulo=self.descripcion=self.flag=""
        self.puntaje_inicial=self.puntaje_minimo=""
        self.archivo_original=self.archivo_ruta=self.nombre_subido=""
        self.id_evento=self.id_categoria=self.id_dificultad=self.id_modo_puntaje=""


class ListarRetosState(AuthState):
    
    lista: list[dict] = []
    busqueda: str = ""

    def set_busqueda(self, v:str):
        self.busqueda=v

    def cargar_lista(self):
        guard = self.requiere_staff()
        if guard:
            return guard
        
        with Session(engine) as s:
            stmt = (select(Reto,Categoria.etiqueta,Dificultad.etiqueta,ModoPuntaje.etiqueta)
                          .join(Categoria, Reto.id_categoria==Categoria.id_categoria)
                          .join(Dificultad, Reto.id_dificultad==Dificultad.id_dificultad)
                          .join(ModoPuntaje, Reto.id_modo_puntaje==ModoPuntaje.id_modo_puntaje)
                          )
            
            if self.busqueda:
                stmt = stmt.where(Reto.titulo.ilike(f"%{self.busqueda}%"))
                

            self.lista = [
                {
                    "id":r.id_reto,
                    "titulo":r.titulo,
                    "categoria":cat,
                    "dificultad":dif,
                    "modalidad":mod,
                    "puntaje":r.puntaje_inicial,
                    "minimo":r.puntaje_minimo if r.puntaje_minimo else "---",
                    "activo":r.activo, 
                    "edit":puede_editar(r,self.id_usuario,self.codigo_rol) 
                }
                for r,cat,dif,mod in s.exec(stmt).all()
            ]

    def buscar(self):
        return ListarRetosState.cargar_lista
    

    def alternar_activo(self, id_reto:int):
        guard = self.requiere_staff()
        if guard:
            return guard      
        activar_desactivar_reto(id_reto)  
        return ListarRetosState.cargar_lista
    
class EditarRetosState(AuthState):
    id_reto: int = 0
    titulo: str = ""    
    descripcion: str=""
    flag: str=""
    puntaje_inicial: str=""
    puntaje_minimo: str=""
    
    id_modo_puntaje: str = ""
    id_dificultad: str = ""
    id_categoria: str = ""
    
    categorias:list[tuple[str,str]]=[]
    dificultades:list[tuple[str,str]]=[]
    modos:list[tuple[str,str]]=[]

    mensaje: str=""
    
    def set_titulo(self, v: str):
        self.titulo = v    
    def set_descripcion(self, v: str):
        self.descripcion = v
    def set_flag(self, v: str):
        self.flag = v
    def set_puntaje_inicial(self, v: str):
        self.puntaje_inicial = v
    def set_puntaje_minimo(self, v: str): 
        self.puntaje_minimo = v
    def set_mesaje(self, v: str):
        self.mensaje = v      
    def set_id_modo_puntaje(self, v: str): 
        self.id_modo_puntaje=v
    def set_id_dificultad(self, v: str): 
        self.id_dificultad=v
    def set_id_categoria(self, v: str): 
        self.id_categoria=v

    def cargar_reto(self, id_reto:int):
        guard = self.requiere_staff()
        if guard:
            return guard

        with Session(engine) as s:
            reto = s.get(Reto,id_reto)
            if not reto:
                return
            
            if not puede_editar(reto, self.id_usuario,self.codigo_rol):
                self.mensaje="no puedes editar este reto."
                return
            
            
            self.categorias=[(str(c.id_categoria),c.etiqueta) for c in s.exec(select(Categoria)).all()]
            self.dificultades=[(str(d.id_dificultad),d.etiqueta) for d in s.exec(select(Dificultad)).all()]
            self.modos=[(str(m.id_modo_puntaje),m.etiqueta) for m in s.exec(select(ModoPuntaje)).all()]
            self.id_reto = reto.id_reto            
            self.titulo = reto.titulo            
            self.descripcion = reto.descripcion or ""
            self.puntaje_inicial = str(reto.puntaje_inicial)
            self.puntaje_minimo = str(reto.puntaje_minimo) if reto.puntaje_minimo else ""
            self.id_modo_puntaje = str(reto.id_modo_puntaje)
            self.id_dificultad = str(reto.id_dificultad)
            self.id_categoria = str(reto.id_categoria)
            self.flag = ""
            self.mensaje = ""

    def guardar(self):
        guard = self.requiere_staff()
        if guard:
            return guard
        
        with Session(engine) as s:
            reto = s.get(Reto,self.id_reto)
            if not reto:
                self.mensaje="El reto no existe"
            if not puede_editar(reto, self.id_usuario, self.codigo_rol):
                self.mensaje="No cuatas con permiso de edicion de retos"
                return
            
        values = {
            "titulo": self.titulo,            
            "descripcion": self.descripcion,
            "puntaje_inicial": int(self.puntaje_inicial),
            "puntaje_minimo": int(self.puntaje_minimo) if self.puntaje_minimo else None,
            "id_categoria":int(self.id_categoria),
            "id_dificultad":int(self.id_dificultad),
            "id_modo_puntaje":int(self.id_modo_puntaje),
        }
        if self.flag:
            values['flag']=self.flag
        editar_reto(self.id_reto,values)
        self.mensaje="Reto actualizado."
        return ListarRetosState.cargar_lista 