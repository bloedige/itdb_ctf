import reflex as rx
from itdb_ctf.components.navbar import navbar_cerrado
from itdb_ctf.evento_cerrado.evento_cerrado_informacion_view import evento_cerrado_informacion_view
from itdb_ctf.evento_cerrado.evento_cerrado_informacion_state import EventoCerradoInfromacionState
from itdb_ctf.evento_cerrado.evento_cerrado_acceso_state import EventoCerradoAccesoState
from itdb_ctf.evento_cerrado.evento_cerrado_acceso_view import con_acceso

def evento_cerrado_informacion_page() -> rx.Component:
    return rx.vstack(
        navbar_cerrado(EventoCerradoInfromacionState.id_cerrado),
        con_acceso(evento_cerrado_informacion_view()),
        width="100%",
        on_mount=[EventoCerradoAccesoState.escuchar_acceso, EventoCerradoInfromacionState.escuchar_info_cerrado],
        on_unmount=[EventoCerradoAccesoState.parar_acceso, EventoCerradoInfromacionState.parar_info_cerrado],
    )
