import reflex as rx
from itdb_ctf.auth.local_auth import verificar_credenciales
from itdb_ctf.auth.jwt_utils import emitir_jwt
from itdb_ctf.auth.auth_state import AuthState
from itdb_ctf.core.rate_limit import login_bloqueado, registrar_fallo_login, limpiar_login
from itdb_ctf.utils.validaciones import formato_email_valido

class LocalAuthState(AuthState):
    email: str = ""
    password: str = ""

    def set_email(self, v: str):
        self.email=v

    def set_password(self, v: str):
        self.password = v

    def entrar_local(self):
        ip = self.router.session.client_ip or "desconocida"
        bloqueado, faltan = login_bloqueado(ip, self.email)
        if bloqueado:
            return rx.toast.error(f"Demasiados intentos fallidos. Reintentá en {faltan} s.")
        usuario = verificar_credenciales(self.email,self.password)
        if not usuario:
            registrar_fallo_login(ip, self.email)
            return rx.toast.error("Credenciales inválidas.")
        limpiar_login(ip, self.email)
        self.token = emitir_jwt(usuario)
        match self.codigo_rol:
            case "autor":
                return rx.redirect("/admin/dashboard/retos")
            case "user":
                return rx.redirect("/informacion")
        return rx.redirect("/admin/dashboard")