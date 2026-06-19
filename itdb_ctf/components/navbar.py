import reflex as rx 
from itdb_ctf.auth.auth_state import AuthState

def navbar() -> rx.Component:
    return rx.desktop_only(
        rx.hstack(
            rx.heading("ITDB CTF", size="5", weight="bold"),
            rx.spacer(),
            rx.cond(
                AuthState.autenticado,
                rx.button(rx.icon("log_out"), color_scheme="red", on_click=AuthState.logout)
            )
        )
    )