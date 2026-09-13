import reflex as rx 
from itdb_ctf.catalogo.catalogo_states import CatalogoState, EnvioFlagState, listarPistaState
from itdb_ctf.components.form import button

def chip(texto:str,valor:str,filtro_actual,on_click)->rx.Component:
    return rx.button(
        texto,
        on_click=on_click(valor),
        variant=rx.cond(filtro_actual==valor,"solid","outline"),
        size="2",
        color_scheme="jade",
    )

def filtro_categoria_view()->rx.Component:
    return rx.vstack(
        rx.text("Categoría",size="1",weight="medium"),
        rx.flex(
            rx.foreach(
                CatalogoState.categorias,
                lambda par: chip(par[1],par[0],CatalogoState.id_categoria_filtro,CatalogoState.set_id_categoria_filtro),
            ),
            wrap="wrap", spacing="2",
        ),
        spacing="2",
        width="100%",
    )

def filtro_dificultad_view()->rx.Component:
    return rx.vstack(
        rx.text("Dificultad",size="1",weight="medium"),
        rx.flex(
            rx.foreach(
                CatalogoState.dificultades,
                lambda par: chip(par[1],par[0],CatalogoState.id_dificultad_filtro,CatalogoState.set_id_dificultad_filtro),
            ),
            wrap="wrap", spacing="2",
        ),
        spacing="2",
        width="100%",
    )

def filtros_view()->rx.Component:
    return rx.vstack(
        filtro_categoria_view(),
        filtro_dificultad_view(),
        width="100%",
        spacing="5",
    )


def pista_trigger(pista:dict) -> rx.Component:
    return rx.button(
        rx.grid(
            rx.text(f"Pista {pista['costo']} pts.", weight="regular", size="2"),
            place_items="center",
            width="100%",
        ),
        width="100%",
        bg=rx.cond(pista['adquirido'], "#00FFC350", "#B3B3B350"),
    )

def pista_content(pista:dict) -> rx.Component:
    return rx.cond(
        pista['adquirido'],
        rx.grid(
            rx.text(f"Pista {pista['costo']} pts.", weight="bold", size="3"),
            rx.text(pista['descripcion'], weight="regular", width="100%", size="2"),
            spacing="3",
            place_items="center",
            width="100%",
        ),
        rx.grid(
            rx.text(f"Pista {pista['costo']} pts.", weight="bold", size="3"),
            rx.text("¿Desea adquirir la pista?", weight="regular", width="100%", size="2"),
            spacing="3",
            place_items="center",
            width="100%",
        )
    )

def dialog_pista(pista:dict) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            pista_trigger(pista),
        ),
        rx.dialog.content(
            pista_content(pista),
            rx.cond(
                ~pista['adquirido'],
                rx.flex(
                    rx.dialog.close(button("Cancelar", "gray", [], size="2")),
                    button("confirmar", "jade", [lambda: listarPistaState.comprar_pista(pista['id_reto'],pista['id_pista'])], size="2"),
                    spacing="3",
                    justify="end",
                ),
            ),
            max_width="45vh"
        )
    )

def reto_trigger(reto:dict) -> rx.Component:
    return rx.card(
        rx.flex(
            rx.text(reto['titulo'],size="3", weight="medium",
            color=rx.cond(reto['resuelto'],"#00FFC3FF",""),
            ),
            rx.text(f"{reto['puntaje']} pts.",size="2", weight="regular",
            color=rx.cond(reto['resuelto'],"#00FFC3FF",""),
            ),
            align="center",
            justify="center",
            direction="column",
            height="12vh",
            width="100%",
        ),
        rx.text(f"by. {reto['creador']}",size="1", weight="light",
            color=rx.cond(reto['resuelto'],"#00FFC3FF",""),
            position="absolute",
            right="1em",
            bottom="1em",
            
        ),
        width="100%",
        bg=rx.cond(reto['resuelto'],"#00FFC350",""),
    )

def reto_content(reto:dict) -> rx.Component:
    return rx.vstack(
        rx.flex(
            rx.badge(reto['categoria'], variant="surface", color_scheme="jade", size="1"),
            rx.badge(reto['dificultad'], variant="surface", color_scheme="jade", size="1"),
            justify="end",
            spacing="2",
            width="100%",
        ),
        rx.divider(),
        rx.grid(
            rx.text(reto['titulo'], weight="bold", size="3" ),
            rx.text(f"{reto['puntaje']} pts.", size="2", weight="medium"),
            place_items="center",
            width="100%",
        ),
        rx.divider(),
        rx.text(reto['descripcion'],weight="regular", width="100%",),
        rx.flex(
            rx.text(f"by: {reto['creador']}", size="1", color="gray"),
            justify="end",
            width="100%",
        ),
        rx.foreach(listarPistaState.pistas, dialog_pista),
        rx.cond(
            reto['original'] != None,
            rx.link(
                    rx.grid(
                        rx.icon("file_down", stroke_width=1.5 , size=15),
                        rx.text(reto['original'], size="2", weight="light", 
                            style={
                                "whiteSpace": "nowrap",
                                "overflow": "hidden",
                                "textOverflow": "ellipsis",
                            },
                        ),
                        grid_template_columns="10% 1fr",
                        spacing="2", 
                    ),
                max_width="30%",
                border="1px solid",
                border_radius=".3em",
                padding=".3em",
                bg="#049BFF3E",
                href=f"http://localhost:8000/api/reto/{reto['id_reto']}/descarga",text_decoration="none"
            ),
        ),
        rx.divider(),
        rx.hstack(
            rx.input(
                placeholder="flag{...}",
                on_change=EnvioFlagState.set_flag,
                width="100%",
                auto_focus=True,
            ),
            rx.button(
                "Enviar",
                on_click=lambda:EnvioFlagState.enviar_flag(reto['id_reto']),
            ),
            spacing="3",
            width="100%",   
        ),
        spacing="3",
        width="100%",
    )

def reto_card_view(reto:dict)->rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            reto_trigger(reto),
            on_click=lambda:listarPistaState.cargar_pistas(reto['id_reto']),
        ),
        rx.dialog.content(
            reto_content(reto),
            max_width="50vh",
        ),
        on_open_change=EnvioFlagState.drop_flag,     
    )

def catalogo_view()->rx.Component:
     return rx.vstack( 
        rx.heading("Catalogo de retos",size="5"),
        filtros_view(),
        rx.grid(
            rx.foreach(CatalogoState.retos,reto_card_view),
            columns={"base":"1", "md":"4"},
            spacing="4",
            width="100%",
            place_items="center"
        ),
        width="60%",
    )