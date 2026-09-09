import reflex as rx
from itdb_ctf.components.navbar import navbar_staff
from itdb_ctf.reto.retos_view import retos_view
from itdb_ctf.reto.reto_states import ListarRetosState

def admin_retos_page() -> rx.Component:
    return rx.grid(
        navbar_staff(),
        rx.flex(
            retos_view(),
            spacing="5",
            width="100%",
            justify="center",
        ),
        spacing="5",
        width="100%",
        grid_template_columns="12% 1fr",
        on_mount=ListarRetosState.escuchar_retos_admin,
        on_unmount=ListarRetosState.parar_retos_admin,
    )