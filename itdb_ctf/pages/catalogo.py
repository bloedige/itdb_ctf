import reflex as rx
from itdb_ctf.components.navbar import navbar
from itdb_ctf.catalogo.catalogo_view import catalogo_view

def catalogo_page()->rx.Component:
    return rx.vstack(
        navbar(),
        catalogo_view(),
        width="100%",
    )