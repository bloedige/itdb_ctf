import reflex as rx
from sqlmodel import Session,  select
from itdb_ctf.models import Usuario, Rol
from itdb_ctf.db import engine
from itdb_ctf.auth.jwt_utils import validar_jwt

ROLES_STAFF = {"superadmin","admin","autor"}
ROLES_ADMIN = {"superadmin","admin"} #agrege esto 


class AuthState(rx.State):
    # El JWT guardado como cookie (1 hora).
    token: str = rx.Cookie(name="token", max_age=3600)

 # --- VARIABLES CALCULADAS (@rx.var): solo LEEN, no hacen acciones ---

    @rx.var
    def payload(self) -> dict | None:
        if not self.token:
            return None
        return validar_jwt(self.token)
    
    @rx.var
    def autenticado(self) -> bool:
        return self.payload is not None
    
    @rx.var
    def id_usuario(self) -> int | None:
        p = self.payload
        return int(p["sub"]) if p else None
    
    @rx.var
    def codigo_rol(self) -> str:
        if not self.payload:
            return ""
        with Session(engine) as s:
            u = s.get(Usuario,int(self.payload["sub"]))
            if not u:
                return ""
            rol = s.get(Rol, u.id_rol)
            return rol.codigo if rol else ""
        
    @rx.var
    def es_staff(self) -> bool:
        return self.codigo_rol in ROLES_STAFF
    
    @rx.var
    def es_admin(self) -> bool:
        return self.codigo_rol in ROLES_ADMIN
    
 # --- EVENT HANDLERS (sin @rx.var): HACEN acciones (redirigen, borran) ---

    def requiere_login(self):
        if not self.autenticado:
            return rx.redirect("/login")
         
    def requiere_staff(self):
        if not self.autenticado:
            return rx.redirect("/login")
        if not self.es_staff:
            return rx.redirect("/retos")
        
    def requiere_admin(self):
        if not self.autenticado:
            return rx.redirect("/login")
        if not self.es_admin:
            return rx.redirect("/retos")
        
    def logout(self):
        self.token = ""
        return rx.redirect("/login")


