import reflex as rx
from itdb_ctf.states.evento_states import CreaEventoState
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
        rx.dialog.trigger(rx.button("Crear evento", on_click=CreaEventoState.open_close_dialog)),
        rx.dialog.content(
            form_evento(),
            close_dialog_button(CreaEventoState.open_close_dialog),
            width="100%",
            max_width="600px",
        ),
        open=CreaEventoState.dialog_bool,
        on_open_change=CreaEventoState.set_drop_mensaje
    )