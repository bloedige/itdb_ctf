import reflex as rx
from itdb_ctf.components.navbar import navbar
from itdb_ctf.catalogo.catalogo_view import catalogo_view
from itdb_ctf.catalogo.catalogo_states import CatalogoState, listarPistaState

def catalogo_page()->rx.Component:
    return rx.vstack(
        navbar(),
        catalogo_view(),
        width="100%",
        on_mount=[CatalogoState.escuchar_catalogo, listarPistaState.escuchar_pistas],
        on_unmount=[CatalogoState.parar_catalogo, listarPistaState.parar_pistas],
    )
