import reflex as rx

from itdb_ctf.views.form_crear_evento_view import form_crear_evento_view
from itdb_ctf.views.tabla_eventos_view import tabla_eventos_view

def admin_eventos_page() -> rx.Component:
    return rx.vstack(
        form_crear_evento_view(),
        tabla_eventos_view(),

    )