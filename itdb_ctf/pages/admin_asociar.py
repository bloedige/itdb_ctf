import reflex as rx
from itdb_ctf.components.navbar import navbar_staff
from itdb_ctf.asociar.asociar_view import asociar_view
from itdb_ctf.asociar.asociar_state import AsociarState

def admin_asociar_page() -> rx.Component:
    return rx.grid(
        navbar_staff(),
        asociar_view(),
        spacing="5",
        width="100%",
        grid_template_columns="12% 1fr",
        on_mount=AsociarState.escuchar_asociar,
        on_unmount=AsociarState.parar_asociar,
    )