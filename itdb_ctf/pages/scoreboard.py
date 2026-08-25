import reflex as rx
from itdb_ctf.components.navbar import navbar
from itdb_ctf.scoreboard.scoreboard_view import scoreboard_view
from itdb_ctf.scoreboard.scoreboard_state import ScoreboardState

def scoreboard_page() -> rx.Component:
    return rx.vstack(
        navbar(),
        rx.grid(
            scoreboard_view(),
            width="100%",
            place_items="center",
        ),
        width="100%",
        on_mount=ScoreboardState.auto_refresh,
        on_unmount=ScoreboardState.stop_refresh,
    )