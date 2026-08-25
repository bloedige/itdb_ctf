import reflex as rx
from itdb_ctf.components.navbar import navbar
from itdb_ctf.auto_inscripcion.auto_inscripcion_evento_view import auto_inscripcion_eventos_view

def eventos_page() -> rx.Component:
    return rx.vstack(
        navbar(),
        auto_inscripcion_eventos_view(),
    )