import reflex as rx

from itdb_ctf.dashboards.eventos_cerrados_dashboard_states import EventosCerradosDashboardState as S
from itdb_ctf.components.form import select_catalog
from itdb_ctf.components.pdf_viewer import documento, pagina
from itdb_ctf.dashboards.dashboard_componentes import (
    NARANJA,
    VERDE,
    kpi,
    panel,
    grafica_evolucion as _grafica_evolucion,
    grafica_desglose,
    panel_ranking,
)


# ------------------------------------------------------------------ barra estado


def _badge_estado() -> rx.Component:
    return rx.match(
        S.info["estado"],
        ("activo", rx.badge("Activo", color_scheme="green", size="2")),
        ("futuro", rx.badge("Futuro", color_scheme="blue", size="2")),
        ("concluido", rx.badge("Concluido", color_scheme="gray", size="2")),
        rx.badge(S.info["estado"], color_scheme="gray", size="2"),
    )


def barra_estado() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.hstack(
                _badge_estado(),
                rx.cond(
                    S.esta_congelado,
                    rx.badge("Congelado (vista estudiante)", color_scheme="cyan", size="2"),
                ),
                rx.text(
                    f"{S.info['fec_inicio']}  →  {S.info['fec_fin']}",
                    size="1", color_scheme="gray",
                ),
                rx.spacer(),
                rx.text(S.info["tiempo_texto"], size="2", weight="medium"),
                rx.cond(
                    S.hay_seleccion,
                    rx.link(
                        rx.button(
                            rx.icon("eye", size=15),
                            "Ver como jugador",
                            variant="soft",
                            color_scheme="gray",
                            size="1",
                        ),
                        href=f"/evento/{S.id_sel}/scoreboard",
                        is_external=True,
                    ),
                ),
                rx.cond(
                    S.hay_seleccion,
                    rx.button(
                        rx.icon("file-text", size=15),
                        "Reporte PDF",
                        on_click=S.abrir_reporte,
                        variant="soft",
                        color_scheme="gray",
                        size="1",
                    ),
                ),
                rx.cond(
                    S.evento_activo,
                    rx.button(
                        rx.icon("snowflake", size=15),
                        rx.cond(S.esta_congelado, "Descongelar", "Congelar scoreboard"),
                        on_click=S.congelar,
                        variant="soft",
                        color_scheme="cyan",
                        size="1",
                    ),
                ),
                width="100%",
                align="center",
                spacing="3",
            ),
            rx.cond(
                S.evento_activo,
                rx.progress(value=S.info["pct_transcurrido"], width="100%", color_scheme="green"),
            ),
            spacing="2",
            width="100%",
        ),
        width="100%",
    )


# -------------------------------------------------------------------------- KPIs


def fila_kpis() -> rx.Component:
    r = S.resumen
    return rx.grid(
        kpi(
            "Participantes",
            r["participantes_total"],
            f"{r['participantes_inscritos']} inscritos · {r['participantes_descalificados']} descalificados",
        ),
        kpi(
            "Participación real",
            f"{r['pct_participacion']}%",
            f"{r['participantes_activos']} con al menos un envío",
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
        columns={"base": "1", "sm": "2", "lg": "5"},
        spacing="3",
        width="100%",
    )


# ------------------------------------------------------------------------ charts


def grafica_actividad() -> rx.Component:
    return panel(
        "Actividad durante el evento",
        rx.recharts.line_chart(
            rx.recharts.line(
                data_key="envios", name="Envíos", type_="monotone",
                stroke=NARANJA, dot=False,
            ),
            rx.recharts.line(
                data_key="resoluciones", name="Resoluciones", type_="monotone",
                stroke=VERDE, dot=False,
            ),
            rx.recharts.x_axis(data_key="t"),
            rx.recharts.y_axis(),
            rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
            rx.recharts.graphing_tooltip(),
            rx.recharts.legend(),
            data=S.actividad,
            width="100%",
            height=280,
        ),
    )


# -------------------------------------------------------------------------- feed


def _fila_feed(f: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(f["participante"]),
        rx.table.cell(f["reto"]),
        rx.table.cell(f["hora"]),
    )


def feed_view() -> rx.Component:
    return panel(
        "Últimas resoluciones",
        rx.cond(
            S.hay_feed,
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Participante"),
                        rx.table.column_header_cell("Reto"),
                        rx.table.column_header_cell("Hora"),
                    ),
                ),
                rx.table.body(rx.foreach(S.feed, _fila_feed)),
                width="100%",
                height="35vh",
                overflow_y="auto",                
            ),
            rx.text("Sin resoluciones todavía.", size="2", weight="light", color_scheme="gray"),
        ),
    )


# ---------------------------------------------------------------- preview del PDF


def _navegador_paginas() -> rx.Component:
    """react-pdf pinta una página a la vez, así que la navegación va aparte."""
    return rx.hstack(
        rx.button(
            rx.icon("chevron-left", size=16),
            on_click=S.pagina_anterior,
            disabled=S.reporte_pagina <= 1,
            variant="soft", color_scheme="gray", size="2",
        ),
        rx.text(S.texto_paginas, size="2", weight="medium"),
        rx.button(
            rx.icon("chevron-right", size=16),
            on_click=S.pagina_siguiente,
            disabled=S.reporte_pagina >= S.reporte_paginas,
            variant="soft", color_scheme="gray", size="2",
        ),
        align="center",
        spacing="3",
    )


def dialog_reporte() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    _navegador_paginas(),
                    rx.spacer(),
                    rx.button(
                        rx.icon("x", size=16),
                        on_click=S.cerrar_reporte,
                        variant="soft", color_scheme="gray", size="2",
                    ),
                    width="100%",
                    align="center",
                    spacing="3",
                ),
                rx.box(
                    # sin el `cond` el visor se monta siempre y pdf.js intentaría
                    # renderizar en cada carga de la página
                    rx.cond(
                        S.reporte_abierto,
                        rx.center(
                            documento(
                                pagina(page_number=S.reporte_pagina, width=740),
                                file=S.reporte_uri,
                                on_load_success=S.reporte_cargado,
                            ),
                            width="100%",
                            padding="1em",
                        ),
                    ),
                    rx.box(
                        rx.button(
                            rx.icon("download", size=18),
                            "Descargar",
                            on_click=S.descargar_reporte,
                            color_scheme="amber",
                            size="3",
                            box_shadow="0 6px 20px rgba(0,0,0,.28)",
                            pointer_events="auto",
                        ),
                        # sticky dentro del área con scroll: acompaña al documento
                        # mientras se baja. El margen negativo evita que sume alto,
                        # y `pointer_events` deja pasar el scroll al PDF de abajo.
                        position="sticky",
                        bottom="1.2em",
                        margin_top="-3.6em",
                        width="100%",
                        display="flex",
                        justify_content="flex-end",
                        padding_right="1.2em",
                        pointer_events="none",
                        z_index="10",
                    ),
                    width="100%",
                    height="72vh",
                    overflow="auto",
                    background="var(--gray-3)",
                    border_radius="var(--radius-3)",
                ),
                width="100%",
                spacing="3",
            ),
            width="95vw",
            max_width="60em",
        ),
        open=S.reporte_abierto,
    )


# -------------------------------------------------------------------------- view


def eventos_cerrados_dashboard_view() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.heading("Dashboard — Eventos Cerrados", size="6"),
            rx.spacer(),
            rx.box(
                select_catalog(
                    "Evento",
                    "Seleccionar evento...",
                    S.eventos,
                    S.set_evento,
                    S.id_sel,
                ),
                width="20em",
            ),
            width="100%",
            align="end",
            spacing="3",
        ),
        rx.cond(
            S.hay_eventos,
            rx.cond(
                S.hay_seleccion,
                rx.vstack(
                    barra_estado(),
                    fila_kpis(),
                    rx.grid(
                        _grafica_evolucion(S.evol_opcion),
                        panel_ranking(S.hay_ranking, S.ranking),
                        columns={"base": "1", "md": "60% 1fr"},
                        spacing="3",
                        width="100%",
                    ),
                    rx.grid(
                        grafica_actividad(),
                        feed_view(),
                        columns={"base": "1", "lg": "60% 1fr"},
                        spacing="3",
                        width="100%",
                    ),
                    rx.grid(
                        grafica_desglose("Retos y resoluciones por categoría", S.categoria),
                        grafica_desglose("Retos y resoluciones por dificultad", S.dificultad),
                        columns={"base": "1", "lg": "2"},
                        spacing="3",
                        width="100%",
                    ),
                    dialog_reporte(),
                    spacing="4",
                    width="100%",
                ),
                rx.center(
                    rx.text("Elige un evento.", size="4", weight="light", color_scheme="gray"),
                    height="40vh", width="100%",
                ),
            ),
            rx.center(
                rx.text(
                    "No hay eventos cerrados creados.",
                    size="4", weight="light", color_scheme="gray",
                ),
                height="50vh", width="100%",
            ),
        ),
        spacing="4",
        width=rx.breakpoints(sm="95%", md="90%"),
        padding="1.5em",
    )
