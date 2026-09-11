import reflex as rx

from itdb_ctf.components.navbar import navbar_staff
from itdb_ctf.dashboards.eventos_cerrados_dashboard_view import eventos_cerrados_dashboard_view
from itdb_ctf.dashboards.eventos_cerrados_dashboard_states import EventosCerradosDashboardState


def eventos_cerrados_dashboard_page() -> rx.Component:
    return rx.grid(
        navbar_staff(),
        rx.flex(
            eventos_cerrados_dashboard_view(),
            width="100%",
            justify="center",
        ),
        width="100%",
        grid_template_columns=rx.breakpoints(initial="1fr", md="15rem 1fr"),
        on_mount=EventosCerradosDashboardState.escuchar,
        on_unmount=EventosCerradosDashboardState.parar,
    )
