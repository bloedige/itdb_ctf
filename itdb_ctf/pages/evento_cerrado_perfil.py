import reflex as rx

from itdb_ctf.components.navbar import navbar_cerrado
from itdb_ctf.evento_cerrado.evento_cerrado_informacion_state import EventoCerradoInfromacionState
from itdb_ctf.evento_cerrado.evento_cerrado_acceso_state import EventoCerradoAccesoState
from itdb_ctf.evento_cerrado.evento_cerrado_acceso_view import con_acceso
from itdb_ctf.perfil.perfil_state import PerfilEventoCerradoState
from itdb_ctf.perfil.perfil_view import perfil_contenido


def evento_cerrado_perfil_page() -> rx.Component:
    return rx.grid(
        navbar_cerrado(EventoCerradoInfromacionState.id_cerrado),
        con_acceso(
            perfil_contenido(
                PerfilEventoCerradoState,
                titulo="Mi perfil",
                vacio="No participaste en este evento.",
            ),
        ),
        width="100%",
        justify_items="center",
        spacing="0",
        on_mount=EventoCerradoAccesoState.escuchar_acceso,
        on_unmount=EventoCerradoAccesoState.parar_acceso,
    )
