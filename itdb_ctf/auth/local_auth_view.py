import os
import reflex as rx
from itdb_ctf.components.form import input_box
from itdb_ctf.auth.local_auth_state import LocalAuthState

# URL del backend (FastAPI). En prod single-port coincide con PUBLIC_URL.
BACKEND_URL = os.environ.get("API_URL") or os.environ.get("PUBLIC_URL") or "http://localhost:8000"

def logos() -> rx.Component:
    return rx.flex(
        rx.image(
            src="/itdb_logo.webp",
            width="5em",    
            objet_fit="cover",
        ),
        rx.flex(
            rx.flex(
                rx.text("INSTITUTO",weight="regular"),
                rx.text("TECNOLÓGICO",weight="regular"),
                font_size="1em",
                justify_content="space-between",
            ),
            rx.flex(
                rx.text("DON BOSCO", weight="bold"),
                width="100%",
                font_size="2em",
            ),
            rx.flex(
                rx.text("EL ALTO", weight="regular"),
                rx.text("•", weight="regular"),
                rx.text("LA PAZ", weight="regular"),
                rx.text("•", weight="regular"),
                rx.text("BOLIVIA", weight="regular"),
                color="#fab808",
                width="100%",
                font_size=".8em",
                justify_content="space-between",
            ),
            height="100%",
            direction="column",
            justify="between", 
            width="100%",     
        ),
        direction="row",
        width="100%",
        align="center",
        gap="1em",
    )

def login_institucional() -> rx.Component:
    return rx.button(
        rx.flex(
            rx.icon("at_sign", color="#ffffff"),
            rx.text("Iniciar sesión con cuenta institucional"),
            width="100%",
            align="center",
            justify_content="space-evenly",
        ),
        # window.location, NO rx.redirect: cuando la URL es del mismo origen
        # -- el caso en produccion, donde frontend y backend comparten puerto --
        # rx.redirect delega en el router de React, que busca /auth/login entre
        # las rutas del SPA, no la encuentra y muestra su propio 404 sin llegar
        # nunca al backend. Asi la navegacion la hace el navegador.
        on_click=rx.call_script(f'window.location.href = "{BACKEND_URL}/auth/login"'),
        width = "100%",
        height="auto",
        padding=".5em",
        bg="#013269C0",
    )
   
def login_local() -> rx.Component:
    return rx.grid(
        input_box("Correo electronico", "usuario@itdonbosco.org",LocalAuthState.email, LocalAuthState.set_email, "email"),
        input_box("Contraseña", "", LocalAuthState.password, LocalAuthState.set_password, "password"),
        rx.button("Ingresar", on_click=LocalAuthState.entrar_local, width="100%", padding=".5em", color_scheme="amber"),
        width="100%",
        spacing="4",
    )  

def separator(value:str) -> rx.Component:
    return rx.hstack(
                rx.divider(),
                rx.text(
                    value, white_space="nowrap", weight="medium"
                ),
                rx.divider(),
                align="center",
                width="100%",
            ),  
    
def login_card() -> rx.Component:
    return rx.box(
            rx.grid(
                logos(),
                separator("Acceso institucional"),
                login_institucional(),
                separator("Acceso local"),
                login_local(),
                spacing="3",
                width="100%",
            ),
            bg="#0115417E",
            padding="1em",
            border_radius=".5em",
        )