import reflex as rx 
from itdb_ctf.components.navbar import navbar_staff
from itdb_ctf.reto.form_crear_reto import form_crear_reto
from itdb_ctf.reto.tabla_retos_view import tabla_retos_view

def admin_retos_page() -> rx.Component:
    return rx.grid(
        navbar_staff(),
        rx.grid(        
            tabla_retos_view(),
            form_crear_reto(),
            spacing="5",
            width="100%",
            grid_template_columns="80% 1fr",
        ),
        spacing="5",
        width="100%",
        grid_template_columns="12% 1fr",
    )