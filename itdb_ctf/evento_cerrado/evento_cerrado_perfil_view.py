import reflex as rx
from itdb_ctf.evento_cerrado.evento_cerrado_perfil_state import EventoCerradoPerfilState

def evento_cerrado_perfil_view() -> rx.Component:
    return rx.vstack(
        rx.center(
            rx.text("dashboard perfil pendiente", weight="light", size="5", color_scheme="gray", height="50vh"),

        ),
        width="100%",
    )