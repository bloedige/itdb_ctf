import reflex as rx 
from itdb_ctf.states.catalogo_states import CatalogoState
from itdb_ctf.views.card_reto_view import reto_card_view
from itdb_ctf.views.filtros_view import filtros_view
from itdb_ctf.states.catalogo_states import EnvioFlagState

def reto_card_view(reto: dict)->rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.card(
            rx.vstack(
                rx.heading(reto['titulo'],size="4"),
                rx.cond(
                    reto['resuelto'],
                   rx.badge("Resuelto",color_scheme="green"), 
                ),
                rx.hstack(
                    rx.badge(reto['categoria']),
                    rx.badge(reto['dificultad']),
                ),
                rx.text(f"{reto['puntaje']} pts."),
                rx.text(f"by: {reto['creador']}.", size="1", color="gray"),
                spacing="2",
            ),
        ),
        ),
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.badge(reto['categoria']),
                    rx.badge(reto['dificultad']),
                    rx.spacer(),
                    rx.dialog.close(rx.button(rx.icon("x"),size="1")),
                ),
                rx.divider(),
                rx.dialog.title(reto['titulo']),
                rx.dialog.title(f"{reto['puntaje']} pts."),
                rx.divider(),
                rx.dialog.description(reto['descripcion']),
                rx.cond(
                    reto['original'] != None,
                    rx.link(reto['original'],href=f"http://localhost:8000/api/reto/{reto['id']}/descarga"),
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

                    # --- resultado de el envio 
                    rx.cond(
                        reto['resultado'],
                        rx.text(reto['resultado'])
                    ),
                ),
                spacing="3"
            ),
        ),      
    )

def catalogo_view()->rx.Component:
    return rx.vstack(

        rx.text("Retos"),
        filtros_view(),
        rx.flex(
            rx.foreach(CatalogoState.retos,reto_card_view),
            wap="wrap",
            pacing="3",
        ),
        spacing="3",
        width="100%",   
    )
