import reflex as rx
from itdb_ctf.components.form import button, select_catalog, input_box, close_dialog_button
from itdb_ctf.inscripcion.inscripcion_state import InscribirState

def accion_fila(u:dict) -> rx.Component:
    return rx.cond(
        InscribirState.ids_carrito.contains(u['id_usuario']),
        rx.badge(rx.icon("check"), "Agregado", color_scheme="gray", variant="surface"),
        rx.button(
            rx.icon("plus"),
            "Agregar",
            size="1",
            variant="surface",
            color_scheme="jade",
            on_click=InscribirState.agregar_carrito(u['id_usuario'], u['nombre'], u['email_inst']),
        ),
    ),

def fila_candidato(u: dict) -> rx.Component:
    return rx.card(
        rx.tablet_and_desktop(
            rx.grid(
                rx.text(u['alias'], size="2", weight="medium"),
                rx.text(u['nombre'], size="2", weight="regular"),
                rx.text(u['email_inst'], size="1", weight="regular"),
                rx.text(u['metodo'], size="2", weight="medium"),
                accion_fila(u),
                columns="5",
                place_items="center",
                spacing="2",
                width="100%",
            ),
        ),
        rx.mobile_only(
            rx.flex(
                rx.text(u['alias'], size="2", weight="medium"),
                accion_fila(u),
                justify="between",
                width="100%",
            ),
        ),
        width="100%",
    )

def item_carrito(item: dict) -> rx.Component:
    return rx.flex(
        rx.text(item['nombre'], size="1", weight="light", color_scheme="gray"),
        rx.spacer(),
        button("Quitar", "ruby", [InscribirState.quitar_carrito(item['id_usuario'])], size="1"),
        width="100%",
        spacing="1",
    )

def card_carrito() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.text("Por inscribir", size="3", weight="medium"),
            rx.divider(),
            rx.cond(
                InscribirState.carrito_vacio,
                rx.text("Agregar estudiantes"),
                rx.flex(
                rx.foreach(InscribirState.carrito, item_carrito),
                spacing="1",
                overflow_y="auto", 
                max_height="40vh",
                direction="column",
                width="100%",
                ),
            ),
            rx.divider(),
            select_catalog("Evento", "Seleccionar evento", InscribirState.eventos, InscribirState.set_id_evento_car, InscribirState.id_evento_car),
            rx.grid(
                button("Vaciar", "ruby", [InscribirState.vaciar_carrito], size="2"),
                button("Inscribir", "jade", [InscribirState.guardar_carrito], size="2"),
                columns="2",
                spacing="2",
                width="100%",
            ),
            width="100%",
            spacing="3",
        ),
        width="100%",
        position="sticky",
        top="6.3em",
        z_index="99",
    )

def filtros() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Inscribir estudiantes a eventos", size="4"),
            rx.grid(
                input_box("Estudiantes", "Nombre, email, alias", InscribirState.busqueda_ins, InscribirState.set_busqueda_ins, "text"),
                select_catalog("Modo auth", "Todos...", InscribirState.metodos, InscribirState.set_id_metodo_filtro, InscribirState.id_metodo_filtro),
                place_items="center",
                grid_template_columns="1fr 20%",
                width="100%",
                spacing="3",
            ),
            width="100%",
            spacing="3",
        ),
        width="100%",
        position="sticky",
        top="0",
        z_index="99",
    )

def contenido() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.cond(
                InscribirState.id_evento_car != "",
                rx.vstack(
                    rx.tablet_and_desktop(
                        rx.grid(
                            rx.text("Alias", size="1", weight="medium"),
                            rx.text("Nombre", size="1", weight="medium"),
                            rx.text("Correo", size="1", weight="medium"),
                            rx.text("Modo auth", size="1", weight="medium"),
                            rx.text("Acciones", size="1", weight="medium"),
                            columns="5",
                            place_items="center",
                            width="100%",
                        ),
                        width="100%",
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
                    rx.foreach(InscribirState.candidatos, fila_candidato),
                    width="100%", spacing="3",
                ),
                rx.text("seleccione evento para incribir", color_scheme="gray", size="2"),
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
            rx.text("---", color_scheme="gray", size="1", weight="light"),
        ),
        spacing="1",
        width="100%",
    )

def archivo_csv() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Gestion de inscripciones", size="3", weight="bold"),
            select_catalog("Evento", "Seleccionar", InscribirState.eventos, InscribirState.set_id_evento_csv, InscribirState.id_evento_csv),
            rx.cond(
                InscribirState.csv_nombre != "",
                rx.grid(
                    rx.badge(
                        rx.icon("file", size=20),
                        rx.text(
                            InscribirState.csv_nombre,
                            size="1",
                            text_overflow="ellipsis",
                            white_space="nowrap",
                            overflow="hidden",
                            width="100%",
                        ),
                    ),
                    button("Analizar csv", "jade", [InscribirState.analizar_csv], size="1"),
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
                on_drop=InscribirState.on_drop_csv(rx.upload_files(upload_id="csv_inscripcion")),
                border="1px dashed #888", padding="1em",
                border_radius=".25em",
                width="100%",
            ),
            rx.cond(
                InscribirState.csv_analize,
                rx.grid(
                    button("Cerrar", "gray", [InscribirState.cerrar_csv], size="2"),
                    button("Confirmar", "jade", [InscribirState.confirmar_csv], size="2"),
                    width="100%",
                    columns="2",
                    spacing="2",
                )
            ),
            width="100%",
            spacing="2",
        ),
    )

def reporte_csv() -> rx.Component:
    return rx.vstack(
        rx.heading("Reporte de inscripción por csv", size="3", weight="bold"),
        rx.text(
            """Revisa antes de confirmar. Los nuevos se crearan como cuentas Google
que se completan cuando el estudiante inicia sesion.""",
            white_space="pre-wrap", size="1", weight="light", color_scheme="gray",
        ),
        rx.vstack(
            rx.divider(),
            prev_csv("Nuevos (se crean e inscriben)", InscribirState.prev_nuevos, "jade"),
            rx.divider(),
            prev_csv("Existente (se inscriben)", InscribirState.prev_existentes, "blue"),
            rx.divider(),
            prev_csv("Omitidos", InscribirState.prev_omitidos, "ruby", True),
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
                on_click=[InscribirState.open_close_dialog_csv],
                width="100%",
                variant="surface",
            ),
        ),
        rx.dialog.content(
            rx.tablet_and_desktop(
                rx.grid(
                    reporte_csv(),
                    archivo_csv(),
                    grid_template_columns="70% 1fr",
                    spacing="4",
                    width="100%",
                ),
            ),
            rx.mobile_only(
                rx.grid(
                    archivo_csv(),
                    reporte_csv(),
                    spacing="4",
                    width="100%",
                ),
            ),
            close_dialog_button(InscribirState.open_close_dialog_csv),
            max_width=rx.breakpoints(sm="95vw", md="70vw"),  
            height="90vh",          
        ),
        open=InscribirState.csv_dialog,
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
        position="sticky",
        top="0",
        z_index="95",
    )             

def inscribir_view() -> rx.Component:
    return rx.grid(
        rx.tablet_and_desktop(
            rx.grid(
                rx.vstack(
                    filtros(),
                    contenido(),
                    spacing="4",
                    width="100%",
                ),
                rx.vstack(
                    card_csv(),
                    card_carrito(),
                    spacing="4",
                    width="100%",
                ),
                grid_template_columns="80% 1fr",
                spacing="4",
                width="100%",
            ),
            width="90%",
        ),
        rx.mobile_only(
            rx.grid(
                filtros(),
                card_csv(),
                contenido(),
                card_carrito(),
                width="100%",
                spacing="3",
            ),
            width="95%",
        ),
        justify_items="center",
        width="100%",
    )

