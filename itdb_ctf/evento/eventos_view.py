import reflex as rx

from itdb_ctf.evento.evento_states import CreaEventoState, EditarEventoState, ListarEventoState
from itdb_ctf.components.form import input_box, text_area ,select_catalog, input_datetime, checked, badge_msg, button, close_dialog_button

def form_evento() -> rx.Component:
    return rx.vstack(
        rx.heading("Crear evento", size="5"),
        input_box("Titulo","Titulo...",CreaEventoState.titulo,CreaEventoState.set_titulo,"text"),
        text_area("Descripcion","Descripcion... ",CreaEventoState.descripcion,CreaEventoState.set_descripcion),
        rx.grid(
            select_catalog("Modalidad","Seleccionar...",CreaEventoState.modalidades,CreaEventoState.set_id_modalidad),
            select_catalog("Modo puntaje","Seleccionar...",CreaEventoState.modos,CreaEventoState.set_id_modo_puntaje),  
            input_datetime("Fecha de inicio",CreaEventoState.fec_inicio,CreaEventoState.set_fec_inicio,CreaEventoState.modalidad_abierto),
            input_datetime("Fecha de finalización",CreaEventoState.fec_fin,CreaEventoState.set_fec_fin,CreaEventoState.modalidad_abierto),
            checked("Permitir auto incripcion",CreaEventoState.auto_inscripcion,CreaEventoState.set_auto_inscripcion,CreaEventoState.modalidad_abierto),
            columns={"base":"1","md":"2"},
            spacing="4",
            width="100%"
        ),
        rx.grid(
            rx.cond(CreaEventoState.mensaje != "", badge_msg(CreaEventoState.mensaje,"red"), rx.spacer()),
            rx.hstack(
                rx.spacer(),
                button("guardar","green",[CreaEventoState.guardar_evento_completo]),
                button("Cancelar","red",[CreaEventoState.limpiar,CreaEventoState.open_close_dialog]),
                spacing="2",
                width="100%",    
            ),
            spacing="2",
            rows="2",
            width="100%",
        ),
        spacing="5"
    )

def form_crear_evento_view() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(rx.button(rx.icon("plus"),"Crear evento", on_click=CreaEventoState.open_close_dialog)),
        rx.dialog.content(
            form_evento(),
            close_dialog_button(CreaEventoState.open_close_dialog),
            width="100%",
            max_width="600px",
        ),
        open=CreaEventoState.dialog_bool,
        on_open_change=CreaEventoState.set_drop_mensaje
    )

def form_evento_edit() -> rx.Component:
    return rx.vstack(
        rx.heading("Editar Reto", size="5"),
        input_box("Titulo", "", EditarEventoState.titulo, EditarEventoState.set_titulo, "text"),
        text_area("Descripcion", "", EditarEventoState.descripcion, EditarEventoState.set_descripcion),
        rx.grid(
            select_catalog("Modalidad", "", EditarEventoState.modalidades, EditarEventoState.set_id_modalidad, EditarEventoState.id_modalidad),
            select_catalog("Modo Puntaje","", EditarEventoState.modos, EditarEventoState.set_id_modo_puntaje, EditarEventoState.id_modo_puntaje),
            input_datetime("Inicio", EditarEventoState.fec_inicio, EditarEventoState.set_fec_inicio,EditarEventoState.modalidad_abierto),
            input_datetime("Fin", EditarEventoState.fec_fin, EditarEventoState.set_fec_fin, EditarEventoState.modalidad_abierto),
            checked("Auto inscripcion", EditarEventoState.auto_inscripcion, EditarEventoState.set_auto_inscripcion, EditarEventoState.modalidad_abierto),
            columns={"base":"1","md":"2"},
            spacing="4",
            width="100%",
            pointer_events=rx.cond(EditarEventoState.estado == "futuro", "auto", "none"), 
        ),
        rx.grid(
            rx.cond(EditarEventoState.mensaje != "", badge_msg(EditarEventoState.mensaje,"red"), rx.spacer()),
            rx.hstack(
                rx.spacer(),
                button("Guardar","green",[EditarEventoState.guardar_edit_completo]),
                button("Cancelar", "red", [EditarEventoState.open_close_dialog, EditarEventoState.limpiar]),
                spacing="2",
                width="100%"
            ),
            spacing="2",
            rows="2",
            width="100%",
        ),
        spacing="5",
        width="100%",
        pointer_events=rx.cond(EditarEventoState.estado == "concluido", "none", "auto"),       
    )

def button_edit(id_evento) -> rx.Component:
    return rx.button(
        "Editar",
        on_click=EditarEventoState.cargar_evento(id_evento),
        size="1", 
        variant="soft", 
        color_scheme="cyan",
    ),

def form_editar_evento_view() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            form_evento_edit(),
            close_dialog_button(EditarEventoState.open_close_dialog),
            width="100%",
            max_width="600px",
        ),
        open=EditarEventoState.dialog_bool,
    )

def fila_evento(evento:dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(evento['id']),
        rx.table.cell(evento['titulo'], style={"text-overflow":"ellipsis"}),
        rx.table.cell(evento['modalidad']),
        rx.table.cell(evento['modo_puntaje']),
        rx.table.cell(
            rx.cond(
                evento['auto_inscripcion'],
                rx.badge("True", color_scheme="blue"),
                rx.badge("False", color_scheme="gray"),
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
                button_edit(evento['id']),
                rx.cond(
                    evento['estado'] != "abierto",
                    rx.button(
                        rx.cond(evento['activo'],"Desactivar","activar"),
                        on_click=lambda: ListarEventoState.arternar_activo(evento['id']),
                        color_scheme=rx.cond(evento['activo'],"red","green"),
                        size="1", variant="soft",
                    ),
                ),
                spacing="2",
            ),
        
        ),
        style={"text-transform":"capitalize"}
    )

def tabla_eventos_view() -> rx.Component:   
    return rx.table.root(
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

def eventos_view() -> rx.Component:
    return rx.flex(
        rx.card(
            rx.grid(
                rx.flex(
                    rx.hstack(rx.icon("search", size=10 ),rx.text("Buscar",size="1", weight="light", color_scheme="gray")),
                    rx.input(placeholder="Buscar por titulo...", value=ListarEventoState.busqueda, on_change=ListarEventoState.set_busqueda, width="100%"),
                    width="100%",
                    direction="column",
                    spacing="1",
                ),
                form_crear_evento_view(),
                width="100%",
                grid_auto_flow="column",
                place_items="center",
                spacing="5",
            ),
            position="sticky",
            top="1.5em",
            width="100%",
            z_index="99",
        ),
        tabla_eventos_view(),
        form_editar_evento_view(),
        align="center",
        direction="column",
        width="80%",
        spacing="5",
        margin_top="1.5em",
    )