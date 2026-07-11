import reflex as rx
from itdb_ctf.views.asociar_view import asociar_view

def admin_asociar_page() -> rx.Component:
    return rx.vstack(
        asociar_view(),
    )