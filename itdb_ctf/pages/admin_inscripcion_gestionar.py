import reflex as rx
from itdb_ctf.components.navbar import navbar_staff
from itdb_ctf.inscripcion.gestionar_inscripcion_view import gestionar_inscripcion_view
from itdb_ctf.inscripcion.inscripcion_state import GestionarInscripcionState

def admin_inscripcion_gestionar_page() -> rx.Component:
    return rx.grid(
        navbar_staff(),
        gestionar_inscripcion_view(),
        spacing="5",
        justify_items="center",
        width="100%",
        grid_template_columns=rx.breakpoints(initial="1fr", md="15rem 1fr"),
        on_mount=GestionarInscripcionState.escuchar_gestion,
        on_unmount=GestionarInscripcionState.parar_gestion,
    )
