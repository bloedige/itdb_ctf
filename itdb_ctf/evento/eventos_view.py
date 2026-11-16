import reflex as rx
from itdb_ctf.evento.evento_states import CreaEventoState, EditarEventoState, ListarEventoState
from itdb_ctf.components.form import input_box, text_area ,select_catalog, input_datetime, checked, badge_msg, button, close_dialog_button

def form_evento() -> rx.Component:
    return rx.grid(
        rx.heading("Crear evento", size="5"),
        rx.grid(
            # izquierda: título y descripción; la descripción llena el alto y hace scroll dentro del campo
            rx.flex(
                input_box("Título","Título...",CreaEventoState.titulo,CreaEventoState.set_titulo,"text"),
                rx.flex(
                    rx.text("Descripción", size="1", weight="light"),
                    rx.text_area(
                        placeholder="Descripción...",
                        value=CreaEventoState.descripcion,
                        on_change=CreaEventoState.set_descripcion,
                        width="100%",
                        flex=rx.breakpoints(initial="none", sm="1"),
                        height=rx.breakpoints(initial="21vh", sm="auto"),
                        min_height="120px",
                        resize="none",
                    ),
                    direction="column",
                    flex=rx.breakpoints(initial="none", sm="1"),
                    height=rx.breakpoints(initial="auto", sm="100%"),
                    min_height=rx.breakpoints(initial="auto", sm="0"),
                    width="100%",
                ),
                direction="column",
                spacing="2",
                height=rx.breakpoints(initial="auto", sm="100%"),
                min_height=rx.breakpoints(initial="auto", sm="0"),
                width="100%",
            ),
            # derecha: datos del evento
            rx.grid(
                select_catalog("Modalidad","Seleccionar...",CreaEventoState.modalidades,CreaEventoState.set_id_modalidad),
                select_catalog("Modo puntaje","Seleccionar...",CreaEventoState.modos,CreaEventoState.set_id_modo_puntaje),
                input_datetime("Fecha de inicio",CreaEventoState.fec_inicio,CreaEventoState.set_fec_inicio,CreaEventoState.modalidad_abierto),
                input_datetime("Fecha de finalización",CreaEventoState.fec_fin,CreaEventoState.set_fec_fin,CreaEventoState.modalidad_abierto),
                checked("Permitir autoinscripción",CreaEventoState.auto_inscripcion,CreaEventoState.set_auto_inscripcion,CreaEventoState.modalidad_abierto),
                spacing="3",
                align_content="start",
                width="100%"
            ),
            # celular: una columna · tablet y escritorio: 70% / 30%
            grid_template_columns=rx.breakpoints(initial="minmax(0, 1fr)", sm="minmax(0, 7fr) minmax(0, 3fr)"),
            width="100%",
            spacing="4",
            min_height="0",
            overflow_y=rx.breakpoints(initial="auto", sm="hidden"),
        ),
        # pie: mensaje y botones, siempre visibles
        rx.grid(
            rx.cond(CreaEventoState.mensaje != "", badge_msg(CreaEventoState.mensaje,"red"), rx.spacer()),
            rx.hstack(
                rx.spacer(),
                button("Guardar","green",[CreaEventoState.guardar_evento_completo]),
                button("Cancelar","red",[CreaEventoState.limpiar,CreaEventoState.open_close_dialog]),
                spacing="2",
                width="100%",
            ),
            rows="2",
            width="100%",
        ),
        grid_template_rows="auto minmax(0, 1fr) auto",
        spacing="4",
        height="100%",
    )

def form_crear_evento_view() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(rx.button(rx.icon("plus"),"Crear evento", on_click=CreaEventoState.open_close_dialog, variant="solid", color_scheme="jade")),
        rx.dialog.content(
            form_evento(),
            close_dialog_button(CreaEventoState.open_close_dialog),
            width=rx.breakpoints(initial="90vw", sm="40vw"),
            max_width=rx.breakpoints(initial="90vw", sm="40vw"),
            height="60vh",
            max_height="60vh",
        ),
        open=CreaEventoState.dialog_bool,
        on_open_change=CreaEventoState.set_drop_mensaje
    )

def form_evento_edit() -> rx.Component:
    return rx.grid(
        rx.heading("Editar evento", size="5"),
        rx.grid(
            # izquierda: título y descripción; la descripción llena el alto y hace scroll dentro del campo
            rx.flex(
                input_box("Título", "", EditarEventoState.titulo, EditarEventoState.set_titulo, "text"),
                rx.flex(
                    rx.text("Descripción", size="1", weight="light"),
                    rx.text_area(
                        placeholder="",
                        value=EditarEventoState.descripcion,
                        on_change=EditarEventoState.set_descripcion,
                        width="100%",
                        flex=rx.breakpoints(initial="none", sm="1"),
                        height=rx.breakpoints(initial="21vh", sm="auto"),
                        min_height="120px",
                        resize="none",
                    ),
                    direction="column",
                    flex=rx.breakpoints(initial="none", sm="1"),
                    height=rx.breakpoints(initial="auto", sm="100%"),
                    min_height=rx.breakpoints(initial="auto", sm="0"),
                    width="100%",
                ),
                direction="column",
                spacing="2",
                height=rx.breakpoints(initial="auto", sm="100%"),
                min_height=rx.breakpoints(initial="auto", sm="0"),
                width="100%",
            ),
            # derecha: datos del evento
            rx.grid(
                select_catalog("Modalidad", "", EditarEventoState.modalidades, EditarEventoState.set_id_modalidad, EditarEventoState.id_modalidad),
                select_catalog("Modo puntaje","", EditarEventoState.modos, EditarEventoState.set_id_modo_puntaje, EditarEventoState.id_modo_puntaje),
                input_datetime("Inicio", EditarEventoState.fec_inicio, EditarEventoState.set_fec_inicio,EditarEventoState.modalidad_abierto),
                input_datetime("Fin", EditarEventoState.fec_fin, EditarEventoState.set_fec_fin, EditarEventoState.modalidad_abierto),
                checked("Autoinscripción", EditarEventoState.auto_inscripcion, EditarEventoState.set_auto_inscripcion, EditarEventoState.modalidad_abierto),
                spacing="3",
                align_content="start",
                width="100%",
            ),
            # celular: una columna · tablet y escritorio: 70% / 30%
            grid_template_columns=rx.breakpoints(initial="minmax(0, 1fr)", sm="minmax(0, 7fr) minmax(0, 3fr)"),
            width="100%",
            spacing="4",
            min_height="0",
            overflow_y=rx.breakpoints(initial="auto", sm="hidden"),
        ),
        # pie: mensaje y botones, siempre visibles
        rx.grid(
            rx.cond(EditarEventoState.mensaje != "", badge_msg(EditarEventoState.mensaje,"red"), rx.spacer()),
            rx.hstack(
                rx.spacer(),
                button("Guardar","green",[EditarEventoState.guardar_edit_completo]),
                button("Cancelar", "red", [EditarEventoState.open_close_dialog, EditarEventoState.limpiar]),
                spacing="2",
                width="100%"
            ),
            rows="2",
            width="100%",
        ),
        grid_template_rows="auto minmax(0, 1fr) auto",
        spacing="4",
        height="100%",
    )

def button_edit(id_evento) -> rx.Component:
    return rx.button(
        "Editar",
        on_click=EditarEventoState.cargar_evento(id_evento),
        size="1", 
        variant="solid", 
        color_scheme="blue",
    ),

def form_editar_evento_view() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            form_evento_edit(),
            close_dialog_button(EditarEventoState.open_close_dialog),
            width=rx.breakpoints(initial="90vw", sm="40vw"),
            max_width=rx.breakpoints(initial="90vw", sm="40vw"),
            height="60vh",
            max_height="60vh",
        ),
        open=EditarEventoState.dialog_bool,
    )

def fila_evento(evento:dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(evento['titulo'], style={"text-overflow":"ellipsis"}),
        rx.table.cell(evento['modalidad']),
        rx.table.cell(evento['modo_puntaje']),
        rx.table.cell(
            rx.cond(
                evento['auto_inscripcion'],
                rx.text("Sí", color_scheme="blue"),
                rx.text("No", color_scheme="gray"),
            ),
        ),
        rx.table.cell(
            rx.text(evento['estado']),
            #rx.cond(
            #    evento['activo'],
            #    rx.text("Activo", color_scheme="jade",),
            #    rx.text("Inactivo", color_scheme="gray",),
            #),
        ),
        
        rx.table.cell(
            rx.grid(
                button_edit(evento['id']),
                rx.cond(
                    evento['estado'] != "abierto",
                    rx.button(
                        rx.cond(evento['activo'],"Desactivar","activar"),
                        on_click=lambda: ListarEventoState.arternar_activo(evento['id']),
                        color_scheme=rx.cond(evento['activo'],"ruby","jade"),
                        size="1", variant="solid",
                    ),
                ),
                columns="2",
                place_items="center",
            ),
        
        ),
        style={"text-transform":"capitalize"}
    )

def fila_evento_movil(evento:dict) -> rx.Component:
    return rx.card(
        rx.flex(
            rx.text(evento['titulo'], size="2", weight="medium"),
            rx.grid(
                button_edit(evento['id']),
                rx.cond(
                    evento['estado'] != "abierto",
                    rx.button(
                        rx.cond(evento['activo'],"Desactivar","activar"),
                        on_click=lambda: ListarEventoState.arternar_activo(evento['id']),
                        color_scheme=rx.cond(evento['activo'],"ruby","jade"),
                        size="1", variant="solid",
                    ),
                ),
                columns="2",
                place_items="center",
            ),
            justify="between",
            width="100%",
        ),
        width="100%",
        style={"text-transform":"capitalize"},
    )

def tabla_eventos_view() -> rx.Component:
    return rx.vstack(
        rx.tablet_and_desktop(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Título"),
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
            width="100%",
        ),
        rx.mobile_only(
            rx.vstack(
                rx.grid(
                    rx.text("Título", size="1", weight="medium"),
                    rx.text("Acciones", size="1", weight="medium"),
                    grid_template_columns="1fr 30%",
                    width="100%",
                ),
                rx.foreach(ListarEventoState.lista, fila_evento_movil),
                spacing="2",
                width="100%",
            ),
            width="100%",
        ),
        spacing="2",
        width="100%",
    )

def eventos_view() -> rx.Component:
    return rx.flex(
        rx.card(
                rx.flex(
                    rx.heading("Gestión — Eventos", size="4"),
                    rx.grid(
                        input_box("Buscar", "Buscar por título...", ListarEventoState.busqueda, ListarEventoState.set_busqueda, "text"),
                        form_crear_evento_view(),
                        width="100%",
                        grid_auto_flow="column",
                        place_items="center",
                        spacing="5",
                    ),
                    width="100%",
                    direction="column",
                    spacing="3",
                ),
            position="sticky",
            top="0",
            width="100%",
            z_index="99",
        ),
        tabla_eventos_view(),
        form_editar_evento_view(),
        align="center",
        direction="column",
        width=rx.breakpoints(sm="95%", md="90%"),
        spacing="4",
    )