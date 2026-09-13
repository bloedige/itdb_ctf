import reflex as rx
from itdb_ctf.components.navbar import navbar_staff
from itdb_ctf.evento.eventos_view import eventos_view
from itdb_ctf.evento.evento_states import ListarEventoState

def admin_eventos_page() -> rx.Component:
    return rx.grid(
        navbar_staff(),
        eventos_view(),
        spacing="4",
        justify_items="center",
        width="100%",
        grid_template_columns=rx.breakpoints(initial="1fr", md="12% 1fr"),
        on_mount=ListarEventoState.escuchar_eventos_admin,
        on_unmount=ListarEventoState.parar_eventos_admin,
    )