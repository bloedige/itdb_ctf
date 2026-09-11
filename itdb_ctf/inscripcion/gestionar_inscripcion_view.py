import reflex as rx
from itdb_ctf.components.form import button, select_catalog, input_box
from itdb_ctf.inscripcion.inscripcion_state import GestionarInscripcionState


def alert_descalificar(id_participa, descalificado, nombre, email) -> rx.Component:
    return rx.alert_dialog.root(
        rx.alert_dialog.trigger(
            button(
                rx.cond(descalificado, "Rehabilitar", "Descalificar"),
                rx.cond(descalificado, "jade", "amber"),
                [],
                size="1",
            ),
        ),
        rx.alert_dialog.content(
            rx.vstack(
                rx.text(
                    rx.cond(descalificado, "Rehabilitar", "Descalificar"),
                    size="2",
                    weight="medium",
                ),
                rx.text("Desea rehabilitar o descalificar la cuenta del evento.", size="1", weight="light"),
                rx.center(
                    rx.text(f"{nombre}", size="1", weight="regular"),
                    width="100%",
                ),
                rx.center(
                    rx.text(f"{email}", size="1", weight="medium"),
                    width="100%",
                ),
                rx.flex(
                    rx.alert_dialog.cancel(
                        button("Cancelar", "gray", [], size="1"),
                    ),
                    rx.alert_dialog.action(
                        button(
                            rx.cond(descalificado, "Rehabilitar", "descalificar"),
                            rx.cond(descalificado, "jade", "ruby"),
                            [GestionarInscripcionState.descalificar(id_participa)],
                            size="1",
                        ),
                    ),
                    justify="end",
                    width="100%",
                    spacing="2"
                ),
                width="100%",
                spacing="2",
            ),
            width="100%",
            max_width="400px",
        ),
    )


def alert_quitar(id_participa, nombre, email) -> rx.Component:
    return rx.alert_dialog.root(
        rx.alert_dialog.trigger(
            button("Quitar", "ruby", [], size="1"),
        ),
        rx.alert_dialog.content(
            rx.vstack(
                rx.text("Quitar", size="2", weight="medium"),
                rx.text("Desea realizar la acción para quitar la cuenta de el evento.", size="1", weight="light"),
                rx.center(
                    rx.text(f"{nombre}", size="1", weight="regular"),
                    width="100%",
                ),
                rx.center(
                    rx.text(f"{email}", size="1", weight="medium"),
                    width="100%",
                ),
                rx.flex(
                    rx.alert_dialog.cancel(
                        button("Cancelar", "gray", [], size="1"),
                    ),
                    rx.alert_dialog.action(
                        button("Quitar", "ruby", [GestionarInscripcionState.quitar(id_participa)], size="1"),
                    ),
                    justify="end",
                    width="100%",
                    spacing="2"
                ),
                width="100%",
                spacing="2",
            ),
            width="100%",
            max_width="400px",
        ),
    )


def fila_participante(u: dict) -> rx.Component:
    return rx.card(
        rx.tablet_and_desktop(

        rx.grid(
            rx.text(u['alias'], size="2", weight="medium"),
            rx.text(u['email_inst'], size="1", weight="regular"),
            rx.text(u['fec_ingreso'], size="1", weight="regular"),
            rx.cond(
                u['descalificado'],
                rx.badge("Descalificado", color_scheme="ruby", variant="surface"),
                rx.badge("Inscrito", color_scheme="jade", variant="surface"),
            ),
            rx.grid(
                alert_descalificar(u['id_participa'], u['descalificado'], u['nombre'], u['email_inst']),
                rx.cond(
                    u['quitar'],
                    alert_quitar(u['id_participa'], u['nombre'], u['email_inst']),
                ),
                place_items="center",
                columns=rx.cond(u['quitar'], "2", ""),
                width="100%",
            ),
            columns="5",
            place_items="center",
            spacing="2",
            width="100%",
        ),
        ),
        rx.mobile_only(
        rx.grid(
            rx.text(u['alias'], size="2", weight="medium"),
            rx.grid(
                alert_descalificar(u['id_participa'], u['descalificado'], u['nombre'], u['email_inst']),
                rx.cond(
                    u['quitar'],
                    alert_quitar(u['id_participa'], u['nombre'], u['email_inst']),
                ),
                place_items="center",
                columns=rx.cond(u['quitar'], "2", ""),
                width="100%",
            ),
            grid_template_columns="1fr 30%",
            spacing="2",
            width="100%",
        ),

        ),
        bg=rx.cond(u['descalificado'], "#A3292942", ""),
        width="100%",
    )


def filtros() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Gestionar participantes de un evento", size="4"),
            select_catalog("Eventos", "Seleccionar...", GestionarInscripcionState.eventos, GestionarInscripcionState.set_id_evento_ges, GestionarInscripcionState.id_evento_ges),
            rx.grid(
                input_box("Estudiantes", "Nombre, email, alias", GestionarInscripcionState.busqueda_ges, GestionarInscripcionState.set_busqueda_ges, "text"),
                select_catalog("Estado en evento", "Todos...", GestionarInscripcionState.estados, GestionarInscripcionState.set_id_estado_filtro, GestionarInscripcionState.id_estado_filtro),
                place_items="center",
                grid_template_columns="1fr 20%",
                width="100%",
                spacing="3",
            ),
            width="100%",
            spacing="3",
        ),
        width="100%",
        spacing="5",
        position="sticky",
        top="0",
        z_index="99",
    )


def contenido() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.cond(
                GestionarInscripcionState.id_evento_ges != "",
                rx.vstack(
                    rx.tablet_and_desktop(
                        rx.grid(
                            rx.text("Alias", size="1", weight="medium"),
                            rx.text("Correo", size="1", weight="medium"),
                            rx.text("Fecha inscripción", size="1", weight="medium"),
                            rx.text("Estado", size="1", weight="medium"),
                            rx.text("acciones", size="1", weight="medium"),
                            columns="5",
                            place_items="center",
                            width="100%",
                        ),
                    ),
                    rx.mobile_only(
                        rx.grid(
                            rx.text("Alias", size="1", weight="medium"),
                            rx.text("Acciones", size="1", weight="medium"),
                            grid_template_columns="1fr 30%",
                            width="100%", 
                        ),
                        width="100%",
                    ),
                    rx.foreach(GestionarInscripcionState.participantes, fila_participante),
                    width="100%", spacing="3",
                ),
                rx.text("seleccione evento a gestionar", color_scheme="gray", size="2"),
            ),
            width="100%", 
        ),
        width="100%",
    )

def gestionar_inscripcion_view() -> rx.Component:
    return rx.grid(
        filtros(),
        contenido(),
        spacing="4",
        width=rx.breakpoints(sm="95%", md="80%"),
    )
