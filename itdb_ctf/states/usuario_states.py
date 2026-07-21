import reflex as rx 
from sqlmodel import select, Session
from itdb_ctf.db import engine
from itdb_ctf.models import Rol, MetodoAuth
from itdb_ctf.auth.auth_state import AuthState
from itdb_ctf.usuario import usuario_logic as user

class CredencialesUsuarioState(AuthState):
    cred_titulo:str = ""
    cred_email:str = ""
    cred_alias:str = ""
    cred_password:str = ""
    cred_rol:str = ""
    cred_bool:bool = False
    
    @rx.var
    def credenciales(self) -> str:
        return f"""     
               -----------------------------------------------------
                      CREDENCIALES
        -----------------------------------------------------
        {self.cred_titulo}
        -----------------------------------------------------
        email: {self.cred_email}
        contraseña: {self.cred_password}
        -----------------------------------------------------
        rol: {self.cred_rol}
        alias: {self.cred_alias if self.cred_alias else '---'}
        -----------------------------------------------------
        """.strip()

    def open_credenciales(self, titulo:str, email:str, alias:str , password:str, rol:str):
        self.cred_bool = True
        self.cred_titulo = titulo
        self.cred_email = email
        self.cred_alias =  alias or "---"
        self.cred_password = password
        self.cred_rol = rol

    def close_credenciales(self):
        self.cred_bool = False
        self.cred_titulo = self.cred_email = self.cred_alias = self.cred_password = self.cred_rol = ""

    def copiar(self):
        return [rx.set_clipboard(self.credenciales), rx.toast.success("Credenciales copiadas.")]        
    

class CrearUsuarioState(AuthState):
    nombre:str = ""
    paterno:str = ""
    materno:str= ""
    alias:str= ""
    email:str= ""
    id_rol:str= ""
    mensaje:str= ""

    roles: list[tuple[str,str]] = []
    dialog_bool:bool = False

    def set_nombre(self, v:str):
        self.nombre = v
    def set_paterno(self, v:str):
        self.paterno = v
    def set_materno(self, v:str):
        self.materno = v
    def set_alias(self, v:str):
        self.alias = v
    def set_email(self, v:str):
        self.email = v
    def set_id_rol(self, v:str):
        self.id_rol = v
    def set_drop_mensaje(self):
        self.mensaje = ""

    def open_close_dialog(self):
        self.dialog_bool = not self.dialog_bool

    def cargar_catoalogos(self):
        guard = self.requiere_admin()
        if guard: return guard
        self.roles = user.roles_asignables(self.codigo_rol)
    
    def validar_campos(self) -> bool:
        validaciones = [
            (self.nombre, "Se requiere campo nombre"),
            (self.paterno, "Se requiere campo paterno"),
            (self.email, "Se requiere campo email"),
            (self.id_rol, "Se requiere selección de rol"),
        ]
        for v, msg in validaciones:
            if not v:
                self.mensaje = msg
                return False
        if "@" not in self.email:
            self.mensaje = "Correo no valido"
            return False
        return True
        
    def guardar(self) -> str:
        try:
            return user.crear_cuenta(self.nombre, self.paterno, self.materno, self.alias, self.email, int(self.id_rol), self.codigo_rol)
        except ValueError as e:
            self.mensaje = str(e)
            return ""
        except Exception as e:
            self.mensaje =  f"error: {e}"
            return ""


    async def guardar_completo(self):
        guard = self.requiere_admin()
        if guard: return guard
        if not self.validar_campos():
            return 
        password = self.guardar()
        if password: 
            listar  = await self.get_state(ListarUsuarioState)
            listar.cargar_lista()
            credenciales = await self.get_state(CredencialesUsuarioState)
            credenciales.open_credenciales("Cuenta creada", self.email, self.alias, password, user.id_rol_eti(int(self.id_rol)))
            self.open_close_dialog()
            self.limpiar()
        return
    
    def limpiar(self):
        self.nombre = self.paterno = self.materno = ""
        self.email = self.alias = self.id_rol = ""


class ListarUsuarioState(AuthState):
    lista:list[dict] = []
    busqueda:str = ""
    id_rol_filtro:str = ""
    id_metodo_filtro:str = ""
    activo_filtro:str = ""

    roles:list[tuple[str,str]] = []
    roles_asignables:list[tuple[str,str]] = []
    metodos:list[tuple[str,str]] = []
    estados:list[tuple[str,str]] = []

    def set_busqueda(self, v:str):
        self.busqueda = v
        return ListarUsuarioState.cargar_lista
    def set_id_rol_filtro(self, v:str):
        self.id_rol_filtro = v
        return ListarUsuarioState.cargar_lista
    def set_id_metodo_filtro(self, v:str):
        self.id_metodo_filtro = v
        return ListarUsuarioState.cargar_lista
    def set_activo_filtro(self, v:str):
        self.activo_filtro = v
        return ListarUsuarioState.cargar_lista
    
    def cargar_catalogos(self):
        guard = self.requiere_admin()
        if guard: return guard
        with Session(engine) as s:
            self.roles =[("","Todos los roles")]+[(str(r.id_rol), r.etiqueta)for r in s.exec(select(Rol)).all()]
            self.metodos=[("","Todos los roles")]+[(str(m.id_metodo_auth), m.etiqueta)for m in s.exec(select(MetodoAuth)).all()]
        self.roles_asignables = user.roles_asignables(self.codigo_rol)
        self.estados = [("","Todos"),("1","Activos"),("0","Inactivos")]

    def cargar_lista(self):
        guard = self.requiere_admin()
        if guard: return guard
        rol = int(self.id_rol_filtro) if self.id_rol_filtro else None
        met = int(self.id_metodo_filtro) if self.id_metodo_filtro else None
        act = (self.activo_filtro == "1") if self.activo_filtro else None
        self.lista = user.listar_usuarios(self.busqueda or None, rol, met, act ,self.id_usuario, self.codigo_rol)
        print(self.lista)
    
    def altenar_activo(self, id_usuario:int):
        guard = self.requiere_admin()
        if guard: return guard
        try:
            user.activar_desactivar(id_usuario, self.id_usuario,self.codigo_rol),
        except ValueError as e:
            return rx.toast.error(str(e))
        self.cargar_lista()
        return rx.toast.success("Estado actualizado")
        
class EditarUsuarioState(AuthState):
    id_usuario_edit:int = 0
    nombre:str = ""
    paterno:str = ""
    materno:str = ""
    email:str = ""
    alias:str = ""
    mensaje:str = ""
    id_rol:str = ""
    dilog_bool:bool = False

    roles:list[tuple[str,str]] = []
    
    def set_nombre(self, v:str):
        self.nombre = v
    def set_paterno(self, v:str):
        self.paterno = v
    def set_materno(self, v:str):
        self.materno= v
    def set_email(self, v:str):
        self.email = v
    def set_alias(self, v:str):
        self.alias = v
    def set_id_rol(self, v:str):
        self.id_rol = v
    def set_drop_mensaje(self):
        self.mensaje = ""

    def open_close_dialog(self):
        self.dilog_bool = not self.dilog_bool

    def cargar_roles(self):
        self.roles = user.roles_asignables(self.codigo_rol)

    def cargar_usario(self, id_usuario:int):
        guard = self.requiere_admin()
        if guard: return guard
        self.cargar_roles()
        u = user.obtener_usuario(id_usuario)
        if not u: return rx.toast.warning("Usuario no obtenido")
        self.id_usuario_edit = u.id_usuario
        self.nombre = u.nombre
        self.paterno = u.paterno
        self.materno = u.materno or ""
        self.alias = u.alias or ""
        self.email = u.email_inst
        self.id_rol = str(u.id_rol)
        self.mensaje = ""

    def validar_campos(self) -> bool:
        validaciones = {
            (self.nombre, "Se requiere campo nombre"), 
            (self.paterno, "Se requiere campo paterno"),
            (self.email, "Se requiere campo correo"),
            (self.id_rol, "Se requiere rol"),
        }
        for v, msg in validaciones:
            if not v:
                self.mensaje = msg
                return False
        if "@" not in self.email:
            self.mensaje = "Correo invalido"
            return False
        return True
    
    def guardar(self) -> bool:
        values = {
            "nombre":self.nombre,
            "paterno":self.paterno,
            "materno":self.materno or None,
            "alias":self.alias or None,
            "email_inst":self.email,
            "id_rol": int(self.id_rol),
        }
        try:
            user.editar_usuario(self.id_usuario_edit, values, self.id_usuario, self.codigo_rol)
        except ValueError as e:
            self.mensaje = str(e)
            return False
        except Exception as e:
            self.mensaje = f"error: {e}"
            return False
        return True
    
    async def guardar_edit_completo(self):
        guard = self.requiere_admin()
        if guard: return guard
        if not self.validar_campos():
            return 
        if self.guardar():
            listar = await self.get_state(ListarUsuarioState)
            listar.cargar_lista()
            self.open_close_dialog()
            self.limpiar()
            self.set_drop_mensaje()
            return rx.toast.success("Datos de cuenta actualizado")
            
    def limpiar(self):
        self.id_usuario_edit = 0
        self.nombre = self.paterno = self.materno = self.alias = self.email = self.id_rol = "" 
    
    async def resetear_password(self, id_usuario:int, email:str, alias:str, rol:str):
        guard = self.requiere_admin()
        if guard: return guard  
        try:
            password = user.reset_password(id_usuario, self.id_usuario, self.codigo_rol)
        except ValueError as e:
            return rx.toast.error(str(e))
        credenciales = await self.get_state(CredencialesUsuarioState)
        credenciales.open_credenciales("Contraseña Restablecida",email,alias,password,rol)
    
