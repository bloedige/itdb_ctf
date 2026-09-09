import reflex as rx

from itdb_ctf.components.navbar import navbar
from itdb_ctf.perfil.perfil_state import PerfilGeneralState
from itdb_ctf.perfil.perfil_view import perfil_contenido


def perfil_page() -> rx.Component:
    return rx.vstack(
        navbar(),
        perfil_contenido(
            PerfilGeneralState,
            titulo="Mi perfil",
            vacio="No estás inscrito en el evento abierto.",
        ),
        width="100%",
        spacing="0",
    )
