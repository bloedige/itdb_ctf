import reflex as rx
from itdb_ctf.components.navbar import navbar_staff
from itdb_ctf.asociar.gestionar_asociar_reto_view import gestionar_asociar_reto_view
from itdb_ctf.asociar.asociar_state import GestionarRetoState

def admin_asociar_gestionar_page() -> rx.Component:
    return rx.grid(
        navbar_staff(),
        gestionar_asociar_reto_view(),
        spacing="5",
        justify_items="center",
        width="100%",
        grid_template_columns=rx.breakpoints(initial="1fr", md="15rem 1fr"),
        on_mount=GestionarRetoState.escuchar_gestionar,
        on_unmount=GestionarRetoState.parar_gestionar,
    )
