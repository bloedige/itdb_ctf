import reflex as rx 
from itdb_ctf.auth.local_auth import verificar_credenciales
from itdb_ctf.auth.jwt_utils import emitir_jwt
from itdb_ctf.auth.auth_state import AuthState

class LoginLocalState(AuthState):
    email: str = ""
    password: str = ""
    error: str = ""

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
                        rx.icon("google")
                    ),
                    width = "100%"
                    ),
                href="/auth/login"
            ),
            rx.divider(),
            rx.text("Acceso local"), 
            ### --- login local autores......
            rx.input(placeholder="Correo electronico", on_change=LoginLocalState.set_email),
            rx.input(placeholder="Contraseña",type="password", on_change=LoginLocalState.set_password),
            rx.button("Ingresar", on_click=LoginLocalState.entrar_local, width="100%"),
            rx.cond(
                LoginLocalState.error != "",    
                rx.text(LoginLocalState.error, color="red"),
            ),
            spacing="4",
            width="320px",     
        ),
        height="100vh"
    )
