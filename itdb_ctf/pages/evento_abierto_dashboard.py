import reflex as rx

from itdb_ctf.components.navbar import navbar_staff
from itdb_ctf.dashboards.evento_abierto_dashboard_view import evento_abierto_dashboard_view


def evento_abierto_dashboard_page() -> rx.Component:
    return rx.grid(
        navbar_staff(),
        rx.flex(
            evento_abierto_dashboard_view(),
            width="100%",
            justify="center",
        ),
        width="100%",
        grid_template_columns=rx.breakpoints(initial="1fr", md="12% 1fr"),
    )
