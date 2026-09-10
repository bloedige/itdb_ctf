import reflex as rx
from itdb_ctf.asociar.asociar_state import GestionarRetoState, EditarAsociarState
from itdb_ctf.components.form import input_box, button, select_catalog


def edit_content() -> rx.Component:
    return rx.vstack(
        rx.text(EditarAsociarState.titulo_edit, size="3", weight="medium"),
        rx.grid(
            rx.cond(
                EditarAsociarState.evento_edit_dinamico,
                rx.grid(
                    select_catalog("Modo de reto", "seleccionar...", GestionarRetoState.modos, EditarAsociarState.set_id_modo_edit, EditarAsociarState.id_modo_edit),
                    input_box("Punataje inicial", EditarAsociarState.inicial_def, EditarAsociarState.puntaje_inicial_edit, EditarAsociarState.set_puntaje_inicial_edit, "number"),
                    rx.cond(
                        EditarAsociarState.reto_edit_dinamico,
                        input_box("Punataje inicial", rx.cond(EditarAsociarState.minimo_def, EditarAsociarState.minimo_def, "0"), EditarAsociarState.puntaje_minimo_edit, EditarAsociarState.set_puntaje_minimo_edit, "number"),
                    ),
                    spacing="3",
                    width="80%",
                ),
                rx.grid(
                    input_box("Punataje inicial", EditarAsociarState.inicial_def, EditarAsociarState.puntaje_inicial_edit, EditarAsociarState.set_puntaje_inicial_edit, "number"),
                    spacing="3",
                    width="80%",
                ),
            ),
            place_items="center",
            spacing="3",
            width="100%",
        ),
        spacing="3",
        width="100%",
    )


def dialog_edit(item: dict) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                "Editar",
                size="1",
                variant="surface",
                color_scheme="jade",
                on_click=lambda: EditarAsociarState.open_edit(item['id_contine'], item['titulo']),
            ),
        ),
        rx.dialog.content(
            rx.grid(
                edit_content(),
                rx.flex(
                    button("Confirmar", "green", [EditarAsociarState.guardar_edit_contiene], size="2"),
                    button("Cancelar", "red", [EditarAsociarState.close_edit], size="2"),
                    justify="end",
                    spacing="3",
                    width="100%",
                ),
                width="100%",
                spacing="3",
            ),
            max_width="400px",
        ),
        open=EditarAsociarState.edit_bool,
    )


def alert_dialog(id_reto, titulo) -> rx.Component:
    return rx.alert_dialog.root(
        rx.alert_dialog.trigger(
            button("Quitar", "red", [], size="1"),
        ),
        rx.alert_dialog.content(
            rx.alert_dialog.title("Quitar reto del evento"),
            rx.alert_dialog.description(f"¿Seguro que quieres quitar '{titulo}' de este evento?"),
            rx.flex(
                rx.alert_dialog.cancel(
                    button("Cancelar", "gray", [], size="2"),
                ),
                rx.alert_dialog.action(
                    button("Quitar", "red", [lambda: GestionarRetoState.quitar_retos(id_reto)], size="2"),
                ),
                justify="end",
                spacing="2",
                width="100%",
            ),
            spacing="2",
            width="100%",
        ),
    )


def fila_gestion(reto: dict) -> rx.Component:
    return rx.card(
        rx.grid(
            rx.text(reto['titulo'], size="2", weight="medium"),
            rx.text(f"{reto['puntaje_inicial']} pts.", size="2", weight="regular"),
            rx.text(f"{reto['puntaje_minimo']} pts.", size="2", weight="regular"),
            rx.text(reto['categoria'], size="2", weight="regular"),
            rx.text(reto['dificultad'], size="2", weight="regular"),
            rx.text(reto['modo'], size="2", weight="regular"),
            rx.grid(
                dialog_edit(reto),
                alert_dialog(reto['id_reto'], reto['titulo']),
                columns="2",
                place_items="center",
                width="100%",
            ),
            columns="7",
            place_items="center",
            width="100%",
        ),
        width="100%",
    )


def filtros() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Gestionar retos de un evento", size="4"),
            rx.grid(
                select_catalog("Eventos (en curso / futuro)", "Seleccionar...", GestionarRetoState.eventos_gest, GestionarRetoState.set_id_evento_gest),
                rx.grid(
                    input_box("Buscar por titulo", "Titutlo...", GestionarRetoState.busqueda_gest, GestionarRetoState.set_busqueda_gest, "text"),
                    select_catalog("Categorias", "Seleccionar...", GestionarRetoState.categorias, GestionarRetoState.set_id_categoria_gest_filtro, GestionarRetoState.id_categoria_gest_filtro),
                    select_catalog("Dificultad", "Seleccionar...", GestionarRetoState.dificultades, GestionarRetoState.set_id_dificultad_gest_filtro, GestionarRetoState.id_dificultad_gest_filtro),
                    select_catalog("Modo puntaje", "Seleccionar...", GestionarRetoState.modos, GestionarRetoState.set_id_modo_gest_filtro, GestionarRetoState.id_modo_gest_filtro),
                    place_items="center",
                    grid_template_columns="30% 1fr 1fr 1fr",
                    columns={"base": "1", "md": "4"},
                    spacing="2",
                    width="100%",
                ),
                place_items="center",
                spacing="2",
                width="100%",
            ),
            spacing="4",
            width="100%",
        ),
        width="100%",
    )


def contenido() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.cond(
                GestionarRetoState.id_evento_gest != "",
                rx.foreach(GestionarRetoState.retos_gest, fila_gestion),
                rx.text("seleccione evento a gestionar", color_scheme="gray", size="2"),
            ),
            spacing="3",
        ),
        width="100%",
    )


def gestionar_asociar_reto_view() -> rx.Component:
    return rx.vstack(
        filtros(),
        contenido(),
        spacing="5",
        width="80%",
    )
