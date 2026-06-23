import reflex as rx
from itdb_ctf.states.catalogo_states import CatalogoState

def chip(texto:str,valor:str,filtro_actual,on_click)->rx.Component:
    return rx.button(
        texto,
        on_click=lambda:on_click(valor),
        variant=rx.cond(filtro_actual==valor,"solid","outline"),
        size="2",
    )

def filtro_categoria_view()->rx.Component:
    return rx.vstack(
        rx.text("Categoría",size="1",weight="bold"),
        rx.flex(
            chip("Todos","",CatalogoState.filtro_categoria,CatalogoState.filtrar_categoria),
            rx.foreach(
                CatalogoState.cat_opciones,
                lambda par: chip(par[1],par[0],CatalogoState.filtro_categoria,CatalogoState.filtrar_categoria),
            ),
            wrap="wrap", spacing="2",
        ),
        spacing="2",
        width="100%",
    )

def filtro_dificultad_view()->rx.Component:
    return rx.vstack(
        rx.text("Dificultad",size="1",weight="bold"),
        rx.flex(
            chip("Todos","",CatalogoState.filtro_dificultad,CatalogoState.filtrar_dificultad),
            rx.foreach(
                CatalogoState.dif_opciones,
                lambda par: chip(par[1],par[0],CatalogoState.filtro_dificultad,CatalogoState.filtrar_dificultad),
            ),
            wrap="wrap", spacing="1",
        ),

        spacing="2",
        width="100%",
    )

def filtros_view()->rx.Component:
    return rx.vstack(
            filtro_categoria_view(),
            filtro_dificultad_view(),
    )