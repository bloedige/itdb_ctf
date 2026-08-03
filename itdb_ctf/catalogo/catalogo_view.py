import reflex as rx 
from itdb_ctf.catalogo.catalogo_states import CatalogoState, EnvioFlagState

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

def reto_trigger(reto:dict) -> rx.Component:
    return rx.card(
        rx.grid(
            rx.text(reto['titulo'],size="3", weight="medium",
            color=rx.cond(reto['resuelto'],"#00FFC3FF",""),
            ),
            rx.text(f"{reto['puntaje']} pts.",size="2", weight="regular",
            color=rx.cond(reto['resuelto'],"#00FFC3FF",""),
            ),
            height="10vh",
            width="100%",
            place_items="center",    
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
        rx.dialog.description(reto['descripcion'], width="100%",),
        rx.flex(
            rx.text(f"by: {reto['creador']}", size="1", color="gray"),
            justify="end",
            width="100%",
        ),
        rx.cond(
            reto['original'] != None,
            rx.link(
                    rx.grid(
                        rx.icon("file_down", stroke_width=1.5 , size=15),
                        rx.text(reto['original'], size="1", weight="light"),
                        grid_template_columns="10% 1fr",
                        spacing="2", 
                    ),
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
        ),
        rx.dialog.content(
            reto_content(reto),
            max_width="50vh",
        ),
        on_open_change=EnvioFlagState.drop_flag,     
    )

def catalogo_view()->rx.Component:
     return rx.vstack(
        filtros_view(),
        rx.vstack(
            rx.grid(
                rx.foreach(CatalogoState.retos,reto_card_view),
                columns={"base":"1", "md":"5"},
                spacing="4",
                width="70%",
                place_items="center"
            ),
        align="center",
        width="100%"
        ),
        spacing="5",
        width="100%",
    )