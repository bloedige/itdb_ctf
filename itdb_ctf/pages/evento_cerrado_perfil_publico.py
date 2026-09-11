import reflex as rx

from itdb_ctf.components.navbar import navbar_cerrado
from itdb_ctf.evento_cerrado.evento_cerrado_informacion_state import EventoCerradoInfromacionState
from itdb_ctf.perfil.perfil_state import PerfilPublicoCerradoState
from itdb_ctf.perfil.perfil_view import perfil_contenido


def evento_cerrado_perfil_publico_page() -> rx.Component:
    # Vitrina pública: mismo criterio que Información/Scoreboard, no pasa por
    # `EventoCerradoAccesoState`/`con_acceso` (esos exigen inscripción del
    # VISITANTE en Retos/Perfil propio; acá solo importa que el usuario del
    # link haya participado, lo que valida `PerfilPublicoCerradoState`).
    return rx.vstack(
        navbar_cerrado(EventoCerradoInfromacionState.id_cerrado),
        perfil_contenido(
            PerfilPublicoCerradoState,
            titulo="Perfil",
            vacio="Ese usuario no participó en este evento.",
            mostrar_email=False,
        ),
        width="100%",
        spacing="0",
    )
