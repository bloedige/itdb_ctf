import reflex as rx
from itdb_ctf.components.navbar import navbar_staff
from itdb_ctf.evento.form_crear_evento_view import form_crear_evento_view
from itdb_ctf.evento.tabla_eventos_view import tabla_eventos_view

def admin_eventos_page() -> rx.Component:
    return rx.grid(
        navbar_staff(),
        rx.grid(
            tabla_eventos_view(),
            form_crear_evento_view(),
            spacing="5",
            width="100%",
            grid_template_columns="80% 1fr",
        ),
        spacing="5",
        width="100%",
        grid_template_columns="12% 1fr",

    )