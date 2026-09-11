import reflex as rx
from itdb_ctf.components.navbar import navbar_cerrado
from itdb_ctf.evento_cerrado.evento_cerrado_reto_view import evento_cerrado_retos_view
from itdb_ctf.evento_cerrado.evento_cerrado_reto_state import EventoCerradoRetoState, EventoCerradoListarPistaState
from itdb_ctf.evento_cerrado.evento_cerrado_informacion_state import EventoCerradoInfromacionState
from itdb_ctf.evento_cerrado.evento_cerrado_acceso_state import EventoCerradoAccesoState
from itdb_ctf.evento_cerrado.evento_cerrado_acceso_view import con_acceso

def evento_cerrado_reto_page() -> rx.Component:
    return rx.grid(
        navbar_cerrado(EventoCerradoInfromacionState.id_cerrado),
        con_acceso(evento_cerrado_retos_view()),
        width="100%",
        justify_items="center",
        on_mount=[
            EventoCerradoAccesoState.escuchar_acceso,
            EventoCerradoRetoState.escuchar_retos,
            EventoCerradoListarPistaState.escuchar_pistas_cerrado,
        ],
        on_unmount=[
            EventoCerradoAccesoState.parar_acceso,
            EventoCerradoRetoState.parar_retos,
            EventoCerradoListarPistaState.parar_pistas_cerrado,
        ],
    )
