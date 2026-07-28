import reflex as rx
from itdb_ctf.components.form import button, select_catalog, input_box, badge_msg, close_dialog_button
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
                        width="100%",spacing="3"
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
                        width="100%",spacing="3"
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

def prev_csv(titulo, items, color, motivo=False) -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.text(titulo, size="2", weight="regular"),
            rx.spacer(),
            rx.badge(items.length().to_string(), size="2", weight="regular", color_scheme=color),
            width="95%",
        ),
        rx.cond(
            items.length() > 0,
            rx.vstack(
                rx.foreach(
                    items, lambda it: rx.grid(
                        rx.text(it['email'], size="1", weight="light"),
                        rx.cond(
                            motivo,
                            rx.text(it['motivo'], size="1", weight="light", color_scheme="gray"),
                        ),
                        columns="2",
                        width="100%",
                        spacing="2"   
                    ),
                ),
            ),
            rx.text("---", color_scheme="gray", size="1", weight="light")
        ),
        spacing="1",
        width="100%",
    )

def archivo_csv() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Gestion de inscripciones", size="3", weight="bold"),
            select_catalog("Evento", "Seleccionar", InscripcionState.eventos, InscripcionState.set_id_evento_csv, InscripcionState.id_evento_csv),
            rx.cond(
                InscripcionState.csv_nombre != "",
                rx.grid(
                    rx.badge(
                        rx.icon("file", size=20),
                        rx.text(
                            InscripcionState.csv_nombre,
                            size="1", 
                            text_overflow="ellipsis",
                            white_space="nowrap",
                            overflow="hidden",
                            width="100%",
                        ),  
                    ), 
                    button("Analizar csv", "jade", [InscripcionState.analizar_csv], size="1"),
                    width="100%",
                    grid_template_columns="65% 1fr",
                    spacing="2",
                ),
            ),
            rx.upload(
                rx.text("Arrastrar o hacer click para Subir csv", size="1"),
                id="csv_inscripcion",
                max_files=1,
                accept={"text/csv": [".csv"]},
                on_drop=InscripcionState.on_drop_csv(rx.upload_files(upload_id="csv_inscripcion")),
                border="1px dashed #888", padding="1em",
                border_radius=".25em",
                width="100%",
            ),
            rx.cond(
                InscripcionState.csv_analize,
                rx.grid(
                    button("Cerrar","gray", [InscripcionState.cerrar_csv], size="2"),
                    button("Confirmar", "jade", [InscripcionState.confirmar_csv], size="2"),
                    width="100%",
                    columns="2",
                    spacing="2",
                )
            ),
            width="100%",
            spacing="2",
        ),
    )

def reporte_csv() -> rx.components:
    return rx.vstack(
        rx.heading("Reporte de inscripción por csv", size="3", weight="bold"),
        rx.text(
            """Revisa antes de confirmar. Los nuevos se crearan como cuentas Google
que se completan cuando el estudiante inicia sesion.""",
            white_space="pre-wrap", size="1", weight="light", color_scheme="gray",
        ),
        rx.vstack(
            rx.divider(),
            prev_csv("Nuevos (se crean e inscriben)", InscripcionState.prev_nuevos, "jade"),
            rx.divider(),
            prev_csv("Existente (se inscriben)", InscripcionState.prev_existentes, "blue"),
            rx.divider(),
            prev_csv("Omitidos", InscripcionState.prev_omitidos, "ruby", True),
            width="100%",
            max_height="60vh",
            overflow_y="auto",    
        ), 
    )

def dialog_csv() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                "CSV", 
                color_scheme="jade", 
                on_click=[InscripcionState.open_close_dialog_csv], 
                width="100%",
                variant="surface",
            ),
        ),
        rx.dialog.content(
            rx.grid(
                reporte_csv(),
                archivo_csv(),
                grid_template_columns="65% 1fr",
                spacing="4",
                width="100%",   
            ),
            close_dialog_button(InscripcionState.open_close_dialog_csv),
            max_width="900px",
        ),
        open=InscripcionState.csv_dialog,
    )

def card_csv() -> rx.Component:
    return rx.card(
        rx.grid(
            rx.text("Incribir estudiantes por lote", size="2", weight="medium"),
            dialog_csv(),
            width="100%",
            spacing="2",
        ),
        width="100%",
        pointer_events=rx.cond(InscripcionState.modo, "none", "auto"),
        opacity=rx.cond(InscripcionState.modo, ".5", "1"),
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
                card_csv(),
                grid_template_rows="1fr 1fr",
                spacing="5",
                width="100%",
                height="100%",
            ),
            grid_template_columns="80% 1fr",
            spacing="5",
            width="100%",
        ),
        spacing="5",
        width="100%",
    )