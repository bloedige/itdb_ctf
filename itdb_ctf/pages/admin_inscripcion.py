import reflex as rx 
from itdb_ctf.components.navbar import navbar_staff
from itdb_ctf.inscripcion.inscripcion_wiew import inscripcion_view

def admin_inscripcion_page() -> rx.Component:
    return rx.grid(
        navbar_staff(),
        inscripcion_view(),
        spacing="5",
        width="100%",
        grid_template_columns="12% 1fr",
    )