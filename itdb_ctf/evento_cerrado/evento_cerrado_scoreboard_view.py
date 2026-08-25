import reflex as rx 
from itdb_ctf.scoreboard.scoreboard_view import scoreboard_view
from itdb_ctf.evento_cerrado.evento_cerrado_informacion_state import EventoCerradoContadorRegresivoFinalState, EventoCerradoInfromacionState

def evento_cerrado_scoreboard_view() -> rx.Component:
    return rx.grid(
        rx.grid(
            rx.moment(
                interval=1000,
                on_change=EventoCerradoContadorRegresivoFinalState.actualizar_tiempo,
                style={"display":"none"}
            ),
            rx.text("Cuenta regresiva", weight="light", size="3"),
            rx.text(EventoCerradoContadorRegresivoFinalState.contador_regresivo, weight="bold", size="8"),
            place_items="center",
        ),
        scoreboard_view(),
        width="100%",
        place_items="center",
    )