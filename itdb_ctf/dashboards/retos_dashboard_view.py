import reflex as rx

from itdb_ctf.dashboards.retos_dashboard_states import RetosDashboardState as S
from itdb_ctf.components.form import select_catalog
from itdb_ctf.dashboards.dashboard_componentes import (
    kpi,
    panel,
    grafica_desglose,
    grafica_barra,
    grafica_pastel,
    CAT_COLORES_VAR,
)


def _controles() -> rx.Component:
    return rx.hstack(
        rx.hstack(
            rx.switch(
                checked=S.solo_mios,
                on_change=S.set_mis_retos,
                disabled=S.es_autor,
            ),
            rx.text("Mis retos", size="2"),
            align="center",
            spacing="2",
            style={"display":rx.cond(S.es_autor,"none",None)}
        ),
        rx.box(
            select_catalog(
                "Evento",
                "Todos los eventos",
                S.eventos_opciones,
                S.set_evento,
                S.id_evento_sel,
            ),
            width="20em",
        ),
        align="end",
        spacing="4",
    )


def fila_kpis() -> rx.Component:
    r = S.resumen
    return rx.grid(
        kpi("Retos", r["total"], f"{r['activos']} activos · {r['inactivos']} inactivos"),
        kpi("Nunca resueltos", r["nunca_resueltos"], "0 resoluciones correctas"),
        kpi("Acierto", f"{r['tasa_acierto']}%", f"{r['resoluciones']} resoluciones"),
        kpi("Pistas", r["retos_con_pistas"], "retos con pista"),
        kpi("Con archivo", r["con_archivo"], f"{r['sin_archivo']} sin archivo"),
        rx.cond(
            S.es_global,
            kpi("Aislados", r["aislados"], "sin ningún evento"),
        ),
        columns={"base": "3", "sm": "6", "lg": "6"},
        spacing="3",
        width="100%",
    )


def _fila_evento(f: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(f["titulo"]),
        rx.table.cell(f["retos"]),
        rx.table.cell(f["resoluciones"]),
    )


def tabla_eventos() -> rx.Component:
    return panel(
        "Retos y resoluciones por evento",
        rx.cond(
            S.sin_eventos,
            rx.text("No hay eventos.", size="2", weight="light", color_scheme="gray"),
            rx.box(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Evento"),
                            rx.table.column_header_cell("Retos"),
                            rx.table.column_header_cell("Resoluciones"),
                        ),
                    ),
                    rx.table.body(rx.foreach(S.eventos, _fila_evento)),
                    width="100%",
                ),
                width="100%",
                height="45vh",
                overflow_y="auto",
            ),
        ),
    )


def _fila_autor(f: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(f["autor"]),
        rx.table.cell(f["retos"]),
    )


def tabla_autores() -> rx.Component:
    return panel(
        "Retos por autor",
        rx.box(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Autor"),
                        rx.table.column_header_cell("Retos"),
                    ),
                ),
                rx.table.body(rx.foreach(S.autores, _fila_autor)),
                width="100%",
            ),
            width="100%",
            height="35vh",
            overflow_y="auto",
        ),
    )


def retos_dashboard_view() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.heading("Dashboard — Retos", size="6"),
            rx.spacer(),
            _controles(),
            width="100%",
            align="center",
        ),
        fila_kpis(),
        rx.grid(
            grafica_desglose("Retos y resoluciones por categoría", S.categoria),
            grafica_desglose("Retos y resoluciones por dificultad", S.dificultad),
            grafica_pastel("Retos por modo de puntaje", S.modo, CAT_COLORES_VAR),
            grafica_barra("Retos creados por mes", S.creados_mes, nombre="Retos"),
            columns={"base": "1", "lg": "2"},
            spacing="3",
            width="100%",
        ),
        rx.grid(
            tabla_eventos(),
            rx.cond(S.mostrar_autores, tabla_autores(), rx.fragment()),
            columns={"base": "1", "lg": "70% 1fr"},
            spacing="3",
            width="100%",
        ),
        spacing="4",
        width=rx.breakpoints(sm="95%", md="90%"),
        padding="1.5em",
    )
