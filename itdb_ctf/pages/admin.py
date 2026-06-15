import reflex as rx 
from itdb_ctf.auth.auth_state import AuthState 

def admin_page() -> rx.Component:
    return rx.cond(
        AuthState.is_hydrated & AuthState.autenticado,
        rx.heading("marina")

    )