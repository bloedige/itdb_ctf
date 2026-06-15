import reflex as rx 
from itdb_ctf.auth.local_auth import verificar_credenciales
from itdb_ctf.auth.jwt_utils import emitir_jwt
from itdb_ctf.auth.auth_state import AuthState

class LoginLocalState(AuthState):
    email: str = ""
    password: str = ""
    error: str = ""

    def set_emai(self, v: str):
        self.email=v

    def set_password(self, v: str):
        self.password = v

    def entrar_local(self):
        usuario = verificar_credenciales(self.email,self.password)
        if not usuario:
            self.error = "Credenciales invalidas"
            return
        self.token = emitir_jwt(usuario)
        self.error = ""
        return rx.redirect("/retos")
        
def login_page() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.heading("ITDB CTF"),
            rx.text("Acceso Institucional"),
            ### --- Google estudiantes, docentes---
            rx.link(
                rx.button(
                    rx.hstack(
                        rx.text("Iniciar sesión con google"),
                        rx.spacer(),
                        rx.icon("heart", color="red"),
                        width="100%"
                    ),
                    width = "100%"
                    ),
                href="http://localhost:8000/auth/login",
                width="100%",
            ),
            rx.divider(),
            rx.text("Acceso local"), 
            ### --- login local autores......
            rx.input(placeholder="Correo electronico", on_change=LoginLocalState.set_emai ,width="100%"),
            rx.input(placeholder="Contraseña",type="password", on_change=LoginLocalState.set_password,width="100%"),
            rx.button("Ingresar", on_click=LoginLocalState.entrar_local, width="100%"),
            rx.cond(
                LoginLocalState.error != "",    
                rx.text(LoginLocalState.error, color="red"),
            ),
            spacing="4",
            width="400px",     
        ),
        height="100vh"
    )
