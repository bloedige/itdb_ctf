import reflex as rx

from itdb_ctf.dashboards.evento_abierto_dashboard_states import EventoAbiertoDashboardState
from itdb_ctf.dashboards.dashboard_componentes import (
    AZUL,
    VERDE,
    NARANJA,
    kpi,
    panel,
    grafica_evolucion as _grafica_evolucion,
    grafica_desglose,
    panel_ranking,
)

def fila_kpis() -> rx.Component:
    r = EventoAbiertoDashboardState.resumen
    return rx.grid(
        kpi(
            "Participantes",
            r["participantes_total"],
            f"{r['participantes_inscritos']} inscritos · {r['participantes_descalificados']} descalificados",
        ),
        kpi("Nuevos este mes", r["nuevos_mes"], "inscripciones del mes en curso"),
        kpi(
            "Participación real",
            f"{r['pct_participacion']}%",
            f"{r['participantes_activos']} con al menos un envío",
        ),
        kpi(
            "Retos en el evento",
            r["retos_total"],
            f"{r['retos_activos']} activos · {r['retos_inactivos']} inactivos",
        ),
        kpi(
            "Tasa de acierto",
            f"{r['tasa_acierto']}%",
            f"{r['envios_correctos']} correctos de {r['envios_total']} envíos",
        ),
        kpi(
            "Puntaje en juego",
            r["puntaje_en_juego"],
            f"{r['resoluciones_total']} resoluciones totales",
        ),
        kpi(
            "Pistas",
            r["pistas_disponibles"],
            f"{r['pistas_compradas']} compradas · {r['puntos_gastados_pistas']} pts gastados",
        ),
        columns={"base": "1", "sm": "2", "lg": "7"},
        spacing="3",
        width="100%",
    )


def grafica_evolucion() -> rx.Component:
    return _grafica_evolucion(EventoAbiertoDashboardState.evol_opcion)

def grafica_actividad() -> rx.Component:
    return panel(
        "Actividad diaria · últimos 30 días",
        rx.recharts.line_chart(
            rx.recharts.line(
                data_key="envios", name="Envíos", type_="monotone",
                stroke=NARANJA, dot=False,
            ),
            rx.recharts.line(
                data_key="resoluciones", name="Resoluciones", type_="monotone",
                stroke=VERDE, dot=False,
            ),
            rx.recharts.x_axis(data_key="fecha"),
            rx.recharts.y_axis(),
            rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
            rx.recharts.graphing_tooltip(),
            rx.recharts.legend(),
            data=EventoAbiertoDashboardState.actividad,
            width="100%",
            height=280,
        ),
    )

def grafica_inscripciones() -> rx.Component:
    return panel(
        "Inscripciones por mes · últimos 12 meses",
        rx.recharts.bar_chart(
            rx.recharts.bar(data_key="cantidad", name="Inscripciones", fill=AZUL),
            rx.recharts.x_axis(data_key="mes"),
            rx.recharts.y_axis(),
            rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
            rx.recharts.graphing_tooltip(),
            data=EventoAbiertoDashboardState.inscripciones_mes,
            width="100%",
            height=280,
        ),
    )



def tabla_ranking() -> rx.Component:
    return panel_ranking(
        EventoAbiertoDashboardState.hay_ranking,
        EventoAbiertoDashboardState.ranking,
    )

def fila_reto(fila: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(fila["titulo"]),
        rx.table.cell(fila["categoria"]),
        rx.table.cell(fila["dificultad"]),
        rx.table.cell(fila["puntaje"]),
        rx.table.cell(
            rx.cond(
                fila["sin_resolver"],
                rx.badge("Sin resolver", color_scheme="gray"),
                rx.text(fila["resoluciones"]),
            ),
        ),
        style={"opacity": rx.cond(fila["sin_resolver"], "0.55", "1")},
    )

def _tabla_retos(titulo: str, filas) -> rx.Component:
    return panel(
        titulo,
        rx.box(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Reto"),
                        rx.table.column_header_cell("Categoría"),
                        rx.table.column_header_cell("Dificultad"),
                        rx.table.column_header_cell("Puntaje"),
                        rx.table.column_header_cell("Resueltos"),
                    ),
                ),
                rx.table.body(rx.foreach(filas, fila_reto)),
                width="100%",
                height="35vh",
                overflow_y="auto",
            ),
            width="100%",
            overflow_x="auto",
        ),
    )

def tabla_retos_mas_resueltos() -> rx.Component:
    return _tabla_retos(
        "Retos más resueltos · top 10",
        EventoAbiertoDashboardState.retos_mas_resueltos,
    )

def tabla_retos_mas_dificiles() -> rx.Component:
    return _tabla_retos(
        "Retos más difíciles · top 10",
        EventoAbiertoDashboardState.retos_mas_dificiles,
    )

def evento_abierto_dashboard_view() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.heading("Dashboard — Evento Abierto", size="6"),
            rx.spacer(),
            width="100%",
            align="center",
        ),
        rx.cond(
            EventoAbiertoDashboardState.hay_evento,
            rx.vstack(
                fila_kpis(),
                rx.grid(
                    grafica_evolucion(),
                    tabla_ranking(),
                    columns={"base": "1", "lg": "60% 1fr"},
                    spacing="3",
                    width="100%",
                ),
                rx.grid(
                    grafica_actividad(),
                    grafica_inscripciones(),
                    grafica_desglose("Retos y resoluciones por categoría", EventoAbiertoDashboardState.categoria),
                    grafica_desglose("Retos y resoluciones por dificultad", EventoAbiertoDashboardState.dificultad),
                    columns={"base": "1", "lg": "2"},
                    spacing="3",
                    width="100%",
                ),
                rx.grid(
                    tabla_retos_mas_resueltos(),
                    tabla_retos_mas_dificiles(),
                    columns={"base": "1", "lg": "2"},
                    spacing="3",
                    width="100%",
                ),
                spacing="4",
                width="100%",
            ),
            rx.center(
                rx.text(
                    "No hay un evento abierto configurado.",
                    size="4", weight="light", color_scheme="gray",
                ),
                height="50vh",
                width="100%",
            ),
        ),
        spacing="4",
        width=rx.breakpoints(sm="95%", md="80%"),
        padding="1.5em",
    )
