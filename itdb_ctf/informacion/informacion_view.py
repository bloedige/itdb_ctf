import reflex as rx 
from itdb_ctf.informacion.informacion_state import InformacionState

def informacion_view() -> rx.Component:
    return rx.grid(
        rx.markdown(InformacionState.desc, width="60%"),
        width="100%", spacing="4", place_items="center",
    ),