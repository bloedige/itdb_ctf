import reflex as rx 

from itdb_ctf.components.navbar import navbar
from itdb_ctf.views.form_crear_reto import form_crear_reto

def admin_retos_page() -> rx.Component:
    return rx.vstack(
        navbar(),
        form_crear_reto(),
    )