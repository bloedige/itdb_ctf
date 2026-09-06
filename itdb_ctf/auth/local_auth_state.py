import reflex as rx 
from itdb_ctf.components.form import badge_msg
from itdb_ctf.auth.local_auth import verificar_credenciales
from itdb_ctf.auth.jwt_utils import emitir_jwt
from itdb_ctf.auth.auth_state import AuthState

class LocalAuthState(AuthState):
    email: str = ""
    password: str = ""

    def set_email(self, v: str):
        self.email=v

    def set_password(self, v: str):
        self.password = v

    def entrar_local(self):
        usuario = verificar_credenciales(self.email,self.password)
        if not usuario: 
            return badge_msg("Credenciales invalidas.")
        self.token = emitir_jwt(usuario)
        if self.codigo_rol != "user":
            return rx.redirect("/admin/retos")
        return rx.redirect("/informacion")