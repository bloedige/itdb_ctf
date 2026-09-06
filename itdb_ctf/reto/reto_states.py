import reflex as rx 
from itdb_ctf.auth.auth_state import AuthState
from itdb_ctf.reto.reto_logic import crear_reto, activar_desactivar_reto, editar_reto, activar_desactivar_pista, crear_pista, editar_pista, listar_pista, listar_retos, puede_editar, obtener_reto
from itdb_ctf.reto.archivo_logic import guardar_archivo, borrar_archivo
from itdb_ctf.asociar.asociar_logic import aislado, listar_eventos_validos, cargar_catalogos

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
    # --- Pistas
    pistas: list[dict]=[]
    pista_costo: str = ""
    pista_desc: str = "" 
    # --- Temp
    archivo_temp:str = ""
    contenido_temp:bytes = b""
    # --- dialog
    dialog_bool:bool = False
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
    def set_pista_costo(self, v:str):
        self.pista_costo=v
    def set_pista_desc(self, v:str):
        self.pista_desc=v

    def set_cancelar(self):
        self.archivo_temp = ""
        self.contenido_temp = b""
    
    def set_drop_mensaje(self):
        self.mensaje = ""
    
    def open_close_dialog(self):
        self.dialog_bool = not self.dialog_bool
        
    async def on_drop_file(self,files:list[rx.UploadFile]):
        if not files:
            return 
        archivo = files[0]
        self.archivo_temp = archivo.name
        self.contenido_temp = await archivo.read()

    def cargar_catalogos(self):
        guard=self.requiere_staff()
        if guard: return guard
        catalogos = cargar_catalogos()
        self.categorias = catalogos["categorias"]
        self.dificultades = catalogos["dificultades"]
        self.modos = catalogos["modos"]
        self.eventos=listar_eventos_validos()

    async def subir_archivo(self):
        original, nombre_fisico = guardar_archivo(self.contenido_temp,self.archivo_temp)
        self.archivo_original=original
        self.archivo_ruta=nombre_fisico
        self.nombre_subido=original
        self.mensaje=f"Archivo '{original}' listo."

    async def guardar_reto(self):
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
                archivo_ruta=self.archivo_ruta or None,
                pistas=self.pistas,
            )
        except Exception as e:
            self.mensaje=f"Error: {e}"
            return
        self.mensaje=(f"Reto {self.titulo} " + (f"con archivo {self.nombre_subido}" if self.nombre_subido else "") + "creado.")
        return True

    async def guardar_reto_completo(self):
        if not self.validar_campos():
            return
        if self.contenido_temp and self.archivo_temp:
            await self.subir_archivo()
        if await self.guardar_reto():
            self.limpiar()
            self.open_close_dialog()
            listar = await self.get_state(ListarRetosState)
            listar.cargar_lista()
            return rx.toast.success(self.mensaje)

    def agregar_pista(self):
        if not self.pista_desc:
            self.mensaje = "la pista una descripcion."
            return
        
        self.pistas = self.pistas + [{
            "costo":self.pista_costo or "0",
            "descripcion":self.pista_desc,
        }]
        self.pista_costo = ""
        self.pista_desc = ""

    def quitar_pista(self, indice:int):
        self.pistas = [p for i, p in enumerate(self.pistas) if i != indice]

    def validar_campos(self) -> bool:
        validaciones = [
            (self.titulo, "Se requiere el título"),
            (self.flag, "Se requiere la flag"),
            (self.puntaje_inicial, "Se requiere el puntaje inicial"),
            (self.id_categoria, "Se requiere una categoría"),
            (self.id_dificultad, "Se requiere una dificultad"),
            (self.id_modo_puntaje, "Se requiere un modo de puntaje"),
            (self.id_evento, "Se requiere un evento"),
        ]
    
        for valor, mensaje in validaciones:
            if not valor:
                self.mensaje = mensaje
                return False
        return True

    def limpiar(self):
        self.titulo = self.descripcion = self.flag = ""
        self.puntaje_inicial = self.puntaje_minimo = ""
        self.archivo_original = self.archivo_ruta = self.nombre_subido = ""
        self.id_evento = self.id_categoria = self.id_dificultad = self.id_modo_puntaje = ""
        self.pistas = []
        self.pista_desc = self.pista_costo = ""
        self.contenido_temp = b""
        self.archivo_temp = ""

class ListarRetosState(AuthState):
    
    lista: list[dict] = []
    busqueda: str = ""

    def set_busqueda(self, v:str):
        self.busqueda=v
        return ListarRetosState.cargar_lista

    def cargar_lista(self):
        guard = self.requiere_staff()
        if guard: return guard
        retos = listar_retos(self.id_usuario, self.codigo_rol)
        if self.busqueda:
            b = self.busqueda.lower()
            retos = [r for r in retos if b in r["titulo"].lower() or b in r["categoria"].lower() or b in r["dificultad"].lower() or b in r["modo_puntaje"].lower()]
        self.lista = retos       
        
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

    # --- Pistas 
    pistas_existentes: list[dict] = []
    pistas_nuevas: list[dict] = []
    pista_costo: str = ""
    pista_desc: str = ""

    # --- Archivos
    archivo_temp: str = ""
    contenido_temp: bytes = b"" 
    accion_archivo: str = "conservar"
    archivo_original: str = ""
    archivo_ruta: str = ""

    dialog_bool:bool = False

    aislado_bool:bool = False
    eventos:list[tuple[str,str]]=listar_eventos_validos
    #conluir selects mas  condicion = view 

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
        self.id_modo_puntaje = v
    def set_id_dificultad(self, v: str): 
        self.id_dificultad = v
    def set_id_categoria(self, v: str): 
        self.id_categoria = v
    def set_pista_costo(self, v:str):
        self.pista_costo = v
    def set_pista_desc(self, v:str):
        self.pista_desc = v
    def open_close_dialog(self):
        self.dialog_bool = not self.dialog_bool 
    def set_drop_mensaje(self):
        self.mensaje = ""

    def set_pista_existente_costo(self, indice:int, v:str):
        self.pistas_existentes = [
            {**p, "costo": v} if i == indice else p
            for i, p in enumerate(self.pistas_existentes)
        ]
    def set_pista_existente_desc(self, indice:int, v:str):
        self.pistas_existentes = [
            {**p, "descripcion": v} if i == indice else p
            for i, p in enumerate(self.pistas_existentes)
        ]

    def toggle_pista(self, id_pista:int):
        activar_desactivar_pista(id_pista)
        self.pistas_existentes = listar_pista(self.id_reto)

    def agregar_pista(self):
        if not self.pista_desc:
            self.mensaje = "La pista necesita descripcion"
            return
        self.pistas_nuevas = self.pistas_nuevas +[{
            "costo": int(self.pista_costo) if self.pista_costo else 0,
            "descripcion":self.pista_desc
        }]
        self.pista_desc = ""
        self.pista_costo = ""

    def quitar_pistas_nuevas(self,  indice:int):
        self.pistas_nuevas = [p for i, p in enumerate(self.pistas_nuevas) if i != indice]  

    def set_conservar(self):
        self.accion_archivo = "conservar"
        self.archivo_temp = ""
        self.contenido_temp: bytes = b"" 

    def set_quitar(self):
        self.accion_archivo = "quitar"
        self.archivo_temp = ""
        self.contenido_temp: bytes = b"" 

    def set_remplazar(self):
        self.accion_archivo = "remplazar"

    async def on_drop_file(self, files:list[rx.UploadFile]):
        if files:
            archivo = files[0]
            self.contenido_temp = await archivo.read()
            self.archivo_temp = archivo.name
            self.set_remplazar()      
    
    def quitar_archivo(self):
        borrar_archivo(self.archivo_ruta)
        self.archivo_original = ""
        self.archivo_ruta = ""

    async def remplazar_archivo(self):
        if not self.contenido_temp:
            return
        borrar_archivo(self.archivo_ruta)
        original, fisico = guardar_archivo(self.contenido_temp, self.archivo_temp)
        self.archivo_original = original
        self.archivo_ruta = fisico

    def cargar_reto(self, id_reto:int):
        print(id_reto)
        guard = self.requiere_staff()
        if guard: return guard
        reto = obtener_reto(id_reto)
        print(reto)
        if not reto:
            return rx.toast.error("Reto inexistente")
        if not puede_editar(reto, self.id_usuario,self.codigo_rol):
            return rx.toast.error("No puedes editar este reto.")
        catalogos = cargar_catalogos()
        self.categorias = catalogos["categorias"]
        self.dificultades = catalogos["dificultades"]
        self.modos = catalogos["modos"]
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
        self.pistas_existentes = listar_pista(id_reto)
        self.pistas_nuevas = []
        self.pista_costo = self.pista_desc = ""
        self.archivo_original = reto.archivo_original or ""
        self.archivo_ruta = reto.archivo_ruta or ""
        self.aislado_bool = aislado(id_reto)
        self.set_conservar()
        self.open_close_dialog()

    async def guardar(self):
        guard = self.requiere_staff()
        if guard: return guard
        reto = obtener_reto(self.id_reto)
        if not reto:
            self.mensaje="El reto no existe"
            return
        if not puede_editar(reto, self.id_usuario, self.codigo_rol):
            self.mensaje="No cuentas con permiso de edicion de retos"
            return
        values = {
            "titulo": self.titulo,            
            "descripcion": self.descripcion,
            "puntaje_inicial": int(self.puntaje_inicial),
            "puntaje_minimo": int(self.puntaje_minimo) if self.puntaje_minimo else None,
            "id_categoria": int(self.id_categoria),
            "id_dificultad": int(self.id_dificultad),
            "id_modo_puntaje": int(self.id_modo_puntaje),
            "archivo_original": self.archivo_original or None,
            "archivo_ruta": self.archivo_ruta or None,
        }
        if self.flag:
            values['flag'] = self.flag
        for p in self.pistas_existentes:
            editar_pista(p['id_pista'], p['costo'], p['descripcion'])
        for p in self.pistas_nuevas:
            if p['descripcion']:
                crear_pista(self.id_reto, p['costo'], p['descripcion'])
        editar_reto(self.id_reto,values)
        self.mensaje=f"Reto {self.titulo} actualizado."
        return True
    
    async def guardar_edit_completo(self):
        if not self.validar_campos():
            return
        if self.accion_archivo == "quitar":
                self.quitar_archivo()
        elif self.accion_archivo == "remplazar" and self.contenido_temp:
            await self.remplazar_archivo()
        if await self.guardar():
            listar = await self.get_state(ListarRetosState)
            listar.cargar_lista 
            self.open_close_dialog()
            self.limpiar()
            self.set_conservar()
            return rx.toast.success(self.mensaje)
           
    def validar_campos(self) -> bool:
        validaciones = [
            (self.titulo, "Se requiere el título"),
            (self.puntaje_inicial, "Se requiere el puntaje inicial"),
            (self.id_categoria, "Se requiere una categoría"),
            (self.id_dificultad, "Se requiere una dificultad"),
            (self.id_modo_puntaje, "Se requiere un modo de puntaje"),
        ]
        for valor, mensaje in validaciones:
            if not valor:
                self.mensaje = mensaje
                return False
        return True
    
    def limpiar(self):
            self.titulo = self.descripcion = self.flag = ""
            self.puntaje_inicial = self.puntaje_minimo = ""
            self.archivo_original = self.archivo_ruta = ""
            self.id_categoria = self.id_dificultad = self.id_modo_puntaje = ""
            self.pistas_nuevas = self.pistas_existentes = []
            self.pista_desc = self.pista_costo = ""
            self.contenido_temp = b""
            self.archivo_temp = ""
            self.pista_costo = self.pista_desc = ""