import reflex as rx
from itdb_ctf.asociar.asociar_state import AsociarRetoState
from itdb_ctf.components.form import input_box, button, select_catalog, checked


def override_content(modo, inicial, minimo) -> rx.Component:
    return rx.vstack(
        rx.text(AsociarRetoState.titulo_dialog, size="3", weight="medium"),
        rx.text("Valores por defecto", size="2", weight="regular"),
        rx.divider(),
        rx.grid(
            rx.grid(
                rx.text("Modo puntaje", weight="light"),
                rx.text("Puntaje inicial", weight="light"),
                rx.text("Puntaje minimo", weight="light"),
                style={"font-size": ".7em"},
                place_items="center",
                columns="3",
                width="100%",
            ),
            rx.grid(
                rx.text(modo, size="1", weight="light", style={"text_transform": "capitalize"}),
                rx.text(inicial, size="1", weight="light"),
                rx.text(rx.cond(minimo, minimo, "---"), size="1", weight="light"),
                place_items="center",
                columns="3",
                width="100%",
            ),
            spacing="1",
            width="100%",
        ),
        rx.divider(),
        rx.grid(
            rx.tabs.root(
                rx.tabs.list(
                    rx.tabs.trigger("Default", value="def", width="50%", color_scheme="jade"),
                    rx.tabs.trigger("Override", value="ove", width="50%", color_scheme="jade"),
                    size="1",
                ),
                default_value="def",
                on_change=AsociarRetoState.set_override_mode,
            ),
            width="100%",
        ),
        rx.grid(
            rx.cond(
                AsociarRetoState.evento_dinamico,
                rx.grid(
                    select_catalog("Modo de reto", "Seleccionar...", AsociarRetoState.modos, AsociarRetoState.set_id_modo_puntaje, AsociarRetoState.id_modo_puntaje, AsociarRetoState.override),
                    input_box("Punataje inicial", AsociarRetoState.inicial_def.to_string(), AsociarRetoState.inicial_def, AsociarRetoState.set_puntaje_inicial, "number", AsociarRetoState.override),
                    rx.cond(
                        AsociarRetoState.reto_dinamico,
                        input_box("Punataje minimo", rx.cond(AsociarRetoState.minimo_def, AsociarRetoState.minimo_def.to_string(), "0"), AsociarRetoState.minimo_def, AsociarRetoState.set_puntaje_minimo, "number", AsociarRetoState.override),
                    ),
                    width="80%",
                    spacing="2",
                ),
                rx.grid(
                    rx.text("Estatico por modo de evento", size="2", weight="regular"),
                    input_box("Punataje inicial", AsociarRetoState.inicial_def.to_string(), AsociarRetoState.inicial_def, AsociarRetoState.set_puntaje_inicial, "number", AsociarRetoState.override),
                    width="80%",
                    spacing="2",
                ),
            ),
            place_items="center",
            width="100%",
        ),
        spacing="3",
        width="100%",
    )


def dialog_override(reto: dict) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon("plus", size=20),
                "Agregar",
                size="1",
                variant="surface",
                color_scheme="jade",
                on_click=lambda: AsociarRetoState.open_dialog(reto['id_reto'], reto['titulo'], reto['id_modo_puntaje'].to_string(), reto['puntaje_inicial'], reto['puntaje_minimo'])
            ),
        ),
        rx.dialog.content(
            rx.grid(
                override_content(reto['modo'], reto['puntaje_inicial'], reto['puntaje_minimo']),
                rx.flex(
                    button("Confirmar", "jade", [AsociarRetoState.confirmar_agregar], size="2"),
                    button("Cancelar", "ruby", [AsociarRetoState.close_dialog], size="2"),
                    justify="end",
                    spacing="3",
                    width="100%",
                ),
                width="100%",
                spacing="3",
            ),
            max_width="400px",
        ),
        open=AsociarRetoState.dialog_bool,
    )


def accion_candidato(reto: dict) -> rx.Component:
    return rx.cond(
        AsociarRetoState.ids_in_carrito.contains(reto['id_reto']),
        rx.badge(rx.icon("check", size=20), "Agregado", color_scheme="gray", variant="surface"),
        dialog_override(reto),
    )


def fila_candidato(reto: dict) -> rx.Component:
    return rx.card(
        rx.tablet_and_desktop(
            rx.grid(
                rx.text(reto['titulo'], size="2", weight="medium"),
                rx.text(f"{reto['puntaje_inicial']} pts.", size="2", weight="regular"),
                rx.text(
                    rx.cond(
                        reto['puntaje_minimo'],
                        f"{reto['puntaje_minimo']} pts.",
                        "---",
                    ),
                    size="2", weight="regular",
                ),
                rx.text(reto['categoria'], size="2", weight="regular"),
                rx.text(reto['dificultad'], size="2", weight="regular"),
                rx.text(reto['modo'], size="2", weight="regular"),
                accion_candidato(reto),
                place_items="center",
                columns="7",
                width="100%",
            ),
            width="100%",
        ),
        rx.mobile_only(
            rx.flex(
                rx.text(reto['titulo'], size="2", weight="medium"),
                accion_candidato(reto),
                justify="between",
                width="100%",
            ),
        ),
        width="100%",
    )


def item_carrito(item: dict) -> rx.Component:
    return rx.grid(
        rx.text(item['titulo'], size="2", weight="light", color_scheme="gray", align="center"),
        rx.text(
            rx.cond(
                item['puntaje_minimo'],
                f"{item['puntaje_inicial']}.pts {item['puntaje_inicial']}.pts",
                f"{item['puntaje_inicial']}.pts ---",
            ),
            size="2", weight="regular"
        ),
        rx.text(item['modo'], size="2", weight="light", color_scheme="gray", align="center"),
        button("Quitar", "red", [lambda: AsociarRetoState.quitar_carrito(item['id'])], size="1"),
        place_items="center",
        columns="4",
        width="100%",
        spacing="2",
    )


def card_carrito() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.text("Asociar", size="3", weight="medium"),
            rx.divider(),
            rx.cond(
                AsociarRetoState.carrito != [],
                rx.foreach(AsociarRetoState.carrito, item_carrito),
                rx.spacer(),
            ),
            select_catalog("Evento destino", "Seleccionar...", AsociarRetoState.eventos_dest, AsociarRetoState.set_id_evento_dest),
            rx.grid(
                button("Asociar", "jade", AsociarRetoState.guardar_carrito, size="2"),
                button("Vaciar", "ruby", AsociarRetoState.vaciar_carrito, size="2"),
                columns="2",
                width="100%",
                spacing="2",
            ),
        ),
        width="100%",
        spacing="3",
    )


def retos_evento_destino(reto: dict) -> rx.Component:
    return rx.box(
        rx.grid(
            rx.text(reto['titulo'], size="1", weight="light"),
            rx.text(reto['categoria'], size="1", weight="light"),
            rx.text(reto['dificultad'], size="1", weight="light"),
            rx.text(
                rx.cond(
                    reto['puntaje_minimo'],
                    f"{reto['puntaje_inicial']}.pts {reto['puntaje_minimo']}.pts",
                    f"{reto['puntaje_inicial']}.pts ---",
                ),
                size="1", weight="light", align="center",
            ),
            rx.text(reto['modo'], size="1", weight="light"),
            place_items="center",
            columns="5",
            width="100%",
            padding=".4em",
        ),
        border_bottom="1px solid gray",
        padding=".4em",
        width="100%",
    )


def card_retos_evento_destino() -> rx.Component:
    return rx.card(
        rx.text("Retos de evento", size="3", weight="medium"),
        rx.grid(
            rx.text("Titulo", size="1", weight="medium"),
            rx.text("Categoria", size="1", weight="medium"),
            rx.text("Dificultad", size="1", weight="medium"),
            rx.text("Puntaje", size="1", weight="medium"),
            rx.text("Modo", size="1", weight="medium"),
            padding=".4em",
            place_items="center",
            columns="5",
            width="100%",
            spacing="2",
        ),
        rx.foreach(AsociarRetoState.prev_retos, retos_evento_destino),
        width="100%",
    )


def filtros() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Asociar retos en eventos", size="4"),
            rx.grid(
                input_box("Buscar por titulo", "Titutlo...", AsociarRetoState.busqueda, AsociarRetoState.set_busqueda, "text"),
                select_catalog("Categorias", "Seleccionar...", AsociarRetoState.categorias, AsociarRetoState.set_id_categoria_filtro),
                select_catalog("Dificultad", "Seleccionar...", AsociarRetoState.dificultades, AsociarRetoState.set_id_dificultad_filtro),
                select_catalog("Modo puntaje", "Seleccionar...", AsociarRetoState.modos, AsociarRetoState.set_id_modo_filtro),
                checked("Aislados", AsociarRetoState.aislados_bool, AsociarRetoState.set_aislados_bool),   
                place_items="center",
                grid_template_columns="30% 1fr 1fr 1fr 1fr",
                columns={"base": "1", "md": "5"},
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
                AsociarRetoState.id_evento_dest != "",
                rx.foreach(AsociarRetoState.candidatos, fila_candidato),
                rx.text("seleccione evento de destino", color_scheme="gray", size="2"),
            ),
            spacing="3",
        ),
        width="100%",
    )


def asociar_reto_view() -> rx.Component:
    return rx.grid(
        rx.vstack(
            filtros(),
            contenido(),
            spacing="5",
            width="100%",
        ),
        rx.vstack(
            card_carrito(),
            card_retos_evento_destino(),
            spacing="5",
            width="100%",
        ),
        grid_template_columns=rx.breakpoints(initial="1fr", md="75% 1fr"),
        width=rx.breakpoints(sm="95%", md="80%"),
        spacing="4",
    )
