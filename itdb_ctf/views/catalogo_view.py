import reflex as rx 
from itdb_ctf.states.catalogo_states import CatalogoState
from itdb_ctf.views.filtros_view import filtros_view
from itdb_ctf.states.catalogo_states import EnvioFlagState


#def cad_trigger() -> rx.Component:
#    return 



def reto_card_view(reto: dict)->rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.card(
                rx.center(
                    rx.grid(
                        rx.text(reto['titulo'],size="3", weight="medium", align="center", width="100%",
                        color=rx.cond(reto['resuelto'],"#00FFC3FF",""),
                        ),
                        rx.text(f"{reto['puntaje']} pts.",size="2", weight="regular", align="center", width="100%",
                        color=rx.cond(reto['resuelto'],"#00FFC3FF",""),
                        ), 
                        spacing="2",
                    ),
                    
                ),
                width="150px",
                bg=rx.cond(reto['resuelto'],"#29A38736",""),
            )
        ),
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.badge(reto['categoria'], variant="surface", color_scheme="jade"),
                    rx.badge(reto['dificultad'],variant="surface", color_scheme="jade"),
                    rx.spacer(),
                    width="100%",
                ),
                rx.divider(),
                rx.dialog.title(reto['titulo']),
                rx.text(f"{reto['puntaje']} pts.",size="3", weight="medium", width="100%"),
                rx.divider(),
                rx.dialog.description(reto['descripcion'], width="100%",),
                rx.hstack(
                    rx.spacer(),
                    rx.text(f"by: {reto['creador']}", size="1", color="gray"),
                width="100%",
                ),
                rx.cond(
                    reto['original'] != None,
                    rx.link(rx.callout(reto['original'], icon="file_down", color_scheme="jade"),href=f"http://localhost:8000/api/reto/{reto['id']}/descarga",text_decoration="none"),
                ),
                rx.cond(
                        reto['resultado'] & reto['resuelto'],
                        rx.callout(reto['resultado'], icon="smile"),
                        rx.callout(reto['resultado'], icon="angry"),
                    ),  
                rx.hstack(
                    rx.input(
                        placeholder="flag{...}",
                        on_change=lambda v :EnvioFlagState.set_flag(reto['id'], v),
                    ),
                    rx.button(
                        "Enviar",
                        on_click=lambda:EnvioFlagState.enviar(reto['id']),
                    ),
                    width="100%",
                    # --- resultado de el envio 
                    
                ),
                spacing="3",
                width="100%",
            ),
        ),      
    )

def catalogo_view()->rx.Component:
     return rx.vstack(
        filtros_view(),
        rx.heading("Retos"),
        rx.vstack(
        
            rx.flex(
                rx.foreach(CatalogoState.retos,reto_card_view),
                flex_wrap="wrap",
                spacing="4",
                direction="row",
                width="80%",
                align="center"
            ),
        align="center",
        width="100%"
        ),
        width="95%"
    )