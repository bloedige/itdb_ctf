import reflex as rx 
from itdb_ctf.evento_cerrado.evento_cerrado_informacion_state import EventoCerradoInfromacionState, EventoCerradoContadorRegresivoFinalState

def evento_cerrado_informacion_view() -> rx.Component:
    return rx.cond(
        EventoCerradoInfromacionState.encontrado,
        rx.grid(
            rx.heading(EventoCerradoInfromacionState.titulo),
            rx.grid(
                rx.grid(
                    rx.text("Inicia", weight="light", size="3"),
                    rx.text(EventoCerradoInfromacionState.fi_str, weight="medium", size="5"),
                    place_items="center",
                ),
                rx.grid(
                    rx.text("Finaliza", weight="light", size="3"),
                    rx.text(EventoCerradoInfromacionState.ff_str, weight="medium", size="5"),
                    place_items="center",
                ),
                width="60%", columns="2", place_items="center",
            ),
            rx.markdown(EventoCerradoInfromacionState.desripcion, width="60%"),
            width="100%", spacing="4", place_items="center",
            
        ),
        rx.center(
            rx.text("Evento no encontrado.", weight="medium", size="4", color_scheme="gray"),
            height="50vh",
        ),
    )