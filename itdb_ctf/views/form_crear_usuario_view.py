import reflex as rx
from itdb_ctf.components.form import input_box,select_catalog, button, close_dialog_button,badge_msg
from itdb_ctf.states.usuario_states import CrearUsuarioState
from itdb_ctf.views.credenciales_usuario_view import credenciales_dialog



def form_content() -> rx.Component:
    return rx.vstack(
        rx.heading("Crear cueta usuario", size="3"),
        input_box("Nombre", "Nombre...", CrearUsuarioState.nombre, CrearUsuarioState.set_nombre, "text"),
        input_box("Paterno", "Paterno...", CrearUsuarioState.paterno, CrearUsuarioState.set_paterno, "text"),
        input_box("Materno", "Materno...", CrearUsuarioState.materno, CrearUsuarioState.set_materno, "text"),
        input_box("Alias", "Alias...", CrearUsuarioState.alias, CrearUsuarioState.set_alias, "text"),
        input_box("Correo electronico", "itdb@itdonbosco.org....", CrearUsuarioState.email, CrearUsuarioState.set_email, "email"),
        select_catalog("Rol", "Seleccionar...", CrearUsuarioState.roles, CrearUsuarioState.set_id_rol, CrearUsuarioState.id_rol),
        rx.cond(
            CrearUsuarioState.mensaje != "",
            badge_msg(CrearUsuarioState.mensaje, "yellow"),
            rx.spacer(),
        ),
        rx.hstack(
            rx.spacer(),
            button("Guardar", "jade", [CrearUsuarioState.guardar_completo], size="2"),
            button("Cancelar", "ruby", [CrearUsuarioState.open_close_dialog, CrearUsuarioState.limpiar]),
            width="100%",
            spacing="2",
        ),
        width="100%",
        spacing="3",
    )

def form_crear_usuario_view() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon("plus"),
                "Crear Usuario",
                size="2",
                variant="surface",
                color_scheme="jade",
                on_click=CrearUsuarioState.open_close_dialog,
            )
        ),
        rx.dialog.content(
            form_content(),
            close_dialog_button(CrearUsuarioState.open_close_dialog),
            max_width="500px",
        ),
        open=CrearUsuarioState.dialog_bool,
        on_open_change=CrearUsuarioState.set_drop_mensaje,   
    )
