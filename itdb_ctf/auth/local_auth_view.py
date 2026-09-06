import reflex as rx
from itdb_ctf.components.navbar import logo
from itdb_ctf.components.form import input_box
from itdb_ctf.auth.local_auth_state import LocalAuthState

def logos() -> rx.Component:
    return rx.flex(
        
        rx.image(
            src="/itdb_logo.png",
            width="6em",    
            objet_fit="cover",
            margin="1em",
        ),
        rx.flex(
            rx.flex(
                rx.text("INSTITUTO TECNOLÓGICO", size="4", weight="regular"),
                justify_content="space-between",
            ),
            rx.flex(
                rx.text("DON", size="8", weight="bold"),
                rx.text("BOSCO", size="8", weight="bold"),
                justify_content="space-between",
            ),
            rx.flex(
                rx.text("EL ALTO", size="3", weight="regular"),
                rx.text("•", size="3", weight="regular"),
                rx.text("LA PAZ", size="3", weight="regular"),
                rx.text("•", size="3", weight="regular"),
                rx.text("BOLIVIA", size="3", weight="regular"),
                color="#fab808",
                gap=".5em",
                justify_content="center",
            ),
            height="100%",
            direction="column",
            padding="2em 0em" ,
            justify="between",      
        ),
        direction="row",
        width="100%",
        align="center",
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
        on_click=rx.redirect("http://localhost:8000/auth/login"),
        width = "100%",
        height="auto",
        padding=".5em",
        bg="#013269C0",
    ),
   
def login_local() -> rx.Component:
    return rx.grid(
        input_box("Correo electronico", "usuario@itdonbosco.org",LocalAuthState.email, LocalAuthState.set_email, "email"),
        input_box("Contraseña", "", LocalAuthState.email, LocalAuthState.set_password, "password"),
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
            )
        )