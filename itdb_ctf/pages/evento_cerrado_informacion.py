import reflex as rx
from itdb_ctf.components.navbar import navbar_cerrado
from itdb_ctf.evento_cerrado.evento_cerrado_informacion_view import evento_cerrado_informacion_view
from itdb_ctf.evento_cerrado.evento_cerrado_informacion_state import EventoCerradoInfromacionState

def evento_cerrado_informacion_page() -> rx.Component:
    return rx.vstack(
        navbar_cerrado(EventoCerradoInfromacionState.id_cerrado),
        evento_cerrado_informacion_view(),
        width="100%",
    )