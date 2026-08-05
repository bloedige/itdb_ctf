import reflex as rx
from itdb_ctf.scoreboard.scoreboard_state import ScoreboardState

COLORES = ["#00ffd0","#ff7300","#9dff00","#8400ff","#ff006a"]
COLORES_VAR = rx.Var.create(COLORES)
COLORES_STROKE = ["#00382e","#4b2200","#315001","#2b0053","#41001b"]
COLORES_STK_VAR = rx.Var.create(COLORES_STROKE)

def grafica_evolucion() -> rx.Component:
    return rx.grid(
        rx.text("Evolucion de puntaje", size="2", weight="medium", color_scheme="gray"),
        rx.recharts.line_chart(
            rx.foreach(
                ScoreboardState.lineas,
                lambda nombre, i: rx.recharts.line(
                    data_key=nombre,
                    type_="monotone",
                    stroke=COLORES_VAR[i % 5],
                    dot=False,
                    active_dot=False,
                    connect_nulls=False,
                ),
            ),
            rx.recharts.x_axis(data_key="fecha", hide=True),
            rx.recharts.y_axis(),
            rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
            rx.recharts.tooltip(
                is_animation_active=False,
                wrapper_style={"textAlign": "center"},
                label_style={"font-size":".8em"},
                item_style={},
                custom_attrs={"itemSorter": "none"},
                trigger="hover",
            ),
            rx.recharts.legend(icon_type="diamond"),
            data=ScoreboardState.grafica,
            width="60%",
            height=300,
        ),
        place_items="center",
        width="100%",
    )

def fila_ranking(fila:dict) -> rx.Component:
    return rx.card(
        rx.grid(
            rx.text(fila['posicion'],weight="medium", size="3"),
            rx.text(fila['nombre'],weight="medium", size="3"),
            rx.text(f"{fila['puntaje']} pts.",weight="medium", size="3"),
            place_items="center",
            spacing="2",
            grid_template_columns="1fr 50% 1fr",
            width="100%",
        ),
        width="100%",
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
        width="80%",
        spacing="5",
    )
