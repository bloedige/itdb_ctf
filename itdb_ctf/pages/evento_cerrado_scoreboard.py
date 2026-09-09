import reflex as rx
from itdb_ctf.components.navbar import navbar_cerrado
from itdb_ctf.evento_cerrado.evento_cerrado_scoreboard_view import evento_cerrado_scoreboard_view
from itdb_ctf.evento_cerrado.evento_cerrado_informacion_state import EventoCerradoInfromacionState
from itdb_ctf.evento_cerrado.evento_cerrado_acceso_state import EventoCerradoAccesoState
from itdb_ctf.evento_cerrado.evento_cerrado_acceso_view import con_acceso
from itdb_ctf.scoreboard.scoreboard_state import ScoreboardState

def evento_cerrado_scoreboard_page() -> rx.Component:
    return rx.vstack(
        navbar_cerrado(EventoCerradoInfromacionState.id_cerrado),
        con_acceso(evento_cerrado_scoreboard_view()),
        width="100%",
        on_mount=[ScoreboardState.escuchar_scoreboard, EventoCerradoAccesoState.escuchar_acceso],
        on_unmount=[ScoreboardState.stop_refresh, EventoCerradoAccesoState.parar_acceso],
    )
