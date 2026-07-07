import reflex as rx
from itdb_ctf.states.evento_states import ListarEventoState
from itdb_ctf.views.form_editar_evento_view import form_editar_evento_view


def fila_evento(evento:dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(evento['id']),
        rx.table.cell(evento['titulo']),
        rx.table.cell(evento['modalidad']),
        rx.table.cell(evento['modo_puntaje']),
        rx.table.cell(
            rx.cond(
                evento['auto_inscripacion'],
                rx.badge("True", color_scheme="cyan"),
                rx.badge("False", color_scheme="purple"),
            ),
        ),
        rx.table.cell(
            rx.cond(
                evento['activo'],
                rx.badge("Activo", color_scheme="green"),
                rx.badge("Inactivo", color_scheme="red"),
            ),
        ),
        rx.table.cell(
            rx.hstack(
                form_editar_evento_view(evento),
                rx.button(
                    rx.cond(evento['activo'],"Desactivar","activar"),
                    on_click=lambda: ListarEventoState.arternar_activo(evento['id']),
                    color_scheme=rx.cond(evento['activo'],"red","green"),
                    size="1", variant="soft",
                ),
                spacing="2",
            ),
        
        ),
    )

def tabla_eventos_view() -> rx.Component:
    return rx.vstack(
        rx.vstack(
            rx.heading("Eventos"),
            rx.card(
                rx.hstack(rx.icon("search", size=16 ),rx.text("Buscar",size="1")),
                rx.input(placeholder="Buscar por titulo...", value=ListarEventoState.busqueda, on_change=ListarEventoState.set_busqueda),
            ),
        ),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("ID"),
                    rx.table.column_header_cell("Titulo"),
                    rx.table.column_header_cell("Modalidad"),
                    rx.table.column_header_cell("Modo puntaje"),
                    rx.table.column_header_cell("Auto Insc."),
                    rx.table.column_header_cell("Estado"),
                    rx.table.column_header_cell("Acciones"),
                ),
            ),
        rx.table.body(
            rx.foreach(ListarEventoState.lista, fila_evento),
        ),
        width="100%",
        ),
        spacing="2", width="100%"
    )