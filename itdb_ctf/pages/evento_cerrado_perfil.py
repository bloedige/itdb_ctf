import reflex as rx
from itdb_ctf.components.navbar import navbar_cerrado
from itdb_ctf.evento_cerrado.evento_cerrado_perfil_view import evento_cerrado_perfil_view
from itdb_ctf.evento_cerrado.evento_cerrado_informacion_state import EventoCerradoInfromacionState

def evento_cerrado_perfil_page() -> rx.Component:
    return rx.vstack(
        navbar_cerrado(EventoCerradoInfromacionState.id_cerrado),
        evento_cerrado_perfil_view(),
        width="100%",
    )