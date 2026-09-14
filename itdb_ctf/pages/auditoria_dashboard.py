import reflex as rx

from itdb_ctf.components.navbar import navbar_staff
from itdb_ctf.dashboards.auditoria_dashboard_states import AuditoriaDashboardState
from itdb_ctf.dashboards.auditoria_dashboard_view import auditoria_dashboard_view


def auditoria_dashboard_page() -> rx.Component:
    return rx.grid(
        navbar_staff(),
        rx.flex(
            auditoria_dashboard_view(),
            width="100%",
            justify="center",
        ),
        width="100%",
        grid_template_columns=rx.breakpoints(initial="1fr", md="12% 1fr"),
        on_mount=AuditoriaDashboardState.escuchar_auditoria,
        on_unmount=AuditoriaDashboardState.parar_auditoria,
    )
