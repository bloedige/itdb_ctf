import reflex as rx
from itdb_ctf.asociar.asociar_state import AsociarState, EditarAsociarState
from itdb_ctf.components.form import input_box, button, select_catalog, checked

def override_content(modo, inicial, minimo) -> rx.Component:
    return rx.vstack(
        rx.text(AsociarState.titulo_dialog, size="3", weight="medium"),
        rx.text("Valores por defecto", size="2",weight="regular"),
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
                rx.text(rx.cond(minimo,minimo,"---"), size="1", weight="light"),
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
                on_change=AsociarState.set_override_mode,
            ),
            width="100%",
        ),
        rx.grid(
            rx.cond(
                AsociarState.evento_dinamico,
                rx.grid(
                    select_catalog("Modo de reto","Seleccionar...", AsociarState.modos, AsociarState.set_id_modo_puntaje, AsociarState.id_modo_puntaje, AsociarState.override),
                    input_box("Punataje inicial", AsociarState.inicial_def.to_string(), AsociarState.inicial_def, AsociarState.set_puntaje_inicial, "number", AsociarState.override),
                    rx.cond(
                        AsociarState.reto_dinamico,
                        input_box("Punataje minimo", rx.cond(AsociarState.minimo_def, AsociarState.minimo_def.to_string(), "0"), AsociarState.minimo_def, AsociarState.set_puntaje_minimo, "number", AsociarState.override),
                    ),
                    width="80%",
                    spacing="2",
                ),
                rx.grid(
                    rx.text("Estatico por modo de evento", size="2", weight="regular"),
                    input_box("Punataje inicial", AsociarState.inicial_def.to_string(), AsociarState.inicial_def, AsociarState.set_puntaje_inicial, "number", AsociarState.override),
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

def dialog_override(reto:dict) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon("plus", size=20),
                "Agregar",
                size="1",
                variant="surface",
                color_scheme="jade",
                on_click=lambda: AsociarState.open_dialog(reto['id_reto'], reto['titulo'], reto['id_modo_puntaje'].to_string(), reto['puntaje_inicial'], reto['puntaje_minimo'])
            ),
        ),
        rx.dialog.content(
            rx.grid(
                override_content(reto['modo'], reto['puntaje_inicial'], reto['puntaje_minimo']),
                rx.flex(
                    button("Confirmar", "jade", [AsociarState.confirmar_agregar], size="2"),
                    button("Cancelar", "ruby", [AsociarState.close_dialog], size="2"),
                    justify="end",
                    spacing="3",
                    width="100%",
                ),
                width="100%",
                spacing="3",
            ),
            max_width="400px",
        ),
        open=AsociarState.dialog_bool,  
    )

def edit_content() -> rx.Component:
    return rx.vstack(
        rx.text(EditarAsociarState.titulo_edit, size="3", weight="medium"),
        rx.grid(
            rx.cond(
                EditarAsociarState.evento_edit_dinamico,
                rx.grid(
                    select_catalog("Modo de reto", "seleccionar...", AsociarState.modos, EditarAsociarState.set_id_modo_edit, EditarAsociarState.id_modo_edit),
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

def dialog_edit(item:dict) -> rx.Component:
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


def fila_candidato(reto:dict) -> rx.Component:
    return rx.card(
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
            rx.cond(
                AsociarState.ids_in_carrito.contains(reto['id_reto']),
                rx.badge(rx.icon("check", size=20), "Agregado", color_scheme="gray", variant="surface"),
                dialog_override(reto), 
            ),
            place_items="center",
            columns="7",
            width="100%",
        ),
        width="100%",
    )

def item_carrito(item:dict) -> rx.Component:
    return rx.grid(
        rx.text(item['titulo'], size="2", weight="light", color_scheme="gray" , align="center"),
        rx.text(
            rx.cond(
                item['puntaje_minimo'],
                f"{item['puntaje_inicial']}.pts {item['puntaje_inicial']}.pts",
                f"{item['puntaje_inicial']}.pts ---",
            ),
            size="2", weight="regular"
        ),  
        rx.text(item['modo'], size="2", weight="light", color_scheme="gray" , align="center"),
        button("Quitar", "red", [lambda:AsociarState.quitar_carrito(item['id'])], size="1"),
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
                AsociarState.carrito != [],
                rx.foreach(AsociarState.carrito, item_carrito),
                rx.spacer(),   
                ),
            select_catalog("Evento destino", "Seleccionar...", AsociarState.eventos_dest, AsociarState.set_id_evento_dest),
            rx.grid(
                button("Asociar", "jade", AsociarState.guardar_carrito, size="2"),
                button("Vaciar", "ruby", AsociarState.vaciar_carrito, size="2"),
                columns="2",
                width="100%",
                spacing="2",
            ),   
        ),
        width="100%",
        spacing="3", 
        pointer_events=rx.cond(AsociarState.modo, "none", "auto"),
        opacity=rx.cond(AsociarState.modo, ".5", "1"),
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
                    button("Quitar", "red", [lambda:AsociarState.quitar_retos(id_reto)], size="2"),
                ),
                justify="end",
                spacing="2",
                width="100%",
            ),
            spacing="2",
            width="100%",
        ),
    )

def fila_gestion(reto:dict) -> rx.Component:
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

def retos_evento_destino(reto:dict) -> rx.Component:
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
        rx.foreach(AsociarState.prev_retos, retos_evento_destino),
        width="100%",
        pointer_events=rx.cond(AsociarState.modo, "none", "auto"),
        opacity=rx.cond(AsociarState.modo, ".5", "1"),
    )

def filtros() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Asociar / Gestionar retos en eventos", size="4"), 
            rx.tabs.root(
                rx.tabs.list(
                    rx.tabs.trigger(
                        rx.text("Asociar", weight="medium", size="2"), 
                        value="asociar", 
                        width="50%",
                        color_scheme="jade",
                    ),
                    rx.tabs.trigger(
                        rx.text("Gestionar", weight="medium", size="2"), 
                        value="gestionar",
                        width="50%",
                        color_scheme="jade",
                    ),
                ),
                value=AsociarState.tab,
                on_change=AsociarState.set_tab,
                width="100%",
            ),
            rx.cond(
                AsociarState.modo,
                rx.grid(
                    select_catalog("Eventos (en curso / futuro)","Seleccionar...", AsociarState.eventos_gest, AsociarState.set_id_evento_gest),
                    rx.grid(
                        input_box("Buscar por titulo", "Titutlo...", AsociarState.busqueda_gest, AsociarState.set_busqueda_gest, "text"),
                        select_catalog("Categorias", "Seleccionar...", AsociarState.categorias, AsociarState.set_id_categoria_gest_filtro, AsociarState.id_categoria_gest_filtro),
                        select_catalog("Dificultad", "Seleccionar...", AsociarState.dificultades, AsociarState.set_id_dificultad_gest_filtro, AsociarState.id_dificultad_gest_filtro),
                        select_catalog("Modo puntaje", "Seleccionar...", AsociarState.modos, AsociarState.set_id_modo_gest_filtro, AsociarState.id_modo_gest_filtro),
                        place_items="center",
                        grid_template_columns="30% 1fr 1fr 1fr",
                        columns={"base":"1", "md":"4"},
                        spacing="2", 
                        width="100%", 
                    ),
                    place_items="center",
                    spacing="2", 
                    width="100%",
                ),
                rx.grid(
                    input_box("Buscar por titulo", "Titutlo...", AsociarState.busqueda, AsociarState.set_busqueda, "text"),
                    select_catalog("Categorias", "Seleccionar...", AsociarState.categorias, AsociarState.set_id_categoria_filtro),
                    select_catalog("Dificultad", "Seleccionar...", AsociarState.dificultades, AsociarState.set_id_dificultad_filtro),
                    select_catalog("Modo puntaje", "Seleccionar...", AsociarState.modos, AsociarState.set_id_modo_filtro),
                    checked("Aislados", AsociarState.aislados_bool, AsociarState.set_aislados_bool),
                    place_items="center",
                    grid_template_columns="30% 1fr 1fr 1fr 1fr",
                    columns={"base":"1", "md":"5"},
                    spacing="2", 
                    width="100%",   
                ),
            ),
            spacin="5",
            width="100%",
        ),
        width="100%",
    )

def contenido() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.cond(
                AsociarState.modo, 
                rx.cond(
                    AsociarState.id_evento_gest != "",
                    rx.foreach(AsociarState.retos_gest, fila_gestion),
                    rx.text("seleccione evento a gestionar", color_scheme="gray", size="2")
                ),
                rx.cond(
                    AsociarState.id_evento_dest != "",
                    rx.foreach(AsociarState.candidatos, fila_candidato),
                    rx.text("seleccione evento de destino", color_scheme="gray", size="2")
                ),
                
            ),
            spacing="3",
        ),
        width="100%",
    )

def asociar_view()-> rx.Component:
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
            width="100%"
        ),
        grid_template_columns="75% 1fr",
        width="100%", 
        spacing="5",
    )