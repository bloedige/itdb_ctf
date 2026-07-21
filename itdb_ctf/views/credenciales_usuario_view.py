import reflex as rx
from itdb_ctf.components.form import button, card_text
from itdb_ctf.states.usuario_states import CredencialesUsuarioState, EditarUsuarioState, ListarUsuarioState

def credenciales_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.heading(CredencialesUsuarioState.cred_titulo, size="3"),
                rx.card(
                    rx.grid(
                        rx.icon("key"),
                        card_text("Correo electronico", CredencialesUsuarioState.cred_email),
                        card_text("Contraseña", CredencialesUsuarioState.cred_password),
                        width="100%",
                        place_items="center",
                        grid_template_columns="20% 1fr 1fr",
                    ),
                    bg="#29A3877D",
                    width="100%",     
                ),
                rx.grid(
                    rx.box(
                        rx.text("Alias", weight="regular", size="1"),
                        rx.center(rx.text(CredencialesUsuarioState.cred_alias, weight="light", size="2"), width="100%"),          
                    ),
                    rx.box(
                        rx.text("Rol", weight="regular", size="1"),
                        rx.center(rx.text(CredencialesUsuarioState.cred_rol, weight="light", size="2"), width="100%"),          
                    ),
                    spacing="2",
                    width="100%",
                    columns="2",
                ),
                rx.divider(),
                rx.center(rx.text("!!! Copia las credenciales no se volveran a mostrar ¡¡¡", size="1", weight="light" ,color_scheme="amber"),width="100%"), 
                rx.button(
                    "Copiar y cerrar",
                    color_scheme="jade",
                    on_click=[CredencialesUsuarioState.copiar, CredencialesUsuarioState.close_credenciales],
                    size="2",
                    width="100%",
                ),
                width="100%",
                spacing="3",
            ),
            width="100%",
            max_width="400px",
            on_pointer_down_outside=rx.prevent_default,
            on_escape_key_down=rx.prevent_default,
        ),
        open=CredencialesUsuarioState.cred_bool,
    )

def alert_reset_password(id_usuario, email, alias, rol) -> rx.Component:
    return rx.alert_dialog.root(
        rx.alert_dialog.trigger(
            rx.button(
                "Restablecer",
                color_scheme="amber",
                variant="surface",
                size="1",
            ),
        ),
        rx.alert_dialog.content(
            rx.vstack(
                rx.alert_dialog.title(
                    rx.text(
                        "Restablecer contraseña",
                        size="3",
                        weight="medium",
                    ),                       
                ),
                rx.alert_dialog.description(
                    rx.vstack(
                        rx.text("Desea generar una nueva contraseña. La actual dejara de funcionar.", size="1"),
                        spacing="3",
                        width="100%",
                    ),
                ),
                rx.flex(
                    rx.alert_dialog.cancel(button("Cancelar", "gray", [], size="1")),
                    rx.alert_dialog.action(button("Restablecer", "amber", [EditarUsuarioState.resetear_password(id_usuario,email,alias,rol)], size="1")),
                    justify="end",
                    width="100%",
                    spacing="2"
                ),
                width="100%",
                max_width="500px",
                spacing="3",
            ),
            max_width="400px",
        ),
    )

def alert_estado(id_usuario, activo, email) -> rx.Component:
    return rx.alert_dialog.root(
        rx.alert_dialog.trigger(
            button(
                rx.cond(activo, "Desactivar", "Activar"),
                rx.cond(activo, "ruby", "jade"),
                [],
                size="1"
            ),
        ),
        rx.alert_dialog.content(
            rx.vstack(
                rx.alert_dialog.title(
                    rx.text(
                        rx.cond(activo, "Desactivar cuenta", "Activar cuenta"),
                        size="3",
                        weight="medium",
                    ),
                ),
                rx.alert_dialog.description(
                    rx.vstack(
                        rx.text("Desea realizar la acción para cambiar el estado de la cuenta.", size="1"), 
                        rx.center(rx.text(f"{email}", weight="medium", size="1" ,color_scheme=rx.cond(activo, "ruby", "jade")), width="100%"),
                        spacing="3",
                        width="100%",
                    ),               
                ),
                rx.flex(
                    rx.alert_dialog.cancel(button("Cancelar", "gray", [], size="1")),
                    rx.alert_dialog.action(button(rx.cond(activo, "Desactivar cuenta", "Activar cuenta"), rx.cond(activo, "ruby", "jade"), [ListarUsuarioState.altenar_activo(id_usuario)], size="1")),
                    justify="end",
                    width="100%",
                    spacing="2"
                ),
                width="100%",
                spacing="3",
            ),
            max_width="400px",
        ),
    )