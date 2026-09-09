"""Componentes de UI compartidos por los dashboards de eventos.

Son funciones puras de Reflex parametrizadas por Vars; no dependen de ningún
State en particular.
"""

import reflex as rx

from itdb_ctf.components.evolucion_chart import evolucion_chart

COLORES = ["#00ffd0", "#ff7300", "#9dff00", "#8400ff", "#ff006a"]
COLORES_VAR = rx.Var.create(COLORES)

# paleta categórica (categorías de retos): 8 tonos distinguibles
CAT_COLORES = [
    "#00b8ff", "#00ffc3", "#ff9d00", "#8400ff",
    "#ff006a", "#9dff00", "#ffd000", "#ff5b5b",
]
CAT_COLORES_VAR = rx.Var.create(CAT_COLORES)

AZUL = "#00b8ff"
VERDE = "#00ffc3"
NARANJA = "#ff9d00"


def kpi(titulo: str, valor, detalle="") -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.text(titulo, size="1", weight="medium", color_scheme="gray"),
            rx.heading(valor, size="6"),
            rx.text(detalle, size="1", weight="light", color_scheme="gray"),
            spacing="1",
            align="start",
            width="100%",
        ),
        width="100%",
    )


def panel(titulo: str, contenido: rx.Component) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.text(titulo, size="2", weight="medium", color_scheme="gray"),
            contenido,
            spacing="3",
            width="100%",
            align="center",
        ),
        width="100%",
    )


def grafica_evolucion(opcion, titulo: str = "Evolución de puntaje · top 10") -> rx.Component:
    return panel(
        titulo,
        evolucion_chart(option=opcion, altura="300px", width="100%"),
    )


def grafica_desglose(titulo: str, data) -> rx.Component:
    return panel(
        titulo,
        rx.recharts.bar_chart(
            rx.recharts.bar(data_key="retos", name="Retos", fill=AZUL),
            rx.recharts.bar(data_key="resoluciones", name="Resoluciones", fill=VERDE),
            rx.recharts.x_axis(data_key="etiqueta"),
            rx.recharts.y_axis(),
            rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
            rx.recharts.graphing_tooltip(),
            rx.recharts.legend(),
            data=data,
            width="100%",
            height=280,
        ),
    )


def grafica_barra(
    titulo: str,
    data,
    data_key: str = "valor",
    nombre: str = "",
    x_key: str = "etiqueta",
    fill: str = AZUL,
) -> rx.Component:
    return panel(
        titulo,
        rx.recharts.bar_chart(
            rx.recharts.bar(data_key=data_key, name=nombre or titulo, fill=fill),
            rx.recharts.x_axis(data_key=x_key),
            rx.recharts.y_axis(),
            rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
            rx.recharts.graphing_tooltip(),
            data=data,
            width="100%",
            height=280,
        ),
    )


def grafica_pastel(
    titulo: str,
    data,
    colores_var,
    data_key: str = "valor",
    name_key: str = "etiqueta",
) -> rx.Component:
    return panel(
        titulo,
        rx.recharts.pie_chart(
            rx.recharts.pie(
                rx.foreach(data, lambda _d, i: rx.recharts.cell(fill=colores_var[i % 8])),
                data=data,
                data_key=data_key,
                name_key=name_key,
                cx="50%",
                cy="50%",
                inner_radius=55,
                outer_radius=90,
                padding_angle=1,
            ),
            rx.recharts.graphing_tooltip(),
            rx.recharts.legend(),
            width="100%",
            height=280,
        ),
    )


def _fila_ranking(fila: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(fila["posicion"]),
        rx.table.cell(fila["nombre"]),
        rx.table.cell(f"{fila['puntaje']} pts"),
    )


def panel_ranking(hay, ranking, titulo: str = "Ranking · top 10") -> rx.Component:
    return panel(
        titulo,
        rx.cond(
            hay,
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("N.º"),
                        rx.table.column_header_cell("Participante"),
                        rx.table.column_header_cell("Puntaje"),
                    ),
                ),
                rx.table.body(rx.foreach(ranking, _fila_ranking)),
                width="100%",
                height="35vh",
                overflow_y="auto",
            ),
            rx.text("Aún no hay puntajes.", size="2", weight="light", color_scheme="gray"),
        ),
    )
