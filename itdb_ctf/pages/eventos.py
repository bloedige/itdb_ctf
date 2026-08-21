import reflex as rx
from itdb_ctf.auto_inscripcion.aut_inscripcion_view import eventos_view

def eventos_page() -> rx.Component:
    return rx.vstack(
        eventos_view()
    )