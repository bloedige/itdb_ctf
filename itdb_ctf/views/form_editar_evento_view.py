import reflex as rx
from itdb_ctf.states.evento_states import EditarEventoState
from itdb_ctf.components.form import input_box, input_datetime, select_catalog, checked, text_area, button, badge_msg, close_dialog_button

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
        ),
        rx.grid(
            rx.cond(EditarEventoState.mensaje != "", badge_msg(EditarEventoState.mensaje,"red"), rx.spacer()),
            rx.hstack(
                rx.spacer(),
                button("Guardar","green",[EditarEventoState.guardar_edit_completo]),
                button("Cancelar", "red", [EditarEventoState.open_close_dialog, EditarEventoState.limpiar]),
                spacing="2",
            ),
            spacing="2",
            rows="2",
            width="100%",
        ),
        spacing="5",
        width="100%",       
    )

def form_editar_evento_view(evento:dict) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                "Editar",
                on_click=[lambda:EditarEventoState.cargar_evento(evento['id']),EditarEventoState.open_close_dialog],
                size="1", 
                variant="soft", 
                color_scheme="cyan",
            ),
        ),
        rx.dialog.content(
            form_evento_edit(),
            close_dialog_button(EditarEventoState.open_close_dialog),
            width="100%",
            max_width="600px",
        ),
        open=EditarEventoState.dialog_bool,
    ) 