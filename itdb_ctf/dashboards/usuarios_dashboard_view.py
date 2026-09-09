import reflex as rx

from itdb_ctf.dashboards.usuarios_dashboard_states import UsuariosDashboardState as S
from itdb_ctf.components.form import select_catalog
from itdb_ctf.dashboards.dashboard_componentes import (
    kpi,
    panel,
    grafica_barra,
    grafica_pastel,
    CAT_COLORES_VAR,
)


def _selector() -> rx.Component:
    return rx.box(
        select_catalog(
            "Evento",
            "Todos los eventos",
            S.eventos_opciones,
            S.set_evento,
            S.id_evento_sel,
        ),
        width="20em",
    )


def fila_kpis() -> rx.Component:
    r = S.resumen
    return rx.grid(
        kpi("Usuarios", r["total"], f"{r['activos']} activos · {r['inactivos']} inactivos"),
        kpi("Google", r["google"], "cuentas institucionales"),
        kpi("Local", r["local"], "cuentas locales"),
        kpi("Placeholders", r["placeholders"], "pendientes de primer login"),
        kpi("Participantes", r["participantes"], "con al menos un evento"),
        kpi("Descalificados", r["descalificados"], "en eventos cerrados"),
        columns={"base": "2", "sm": "4", "lg": "6"},
        spacing="3",
        width="100%",
    )


def _tabla(titulo: str, columnas: list[str], filas, fila_fn, vacio_cond, vacio: str) -> rx.Component:
    return panel(
        titulo,
        rx.cond(
            vacio_cond,
            rx.text(vacio, size="2", weight="light", color_scheme="gray"),
            rx.box(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            *[rx.table.column_header_cell(c) for c in columnas]
                        ),
                    ),
                    rx.table.body(rx.foreach(filas, fila_fn)),
                    width="100%",
                ),
                width="100%",
                height="35vh",
                overflow_y="auto",
            ),
        ),
    )


def tabla_solvers() -> rx.Component:
    return _tabla(
        "Top solvers (retos resueltos)",
        ["Usuario", "Resueltos"],
        S.solvers,
        lambda f: rx.table.row(rx.table.cell(f["alias"]), rx.table.cell(f["resoluciones"])),
        S.sin_solvers,
        "Aún no hay resoluciones.",
    )


def tabla_autores() -> rx.Component:
    return _tabla(
        "Autores por nº de retos",
        ["Autor", "Retos"],
        S.autores,
        lambda f: rx.table.row(rx.table.cell(f["autor"]), rx.table.cell(f["retos"])),
        S.sin_autores,
        "Sin retos.",
    )


def tabla_descalificados() -> rx.Component:
    return _tabla(
        "Descalificados",
        ["Usuario", "Correo", "Evento"],
        S.descalificados,
        lambda f: rx.table.row(
            rx.table.cell(f["alias"]),
            rx.table.cell(f["email"],style={"text-overflow":"ellipsis"}),
            rx.table.cell(f["evento"]),
        ),
        S.sin_descalificados,
        "Sin descalificados.",
    )


def usuarios_dashboard_view() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.heading("Dashboard — Usuarios", size="6"),
            rx.spacer(),
            _selector(),
            width="100%",
            align="center",
        ),
        fila_kpis(),
        rx.grid(
            grafica_pastel("Usuarios por rol", S.roles, CAT_COLORES_VAR),
            grafica_pastel("Usuarios por método de acceso", S.metodos, CAT_COLORES_VAR),
            tabla_autores(),
            columns={"base": "1", "lg": "3"},
            spacing="3",
            width="100%",
        ),
        rx.grid(
            grafica_barra("Registros por mes", S.registros_mes, nombre="Registros"),
            tabla_solvers(),
            tabla_descalificados(),
            columns={"base": "1", "lg": "50% 1fr 1fr"},
            spacing="3",
            width="100%",
        ),
        spacing="4",
        width="100%",
        padding="1.5em",
    )
