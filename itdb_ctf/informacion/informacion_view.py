import reflex as rx 
from itdb_ctf.informacion.informacion_state import InformacionState

def informacion_view() -> rx.Component:
    return rx.grid(
        rx.heading("Información", size="5"),
        rx.markdown(InformacionState.desc, width="100%"),
        width="60%", spacing="4",
    ),