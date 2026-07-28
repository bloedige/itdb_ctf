import reflex as rx
from itdb_ctf.components.form import button, select_catalog, input_box, badge_msg
from itdb_ctf.states.inscripcion_state import InscripcionState




def alert_descalificar(id_participa, descalificado, nombre, email) -> rx.Component:
    return rx.alert_dialog.root(
        rx.alert_dialog.trigger(
            button(
                rx.cond(descalificado, "Rehabilitar","Descalificar"),
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
                    rx.text(f"{email}",size="1",weight="medium"),
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
                            [InscripcionState.descalificar(id_participa)],
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
                rx.text("Quitar", size="2", weight="medium",),
                rx.text(f"Desea realizar la acción para quitar la cuenta de el evento.", size="1", weight="light"),
                rx.center(
                    rx.text(f"{nombre}", size="1", weight="regular"),
                    width="100%",
                ),
                rx.center(
                    rx.text(f"{email}",size="1",weight="medium"),
                    width="100%",
                ),
                rx.flex(
                    rx.alert_dialog.cancel(
                        button("Cancelar", "gray", [], size="1"),
                    ),
                    rx.alert_dialog.action(
                        button("Quitar", "ruby", [InscripcionState.quitar(id_participa)], size="1"),
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

def fila_candidato(u:dict) -> rx.Component:
    return rx.card(
        rx.grid(
            rx.text(u['alias'], size="2", weight="medium"),
            rx.text(u['nombre'], size="2", weight="regular"),
            rx.text(u['email_inst'], size="1", weight="regular"),
            rx.text(u['metodo'], size="2", weight="medium"),
            rx.cond(
                InscripcionState.ids_carrito.contains(u['id_usuario']),
                rx.badge(rx.icon("check"), "Agregado", color_scheme="gray", variant="surface"),
                rx.button(
                    rx.icon("plus"),
                    "Agregar",
                    size="1",
                    variant="surface",
                    color_scheme="jade",
                    on_click=InscripcionState.agregar_carrito(u['id_usuario'], u['nombre'], u['email_inst']),
                ),
            ),
            columns="5",
            place_items="center",
            spacing="2",
            width="100%",
        ),
        width="100%",
    )

def fila_participante(u:dict) -> rx.Component:
    return rx.card(
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
        bg=rx.cond(u['descalificado'], "#A3292942", ""),
        width="100%",
    )

def item_carrito(item:dict) -> rx.Component:
    return rx.grid(
        rx.text(item['nombre'], size="2", weight="light", color_scheme="gray"),
        button("Quitar", "ruby", [InscripcionState.quitar_carrito(item['id_usuario'])], size="1"),
        place_items="center",
        grid_template_columns="1fr 10%",
        width="100%",
        spacing="2",
    )
    
def card_carrito() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.text("Por inscribir", size="3", weight="medium"),
            rx.divider(),
            rx.cond(
                InscripcionState.carrito_vacio,
                rx.text("Agregar estudiantes"),
                rx.foreach(InscripcionState.carrito, item_carrito),
            ),
            rx.divider(),
            select_catalog("Evento", "Seleccionar evento", InscripcionState.eventos, InscripcionState.set_id_evento_car, InscripcionState.id_evento_car),
            rx.grid(
                button("Inscribir", "jade", [InscripcionState.guardar_carrito], InscripcionState.carrito_vacio, size="2"),
                button("Vaciar", "ruby", [InscripcionState.vaciar_carrito], size="2"),
                columns="2",
                spacing="2",
                width="100%",
            ),
            width="100%",
            spacing="3",
        ),
        width="100%",
        pointer_events=rx.cond(InscripcionState.modo, "none", "auto"),
        opacity=rx.cond(InscripcionState.modo, ".5", "1"),
    )

def filtros() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Inscripción / Gestion a eventos", size="3"),
            rx.tabs.root(
                rx.tabs.list(
                    rx.tabs.trigger(
                        rx.text("Inscribir", size="2", weight="medium"),
                        value="inscribir",
                        width="50%",
                    ),
                    rx.tabs.trigger(
                        rx.text("Gestionar", size="2", weight="medium"),
                        value="gestionar",
                        width="50%",
                    ),
                ),
                value=InscripcionState.tab,
                on_change=InscripcionState.set_tab,
                width="100%",
            ),
            rx.cond(
                InscripcionState.modo,
                rx.vstack(
                    select_catalog("Eventos", "Seleccionar...", InscripcionState.eventos, InscripcionState.set_id_evento_ges, InscripcionState.id_evento_ges),
                    rx.grid(
                        input_box("Estudiantes", "Nombre, email, alias", InscripcionState.busqueda_ges, InscripcionState.set_busqueda_ges, "text"),
                        select_catalog("Estado en evento", "Todos...", InscripcionState.estados, InscripcionState.set_id_estado_filtro, InscripcionState.id_estado_filtro),
                        place_items="center",
                        grid_template_columns="1fr 15%",
                        width="100%",
                        spacing="3",
                    ),
                    width="100%",
                    spacing="3",
                ),
                rx.grid(
                    input_box("Estudiantes", "Nombre, email, alias", InscripcionState.busqueda_ins, InscripcionState.set_busqueda_ins, "text"),
                    select_catalog("Metodo auth", "Todos...", InscripcionState.metodos, InscripcionState.set_id_metodo_filtro, InscripcionState.id_metodo_filtro),
                    place_items="center",
                    grid_template_columns="1fr 15%",
                    width="100%",
                    spacing="3",
                ),
            ),
            width="100%",
            spacing="3",
        ),
        width="100%",
        spacing="5",
    )

def contendido() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.cond(
                InscripcionState.modo,
                rx.cond(
                    InscripcionState.id_evento_ges != "",
                    rx.vstack(
                        rx.grid(
                            rx.text("Alias", size="1", weight="medium"),
                            rx.text("Correo", size="1", weight="medium"),
                            rx.text("Fecha inscripción", size="1", weight="medium"),
                            rx.text("Metodo auth", size="1", weight="medium"),
                            rx.text("acciones", size="1", weight="medium"),
                            columns="5",
                            place_items="center",
                            width="100%",
                        ),
                        rx.foreach(InscripcionState.participantes, fila_participante),
                        width="100%",spacing="5"
                    ),
                    rx.text("seleccione evento para incribir", color_scheme="gray", size="2")
                ),
                rx.cond(
                    InscripcionState.id_evento_car != "",
                    rx.vstack(
                        rx.grid(
                            rx.text("Alias", size="1", weight="medium"),
                            rx.text("Nombre", size="1", weight="medium"),
                            rx.text("Correo", size="1", weight="medium"),
                            rx.text("Metodo auth", size="1", weight="medium"),
                            rx.text("acciones", size="1", weight="medium"),
                            columns="5",
                            place_items="center",
                            width="100%",
                        ),
                        rx.foreach(InscripcionState.candidatos, fila_candidato),
                        width="100%",spacing="5"
                    ),
                    rx.text("seleccione evento a gestionar", color_scheme="gray", size="2")
                ),
               
            ),
            width="100%",
            spacing="5",
        ),
        width="100%",
        spacing="5",
    )

def inscripcion_view() -> rx.Component:
    return rx.vstack(
        rx.grid(
            rx.vstack(
                filtros(),
                contendido(),
                spacing="5",
                width="100%",
            ),
            rx.vstack(
                card_carrito(),
                spacing="5",
                width="100%",
            ),
            grid_template_columns="80% 1fr",
            spacing="5",
            width="100%",
        ),
        spacing="5",
        width="100%",
    )