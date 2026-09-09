import reflex as rx
from itdb_ctf.components.navbar import navbar_staff
from itdb_ctf.evento.eventos_view import eventos_view
from itdb_ctf.evento.evento_states import ListarEventoState

def admin_eventos_page() -> rx.Component:
    return rx.grid(
        navbar_staff(),
        rx.flex(
            eventos_view(),
            spacing="5",
            width="100%",
            justify="center",
        ),
        spacing="5",
        width="100%",
        grid_template_columns="12% 1fr",
        on_mount=ListarEventoState.escuchar_eventos_admin,
        on_unmount=ListarEventoState.parar_eventos_admin,
    )