import reflex as rx
from itdb_ctf.components.navbar import navbar_staff
from itdb_ctf.inscripcion.inscribir_view import inscribir_view
from itdb_ctf.inscripcion.inscripcion_state import InscribirState

def admin_inscripcion_page() -> rx.Component:
    return rx.grid(
        navbar_staff(),
        inscribir_view(),
        spacing="5",
        justify_items="center",
        width="100%",
        grid_template_columns="12% 1fr",
        on_mount=InscribirState.escuchar_insc,
        on_unmount=InscribirState.parar_insc,
    )
