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


def sparkline(data, data_key: str = "valor", color: str = AZUL, altura: int = 46) -> rx.Component:
    """Mini-serie sin ejes, grilla ni tooltip: solo la forma de la tendencia."""
    return rx.recharts.area_chart(
        rx.recharts.area(
            data_key=data_key,
            type_="monotone",
            stroke=color,
            stroke_width=2,
            fill=color,
            fill_opacity=0.18,
            dot=False,
            is_animation_active=False,
        ),
        data=data,
        width="100%",
        height=altura,
        # margen propio: sin esto el trazo se pega al borde de la tarjeta
        margin={"top": 6, "right": 4, "left": 4, "bottom": 4},
    )


def _col_grafica(contenido: rx.Component, rotulo: str = "", ancho: str = "100%") -> rx.Component:
    """Columna de la gráfica, centrada en su celda. `ancho` deja respirar al
    trazo dentro del espacio que le toca."""
    return rx.vstack(
        contenido,
        rx.cond(
            rotulo != "",
            rx.text(
                rotulo,
                size="1",
                weight="light",
                color_scheme="gray",
                style={"font_size": "0.65em", "line_height": "1"},
            ),
            rx.fragment(),
        ),
        spacing="1",
        align="center",
        justify="center",
        width=ancho,
        height="100%",
    )


def _tarjeta_kpi(
    titulo: str, valor, detalle: str, columna: rx.Component, columns: str = "70% 30%"
) -> rx.Component:
    """Forma común de las tarjetas: texto | gráfica, con la proporción que se pida.
    Ambas columnas quedan centradas verticalmente."""
    return rx.card(
        rx.grid(
            rx.grid(
                rx.text(titulo, size="1", weight="medium", color_scheme="gray"),
                rx.heading(valor, size="6"),
                # `detalle` puede llegar como Var: nada de `if` sobre él
                rx.text(detalle, size="1", weight="light", color_scheme="gray"),
                spacing="1",
                align_items="center",
                justify_items="start",
                width="100%",
                height="100%",

            ),
            rx.center(columna, width="100%", height="100%"),
            columns=columns,
            align_items="center",
            justify_items="center",
            height="100%",
            spacing="2",
            width="100%",
        ),
        width="100%",
    )


def kpi_spark(
    titulo: str,
    valor,
    detalle: str,
    data,
    rotulo: str = "",
    data_key: str = "valor",
    color: str = AZUL,
) -> rx.Component:
    """Tarjeta con mini-serie temporal a la derecha.

    `rotulo` dice qué mide la línea (la serie no es la misma magnitud que el
    número grande, así que sin rótulo se lee ambigua).
    """
    return _tarjeta_kpi(
        titulo, valor, detalle,
        _col_grafica(sparkline(data, data_key, color), rotulo, ancho="90%"),
        columns="60% 40%",
    )


# repartos de 2 y 3 tramos (activo/inactivo, roles de staff)
REPARTO_COLORES = rx.Var.create([VERDE, "#ff6b6b"])
STAFF_COLORES = rx.Var.create(["#8400ff", "#00b8ff", "#ffd000"])


def _barra_reparto(d: dict, i, colores, con_valor: bool = False) -> rx.Component:
    """Barra con su etiqueta. `con_valor` añade el valor absoluto al final, para
    las tarjetas que no llevan detalle de texto. Nunca el porcentaje."""
    fila = [
        rx.box(
            width="8px", height="8px", border_radius="2px",
            background=colores[i], flex_shrink="0",
        ),
        rx.text(
            d["etiqueta"],
            size="1", weight="light", color_scheme="gray",
            width="100%",
        ),
        rx.box(
            rx.box(
                width=f"{d['pct']}%",
                height="6px",
                border_radius="3px",
                background=colores[i],
            ),
            flex="1",
            height="6px",
            border_radius="3px",
            background="var(--gray-a4)",
            width="100%",
        ),
    ]
    if con_valor:
        fila.append(
            rx.text(
                d["valor"],
                size="1", weight="medium",
                width="2.2em", text_align="right", flex_shrink="0",
            )
        )
    return rx.grid(*fila, width="100%", align_items="center", spacing="2", grid_template_columns="5% 1fr 1fr 5%")


def kpi_barras(
    titulo: str, valor, detalle: str, data, colores=REPARTO_COLORES,
    con_valor: bool = False,
) -> rx.Component:
    """Tarjeta con el reparto en barras a la derecha. Las cifras van en el
    detalle, o en las propias barras si la tarjeta no lleva detalle."""
    return _tarjeta_kpi(
        titulo, valor, detalle,
        _col_grafica(
            rx.grid(
                rx.foreach(data, lambda d, i: _barra_reparto(d, i, colores, con_valor)),
                spacing="2",
                align_items="center",
                width="80%",
            ),
        ),
        columns="20% 80%",
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
