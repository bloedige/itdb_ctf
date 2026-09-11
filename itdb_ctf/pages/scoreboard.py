import reflex as rx
from itdb_ctf.components.navbar import navbar
from itdb_ctf.scoreboard.scoreboard_view import scoreboard_view
from itdb_ctf.scoreboard.scoreboard_state import ScoreboardState

def scoreboard_page() -> rx.Component:
    return rx.grid(
        navbar(),
        scoreboard_view(),
        width="100%",
        justify_items="center",
        on_mount=ScoreboardState.escuchar_scoreboard,
        on_unmount=ScoreboardState.stop_refresh,
    )