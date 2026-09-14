import reflex as rx
from itdb_ctf.scoreboard.scoreboard_state import ScoreboardState
from itdb_ctf.components.evolucion_chart import evolucion_chart

def grafica_evolucion() -> rx.Component:
    return rx.box(
        rx.text("Evolucion de puntaje", size="2", weight="medium", color_scheme="gray"),
        rx.cond(
            ScoreboardState.evolucion_vacia,
            rx.center(
                rx.text("Sin datos de evolucion todavia.", size="2",
                        weight="light", color_scheme="gray"),
                height="320px", width="100%",
            ),
            evolucion_chart(
                option=ScoreboardState.evolucion_opcion,
                width="100%",
            ),
        ),
        width="100%",
    )

def fila_ranking(fila:dict) -> rx.Component:
    return rx.box(
        rx.grid(
            rx.text(fila['posicion'],
                    weight="medium",
                    size="4",
            ),
            rx.text(
                fila['nombre'], 
                weight="medium", 
                size="3",
                on_click=rx.redirect(f"{ScoreboardState.perfil_base}/{fila['id_usuario']}"),
                cursor="pointer",
            ),
            rx.text(f"{fila['puntaje']} pts.",weight="medium", size="3"),
            place_items="center",
            spacing="2",
            grid_template_columns="1fr 50% 1fr",
            width="100%",
        ),
        width="100%",
        border_bottom="1px solid gray",
    ) 

def scoreboard_view() -> rx.Component:
    return rx.grid(
        rx.grid(
            rx.heading("Scoreboard", size="5"),
            rx.cond(
                ScoreboardState.solves,
                grafica_evolucion(),
            ),
            rx.grid(
                rx.text("Pocisión",weight="regular", size="3"),
                rx.text("Paticipante",weight="regular", size="3"),
                rx.text("puntaje",weight="regular", size="3"),
                place_items="center",
                spacing="2",
                grid_template_columns="1fr 50% 1fr",
                width="100%",
            ),
            rx.foreach(ScoreboardState.ranking, fila_ranking),
            rx.cond(
                ScoreboardState.no_solves,
                rx.text("Aun no hay puntajes",weight="light", size="3", color="gray"),
            ),
            spacing="3",
            place_items="center",
            width="100%",
        ),
        place_items="center",
        width=["90%", "90%", "90%", "60%"],
        spacing="5",
    )
