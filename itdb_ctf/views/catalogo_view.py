import reflex as rx 
from itdb_ctf.states.catalogo_states import CatalogoState
from itdb_ctf.views.card_reto_view import reto_card_view
from itdb_ctf.views.filtros_view import filtros_view

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
