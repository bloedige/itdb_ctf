import reflex as rx
from itdb_ctf.states.asociar_state import AsociarState
from itdb_ctf.components.form import input_box, button, select_catalog, checked

def override_content() -> rx.Component:
    return rx.vstack(
        rx.grid(
            rx.tabs.root(
                rx.tabs.list(
                    rx.tabs.trigger("Default", value="def"),
                    rx.tabs.trigger("Override", value="ove"),
                ),
                default_value="def",
                on_change=AsociarState.set_override_mode,
            ),
        ),
        rx.text(AsociarState.titulo_dialog, size="3", weight="medium"),
        input_box("Puntaje override", f"{AsociarState.pts_init_dialog} pts.", AsociarState.override_valor, AsociarState.set_override_valor , "number", AsociarState.override),
        spacing="3",
        width="100%",
    )

def dialog_override(reto:dict) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                rx.icon("plus"),
                "Agregar",
                size="1",
                variant="surface",
                color_scheme="jade",
                on_click=lambda: AsociarState.open_dialog(reto['id_reto'],reto['titulo'], reto['puntaje_inicial'])
            ),
        ),
        rx.dialog.content(
            rx.grid(
                override_content(),
                rx.hstack(
                rx.spacer(),
                    rx.dialog.close(button("Confirmar", "green", [AsociarState.confirmar_agregar,])),
                    rx.dialog.close(button("Cancelar", "red", [])),
                    width="100%",
                ),
                width="100%",
                spacing="3",
            ),
            max_width="400px",
        ),  
    )

def fila_candidato(reto:dict) -> rx.Component:
    return rx.card(
        rx.grid(
            rx.text(reto['titulo'], size="2", weight="medium"),
            rx.text(f"{reto['puntaje_inicial']} pts.", size="2", weight="regular"),
            rx.text(reto['categoria'], size="2", weight="regular"),
            rx.cond(
                AsociarState.ids_in_carrito.contains(reto['id_reto']),
                rx.badge(rx.icon("check"), "Agregado", color_scheme="gray", variant="surface"),
                dialog_override(reto), 
            ),
            place_items="center",
            columns="4",
            width="100%",
        ),
        width="100%",
    )

def item_carrito(item:dict) -> rx.Component:
    return rx.grid(
        rx.text(item['titulo'], size="1", weight="light", color_scheme="gray" , align="center"),
        rx.cond(
            item['override'] != None,
            rx.text(f"{item['override']} pts. (Override)", size="2", weight="light", color_scheme="gray"),
            rx.text(f"{item['default']} pts. (Default)", size="2", weight="light", color_scheme="gray"),
        ),
        button("Quitar", "red", [lambda: AsociarState.quitar_carrito(item['id'])], size="1"),
        place_items="center",
        columns="3",
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
        rx.divider(),
        rx.grid(
            button("Asociar", "jade", AsociarState.guardar_carrito, size="2", disabled=AsociarState.activar_asociar),
            button("Vaciar", "ruby", AsociarState.vaciar_carrito, size="2"),
            columns="2",
            width="100%",
            spacing="2",
        ),
        select_catalog("Evento destino", "Seleccionar", AsociarState.eventos_dest, AsociarState.set_id_evento_dest),
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
            #rx.button("Quitar", color_scheme="red", variant="surface", size="2")
        ),
        rx.alert_dialog.content(
            rx.alert_dialog.title("Quitar reto del evento"),
            rx.alert_dialog.description(f"¿Seguro que quieres quitar '{titulo}' de este evento?"),
            rx.hstack(
                rx.spacer(),
                rx.alert_dialog.cancel(
                    button("Cancelar", "gray", [], size="2"),
                    #x.button("Cancelar", color_scheme="gray", variant="surface", size="2")
                ),
                rx.alert_dialog.action(
                    button("Quitar", "red", [AsociarState.quitar_retos(id_reto)], size="2"),
                    #rx.button("Quitar", on_click=lambda:AsociarState.quitar_retos(id_reto), color_scheme="red", variant="surface", size="2")
                ),
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
            rx.text(reto['categoria'], size="2", weight="regular"),
            alert_dialog(reto['id'], reto['titulo']),
            columns="4",
            place_items="center",
            width="100%",   
        ), 
        width="100%",
    )

def retos_evento_destino(reto:dict)->rx.Component:
    return rx.box(
        rx.grid(
            rx.text(reto['titulo'], size="1", weight="light"),
            rx.text(reto['categoria'], size="1", weight="light"),
            rx.text(f"{reto['puntaje_inicial']} pts.", size="1", weight="light"),
            rx.cond(
                reto['override'] != None,
                rx.text(f"{reto['override']} pts.", size="1", weight="light"),
                rx.text("---", size="1", weight="light"),
            ),
            place_items="center",
            columns="4",
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
            rx.text("Default", size="1", weight="medium"),
            rx.text("Override", size="1", weight="medium"),
            padding=".4em",
            place_items="center",
            columns="4",
            width="100%",
            spacing="2",
        ),
        rx.foreach(AsociarState.retos_dest, retos_evento_destino),
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
                    ),
                    rx.tabs.trigger(
                        rx.text("Gestionar", weight="medium", size="2"), 
                        value="gestionar",
                        width="50%",
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
                    place_items="center",
                    spacing="2", 
                    width="40%",
                ),
                rx.grid(
                    select_catalog("Categorias", "Seleccionar...", AsociarState.categorias, AsociarState.set_id_categoria_filtro),
                    select_catalog("Dificultad", "Seleccionar...", AsociarState.dificultades, AsociarState.set_id_dificultad_filtro),
                    select_catalog("Modo puntaje", "Seleccionar...", AsociarState.modos, AsociarState.set_id_modo_filtro),
                    checked("Aislados", AsociarState.aislados_bool, AsociarState.set_aislados_bool),
                    place_items="center",
                    columns={"base":"1","md":"4"},
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
                    rx.text("seleccione evento a gestionar", color_scheme="gray", size="2", text_aling="center")
                ),
                rx.foreach(AsociarState.candidatos, fila_candidato)
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