import reflex as rx
from itdb_ctf.components.navbar import navbar
from itdb_ctf.views.catalogo_view import catalogo_view
from itdb_ctf.states.catalogo_states import CatalogoState,EnvioFlagState



def catalogo_page()->rx.Component:
    return rx.vstack(
        navbar(),
        rx.center(catalogo_view(),),
    )