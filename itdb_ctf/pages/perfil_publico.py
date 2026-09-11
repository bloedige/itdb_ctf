import reflex as rx

from itdb_ctf.components.navbar import navbar
from itdb_ctf.perfil.perfil_state import PerfilPublicoAbiertoState
from itdb_ctf.perfil.perfil_view import perfil_contenido


def perfil_publico_page() -> rx.Component:
    return rx.grid(
        navbar(),
        perfil_contenido(
            PerfilPublicoAbiertoState,
            titulo="Perfil",
            vacio="Ese usuario no participa en el evento abierto.",
            mostrar_email=False,
        ),
        justify_items="center",
        width="100%",
        spacing="0",
    )
