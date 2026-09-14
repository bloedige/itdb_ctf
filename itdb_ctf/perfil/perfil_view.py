import reflex as rx

from itdb_ctf.dashboards.dashboard_componentes import CAT_COLORES_VAR, VERDE, NARANJA
from itdb_ctf.components.evolucion_chart import evolucion_chart

PIE_COLORES_VAR = rx.Var.create(["#00ffc3", "#ff6b6b"])  # aciertos, errores
REPARTO_COLORES_VAR = rx.Var.create([VERDE, NARANJA])  # puntaje conservado, en pistas


def _card(titulo, contenido) -> rx.Component:
    """Igual que dashboards.panel pero con el padding del card ajustado (simétrico)."""
    return rx.card(
        rx.vstack(
            rx.text(titulo, size="2", weight="medium", color_scheme="gray"),
            contenido,
            spacing="3",
            width="100%",
            align="center",
        ),
        width="100%",
        style={"--card-padding": "0.75em"},
    )


def card_identidad(E, mostrar_email: bool = True) -> rx.Component:
    d = E.datos
    identidad = [rx.heading(d["alias"], size="3")]
    if mostrar_email:
        identidad.append(rx.text(d["email"], size="1", color_scheme="gray"))
    return rx.card(
        rx.flex(
            rx.flex(
                rx.avatar(fallback=d["iniciales"], size="4",),
                rx.vstack(
                    *identidad,
                    spacing="1",
                    align="start",
                ),
                spacing="3",
                align="center",
                justify="start",
                direction="row",
                gap="1em",
            ),
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.text("Puntaje", size="1", color_scheme="gray"),
                        rx.heading(d["puntaje"], size="3"),
                        spacing="0", align="center",
                    ),
                    rx.vstack(
                        rx.text(f"Posición de {d['total']}", size="1", color_scheme="gray"),
                        rx.heading(f"#{d['posicion']}", size="3"),
                        spacing="0", align="center",
                    ),
                    rx.vstack(
                        rx.text("Resueltos", size="1", color_scheme="gray"),
                        rx.heading(d["resueltos"], size="3"),
                        spacing="0", align="center",
                    ),
                    justify="between",
                ),
                rx.vstack(
                    rx.hstack(
                        rx.text("Progreso", size="2", weight="medium", color_scheme="gray"),
                        rx.spacer(),
                        rx.text(
                            f"{d['resueltos']} / {d['retos_total']} retos · {d['pct_progreso']}%",
                            size="2", weight="medium",
                        ),
                        width="100%",
                    ),
                    rx.progress(value=d["pct_progreso"], width="100%"),
                    spacing="2",
                    width="100%",
                ),
                justify="between",
                width="100%",
            ),
            direction="row",
            gap="1em",
            spacing="3",
            width="100%",
            justify_items="start",
            align_items="center",
        ),
        width="100%",
        style={"--card-padding": "0.75em"},
    )

def _fila_alloc(d: dict, i: int, colores) -> rx.Component:
    return rx.hstack(
        rx.box(
            width="10px", height="10px", border_radius="2px",
            background=colores[i], flex_shrink="0",
        ),
        rx.text(d["etiqueta"], size="2", width="7em", flex_shrink="0"),
        rx.box(
            rx.box(
                width=f"{d['pct']}%", height="8px", border_radius="4px",
                background=colores[i],
            ),
            flex="1", height="8px", border_radius="4px",
            background="var(--gray-a4)",
        ),
        rx.text(f"{d['pct']}%", size="2", weight="medium", width="3.5em", text_align="right", flex_shrink="0"),
        rx.text(f"({d['valor']})", size="1", color_scheme="gray", flex_shrink="0"),
        width="100%",
        align="center",
        spacing="2",
    )


def _allocation(titulo, data, colores, sin, vacio: str) -> rx.Component:
    return _card(
        titulo,
        rx.cond(
            sin,
            rx.center(
                rx.text(vacio, size="2", weight="light", color_scheme="gray"),
                height="200px",
            ),
            rx.vstack(
                rx.recharts.pie_chart(
                    rx.recharts.pie(
                        rx.foreach(data, lambda _d, i: rx.recharts.cell(fill=colores[i])),
                        data=data,
                        data_key="valor",
                        name_key="etiqueta",
                        cx="50%",
                        cy="50%",
                        inner_radius=55,
                        outer_radius=90,
                        padding_angle=1,
                    ),
                    rx.recharts.graphing_tooltip(),
                    margin={"top": 0, "right": 0, "bottom": 0, "left": 0},
                    width="100%",
                    height=190,
                ),
                rx.vstack(
                    rx.foreach(data, lambda d, i: _fila_alloc(d, i, colores)),
                    spacing="2",
                    width="100%",
                ),
                spacing="3",
                width="100%",
            ),
        ),
    )


def allocation_view(E) -> rx.Component:
    return _allocation(
        "Distribución por categoría", E.distribucion, CAT_COLORES_VAR,
        E.sin_distribucion, "Aún no resolviste retos.",
    )


def puntos_view(E) -> rx.Component:
    return _allocation(
        "Puntos: conservados vs. pistas", E.reparto, REPARTO_COLORES_VAR,
        E.sin_reparto, "Sin puntos todavía.",
    )


def aciertos_view(E) -> rx.Component:
    return _allocation(
        "Aciertos y errores", E.envios, PIE_COLORES_VAR,
        E.sin_envios, "Sin envíos todavía.",
    )


def evolucion_view(E) -> rx.Component:
    return _card(
        "Evolución de tu puntaje",
        evolucion_chart(option=E.evolucion_opcion, altura="260px", width="100%"),
    )


def _fila_resuelto(f: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(f["titulo"]),
        rx.table.cell(f["categoria"]),
        rx.table.cell(f["dificultad"]),
        rx.table.cell(f["puntaje"]),
    )


def tabla_resueltos(E) -> rx.Component:
    return _card(
        "Retos resueltos",
        rx.cond(
            E.sin_resueltos,
            rx.text("Aún no resolviste ningún reto.", size="2", weight="light", color_scheme="gray"),
            rx.box(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Reto"),
                            rx.table.column_header_cell("Categoría"),
                            rx.table.column_header_cell("Dificultad"),
                            rx.table.column_header_cell("Puntaje"),
                        ),
                    ),
                    rx.table.body(rx.foreach(E.resueltos, _fila_resuelto)),
                    width="100%",
                ),
                width="100%",
                max_height="57vh",
                overflow_y="auto",
            ),
        ),
    )


def perfil_contenido(
    E,
    titulo: str = "Mi perfil",
    vacio: str = "No participás en este evento.",
    mostrar_email: bool = True,
) -> rx.Component:
    # El heading solo tiene sentido cuando hay algo que titular: si no hay datos
    # (no inscrito, o admin sin participación) es puro ruido visual encima del
    # aviso de "no participás".
    return rx.cond(
        E.hay_datos,
        rx.grid(
            rx.heading(titulo, size="5"),
            rx.grid(
                rx.vstack(
                    rx.hstack(
                    card_identidad(E, mostrar_email),
                    width="100%",

                    ),
                    evolucion_view(E),
                    tabla_resueltos(E),
                    spacing="4",
                    width="100%",
                ),
                rx.vstack(
                    allocation_view(E),
                    puntos_view(E),
                    aciertos_view(E),
                    spacing="3",
                    width="100%",
                ),
                columns={"base": "1", "lg": "1fr 22em"},
                spacing="4",
                width="100%",
            ),
            spacing="4",
            justify_items="center",
            width="80%",
            padding="1.5em",
        ),
        rx.center(
            rx.text(vacio, size="4", weight="medium", color_scheme="gray"),
            height="50vh",
            width="100%",
        ),
    )
