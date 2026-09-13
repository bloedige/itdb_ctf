import reflex as rx
from itdb_ctf.components.navbar import navbar_staff
from itdb_ctf.asociar.asociar_reto_view import asociar_reto_view
from itdb_ctf.asociar.asociar_state import AsociarRetoState

def admin_asociar_page() -> rx.Component:
    return rx.grid(
        navbar_staff(),
        asociar_reto_view(),
        spacing="4",
        width="100%",
        grid_template_columns=rx.breakpoints(initial="1fr", md="12% 1fr"),
        justify_items="center",
        on_mount=AsociarRetoState.escuchar_asociar,
        on_unmount=AsociarRetoState.parar_asociar,
    )
