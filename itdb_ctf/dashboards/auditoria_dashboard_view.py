import reflex as rx

from itdb_ctf.components.form import select_catalog
from itdb_ctf.dashboards.auditoria_dashboard_states import AuditoriaDashboardState as S
from itdb_ctf.dashboards.dashboard_componentes import (
    NARANJA,
    STAFF_COLORES,
    kpi_barras,
    kpi_spark,
)


def _badge_op(op) -> rx.Component:
    return rx.match(
        op,
        ("INSERT", rx.badge("INSERT", color_scheme="jade", variant="surface")),
        ("UPDATE", rx.badge("UPDATE", color_scheme="amber", variant="surface")),
        ("DELETE", rx.badge("DELETE", color_scheme="ruby", variant="surface")),
        rx.badge(op, color_scheme="gray", variant="surface"),
    )


def barra_salud() -> rx.Component:
    return rx.card(
        rx.hstack(
            rx.cond(
                S.redis_ok,
                rx.badge("Redis en línea", color_scheme="jade", variant="surface"),
                rx.badge("Redis sin conexión", color_scheme="ruby", variant="surface"),
            ),
            rx.cond(
                S.salud["hay_abierto"],
                rx.badge(S.salud["evento_abierto"], color_scheme="cyan", variant="surface"),
                rx.badge("Sin evento abierto", color_scheme="gray", variant="surface"),
            ),
            rx.cond(
                S.hay_congelados,
                rx.badge(
                    f"{S.salud['congelados']} scoreboard(s) congelado(s)",
                    color_scheme="amber",
                    variant="surface",
                ),
                rx.fragment(),
            ),
            rx.text(S.texto_eventos, size="1", weight="light", color_scheme="gray"),
            rx.spacer(),
            rx.text(
                f"Última escritura auditada: {S.resumen['ultimo_texto']}",
                size="1",
                weight="light",
                color_scheme="gray",
            ),
            width="100%",
            align="center",
            spacing="3",
            wrap="wrap",
        ),
        width="100%",
    )


def fila_kpis() -> rx.Component:
    r = S.resumen
    return rx.grid(
        # la auditoría sí es una serie temporal: ahí la línea es el dato
        kpi_spark(
            "Auditoría",
            r["total"],
            f"{r['inserts']} INSERT · {r['updates']} UPDATE · {r['deletes']} DELETE",
            S.serie_cambios,
            rotulo="cambios/día · 30 d",
            color=NARANJA,
        ),
        # el resto son repartos: la barra muestra lo mismo que el número
        kpi_barras("Usuarios", S.padron["total"], "", S.reparto_usuarios, con_valor=True),
        kpi_barras("Retos", S.retos["total"], "", S.reparto_retos, con_valor=True),
        kpi_barras(
            "Staff", S.staff_total, "", S.reparto_staff, STAFF_COLORES, con_valor=True
        ),
        columns={"base": "1", "sm": "2", "lg": "4"},
        spacing="3",
        width="100%",
    )


def _filtros() -> rx.Component:
    return rx.grid(
        select_catalog("Tabla", "Todas", S.tablas_opciones, S.set_tabla, S.tabla_sel),
        select_catalog(
            "Operación", "Todas", S.operaciones_opciones, S.set_operacion, S.operacion_sel
        ),
        select_catalog("Actor", "Todos", S.actores_opciones, S.set_actor, S.actor_sel),
        select_catalog(
            "Periodo", "7 días", S.periodos_opciones, S.set_periodo, S.periodo_sel
        ),
        columns={"base": "1", "sm": "2", "lg": "4"},
        spacing="3",
        width="100%",
    )


def _celda_cambios(f: dict) -> rx.Component:
    """UPDATE -> campos en gris. INSERT/DELETE -> la propia operación, en color."""
    return rx.match(
        f["operacion"],
        ("INSERT", rx.text("insert", size="1", color_scheme="jade")),
        ("DELETE", rx.text("delete", size="1", color_scheme="ruby")),
        rx.text(f["cambios"], size="1", color_scheme="gray"),
    )


def _fila(f: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(rx.text(f["fecha"], size="1"), white_space="nowrap"),
        rx.table.cell(_badge_op(f["operacion"])),
        rx.table.cell(rx.text(f["tabla"], size="1")),
        rx.table.cell(
            rx.cond(
                f["es_sistema"],
                rx.text(
                    f["actor"], size="1", color_scheme="gray",
                    style={"font_style": "italic"},
                ),
                rx.text(f["actor"], size="1"),
            ),
        ),
        rx.table.cell(rx.text(f["descripcion"], size="1")),
        rx.table.cell(_celda_cambios(f)),
        rx.table.cell(
            rx.button(
                "ver",
                size="1",
                variant="solid",
                color_scheme="gray",
                on_click=lambda: S.ver_detalle(f["id"]),
            ),
        ),
    )


def tabla_bitacora() -> rx.Component:
    return rx.cond(
        S.hay_filas,
        rx.box(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Cuándo"),
                        rx.table.column_header_cell("Operación"),
                        rx.table.column_header_cell("Tabla"),
                        rx.table.column_header_cell("Actor"),
                        rx.table.column_header_cell("Registro"),
                        rx.table.column_header_cell("Cambios"),
                        rx.table.column_header_cell(""),
                    ),
                ),
                rx.table.body(rx.foreach(S.filas, _fila)),
                width="100%",
            ),
            width="100%",
            height="55vh",
            overflow_y="auto",
            overflow_x="auto",
        ),
        rx.center(
            rx.text(
                "Sin registros para estos filtros.",
                size="2",
                weight="light",
                color_scheme="gray",
            ),
            height="20vh",
            width="100%",
        ),
    )


def _fila_detalle(c: dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(rx.text(c["campo"], size="1", weight="medium")),
        rx.table.cell(rx.text(c["antes"], size="1", color_scheme="gray")),
        rx.table.cell(rx.text(c["despues"], size="1")),
    )


def dialog_detalle() -> rx.Component:
    d = S.detalle
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    _badge_op(d["operacion"]),
                    rx.heading(d["descripcion"], size="3"),
                    rx.text(d["tabla"], size="1", color_scheme="gray"),
                    width="100%",
                    align="center",
                    spacing="2",
                ),
                rx.text(
                    f"{d['actor']} · {d['fecha']}",
                    size="1",
                    weight="light",
                    color_scheme="gray",
                ),
                rx.divider(),
                rx.cond(
                    S.hay_detalle,
                    rx.box(
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("Campo"),
                                    rx.table.column_header_cell("Antes"),
                                    rx.table.column_header_cell("Después"),
                                ),
                            ),
                            rx.table.body(rx.foreach(S.detalle_cambios, _fila_detalle)),
                            width="100%",
                        ),
                        width="100%",
                        max_height="50vh",
                        overflow_y="auto",
                    ),
                    rx.text(
                        "Sin campos que mostrar.",
                        size="2",
                        weight="light",
                        color_scheme="gray",
                    ),
                ),
                rx.hstack(
                    rx.spacer(),
                    rx.button(
                        "Cerrar",
                        on_click=S.cerrar_detalle,
                        variant="solid",
                        color_scheme="gray",
                        size="2",
                    ),
                    width="100%",
                ),
                width="100%",
                spacing="3",
            ),
            width="100%",
            max_width="640px",
        ),
        open=S.detalle_abierto,
    )


def auditoria_dashboard_view() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.vstack(
                rx.heading("Dashboard — Auditoría y plataforma", size="6"),
                rx.text(
                    "Registra cambios en catálogos, usuarios, eventos, retos, pistas e "
                    "inscripciones. No registra envíos de flag ni compras de pistas.",
                    size="1",
                    weight="light",
                    color_scheme="gray",
                ),
                spacing="1",
                align="start",
            ),
            rx.spacer(),
            rx.text(S.texto_conteo, size="1", weight="light", color_scheme="gray"),
            width="100%",
            align="center",
        ),
        barra_salud(),
        fila_kpis(),
        _filtros(),
        tabla_bitacora(),
        rx.cond(
            S.hay_mas,
            rx.center(
                rx.button("Ver 100 más", on_click=S.ver_mas, variant="solid", size="2"),
                width="100%",
            ),
            rx.fragment(),
        ),
        dialog_detalle(),
        spacing="4",
        width=rx.breakpoints(sm="95%", md="90%"),
        padding="1.5em",
    )
