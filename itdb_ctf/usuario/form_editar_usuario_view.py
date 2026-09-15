import reflex as rx
from itdb_ctf.components.form import input_box, select_catalog, badge_msg, button, close_dialog_button
from itdb_ctf.usuario.usuario_states import EditarUsuarioState


def form_edit_content() -> rx.Componen:
    return rx.vstack(
        rx.heading("Editar cuenta usuario", size="3"),
        input_box("Nombre", "Nombre...", EditarUsuarioState.nombre, EditarUsuarioState.set_nombre, "text"),
        input_box("Paterno","Paterno...",EditarUsuarioState.paterno, EditarUsuarioState.set_paterno, "text"),
        input_box("Materno","Materno...",EditarUsuarioState.materno, EditarUsuarioState.set_materno, "text"),
        input_box("Alias","Alias...",EditarUsuarioState.alias, EditarUsuarioState.set_alias, "text"),
        input_box("Correo electronico","itdb@itdonbosco.org..." ,EditarUsuarioState.email, EditarUsuarioState.set_email, "email"),
        rx.cond(
            EditarUsuarioState.no_user,
            select_catalog("Rol", "Seleccionar...", EditarUsuarioState.roles, EditarUsuarioState.set_id_rol, EditarUsuarioState.id_rol),
            None
        ),
        rx.center(
            rx.text("!!!Reseter password desde el panel¡¡¡", color_scheme="gray", weight="light", size="1"),
            width="100%",
        ),
        rx.cond(
            EditarUsuarioState.mensaje != "",
            badge_msg(EditarUsuarioState.mensaje, "yellow"),
            rx.spacer(),
        ),
        rx.hstack(
            rx.spacer(),
            button("Guardar", "jade", [EditarUsuarioState.guardar_edit_completo]),
            button("Cancelar", "ruby", [EditarUsuarioState.open_close_dialog, EditarUsuarioState.limpiar]),
            width="100%",
            spacing="2",
        ),
        width="100%",
        spacing="4",
    )

def editar_button(id_usuario):
    return rx.button(
        "Editar",
        size="1",
        variant="solid",
        color_scheme="blue",
        on_click=[EditarUsuarioState.cargar_usario(id_usuario), EditarUsuarioState.open_close_dialog],
    ),


def form_editar_usuario_view():
    return rx.dialog.root(
        rx.dialog.content(
            form_edit_content(),
            close_dialog_button(EditarUsuarioState.open_close_dialog),
            max_width="500px",
        ),
        open=EditarUsuarioState.dilog_bool,
        on_open_change=EditarUsuarioState.set_drop_mensaje,
    )