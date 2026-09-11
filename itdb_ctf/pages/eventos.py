import reflex as rx
from itdb_ctf.components.navbar import navbar
from itdb_ctf.auto_inscripcion.auto_inscripcion_evento_view import auto_inscripcion_eventos_view
from itdb_ctf.auto_inscripcion.auto_inscripcion_evento_state import AutoInscripcionState

def eventos_page() -> rx.Component:
    return rx.grid(
        navbar(),
        auto_inscripcion_eventos_view(),
        justify_items="center",
        on_mount=AutoInscripcionState.escuchar_eventos,
        on_unmount=AutoInscripcionState.parar_eventos,
    )
