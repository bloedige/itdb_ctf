import reflex as rx
from itdb_ctf.scoreboard.scoreboard_state import ScoreboardState

COLORES = ["#00ffd0","#ff7300","#9dff00","#8400ff","#ff006a"]
COLORES_VAR = rx.Var.create(COLORES)
BG_COLORES = ["#00ffd010","#ff730010","#9dff0010","#8400ff10","#ff006a10"]
BG_COLORES_VAR = rx.Var.create(BG_COLORES)

def grafica_evolucion() -> rx.Component:
    return rx.grid(
        rx.text("Evolucion de puntaje", size="2", weight="medium", color_scheme="gray"),
        rx.recharts.line_chart(
            rx.foreach(
                ScoreboardState.series,
                lambda serie, i: rx.recharts.line(
                    data_key=serie["key"],     
                    name=serie["nombre"],       
                    type_="monotone",
                    stroke=COLORES_VAR[i % 5],
                    dot=True,                   
                    connect_nulls=True,         
                ),
            ),
            rx.recharts.x_axis(data_key="fecha", hide=True),
            rx.recharts.y_axis(),
            rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
            data=ScoreboardState.grafica,
            width="90%",
            height=300,
        ),
        place_items="center",
        width="100%",
    )

def fila_ranking(fila:dict) -> rx.Component:
    return rx.card(
        rx.grid(
            rx.text(fila['posicion'],
                    weight="medium",
                    size="4",
            ),
            rx.text(fila['nombre'],weight="medium", size="3"),
            rx.text(f"{fila['puntaje']} pts.",weight="medium", size="3"),
            place_items="center",
            spacing="2",
            grid_template_columns="1fr 50% 1fr",
            width="100%",
        ),
        rx.icon(tag="1st",
            color=rx.match(
                    fila['posicion'],
                    (1, COLORES_VAR[0]),
                    (2, COLORES_VAR[1]),
                    (3, COLORES_VAR[2]),
                    (4, COLORES_VAR[3]),
                    (5, COLORES_VAR[4]),
                    "",
            ),
            style={},
            position="absolute",
            top=".9em",
            right=".9em",
        ),
        width="100%",
        #bg=rx.match(
        #    fila['posicion'],
        #    (1, BG_COLORES_VAR[0]),
        #    (2, BG_COLORES_VAR[1]),
        #    (3, BG_COLORES_VAR[2]),
        #    (4, BG_COLORES_VAR[3]),
        #    (5, BG_COLORES_VAR[4]),
        #    "",
        #),
    ) 

def scoreboard_view() -> rx.Component:
    return rx.grid(
        rx.grid(
            rx.heading("Scoreboard"),
            rx.cond(
                ScoreboardState.solves,
                grafica_evolucion(),
            ),
            rx.grid(
                rx.text("N#",weight="regular", size="3"),
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
        width=["90%", "90%", "90%", "50%"],
        spacing="5",
    )
