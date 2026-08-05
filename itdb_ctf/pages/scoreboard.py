import reflex as rx
from itdb_ctf.scoreboard.scoreboard_view import scoreboard_view

def scoreboard_page() -> rx.Component:
    return rx.vstack(
        rx.grid(
            scoreboard_view(),
            width="100%",
            place_items="center",
        ),
        width="100%",
    )