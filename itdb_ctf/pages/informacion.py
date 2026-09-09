import reflex as rx
from itdb_ctf.components.navbar import navbar
from itdb_ctf.informacion.informacion_view import informacion_view
from itdb_ctf.informacion.informacion_state import InformacionState

def informacion_page() -> rx.Component:
    return rx.grid(
        navbar(),
        informacion_view(),
        width="100%",
        place_items="center",
        on_mount=InformacionState.escuchar_info,
        on_unmount=InformacionState.parar_info,
    )
