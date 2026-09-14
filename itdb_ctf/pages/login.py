import reflex as rx
from itdb_ctf.components.navbar import logo
from itdb_ctf.auth.local_auth_view import login_card

def login_page() -> rx.Component:
    return rx.grid(
        rx.grid(
            rx.box(
                logo(),
                position="absolute",
                width="10%",
                top="1em",
                left="1em",
            ),
            login_card(),
            width="100%",
            height="80vh",
            place_items="center",
        ),
        rx.box(
            rx.center(
                rx.text(
                    "© 2026 Instituto Tecnológico Don Bosco — ITDB CTF",
                    size="1",
                    color="#8fa0c1",
                ),
                padding="0.6em",
            ),
            width="100%",
            bg="#011541BE",
            position="absolute",
            bottom="0",
        ),
        width="100%",
        height="100vh",
        justify_items="center",
        style={
            "background-image": "linear-gradient(#01154180, #01154180), url('/fondo.png')"
        }
    )
