import reflex as rx 
from itdb_ctf.views.inscripcion_wiew import inscripcion_view

def admin_inscripcion_page() -> rx.Component:
    return rx.vstack(
        inscripcion_view(),
        spacing="5",
        width="100%",
    )