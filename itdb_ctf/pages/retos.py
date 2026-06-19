import reflex as rx    
from itdb_ctf.components.navbar import navbar

def retos_page() -> rx.components:
    return rx.vstack(
        navbar(),
        rx.center(
            rx.vstack(
            rx.heading("retos"),
            width="300px"
        )
        ),
       width="100%", 
    )