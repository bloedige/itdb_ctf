"""Wrapper de acceso para las páginas de evento cerrado."""

import reflex as rx

from itdb_ctf.evento_cerrado.evento_cerrado_acceso_state import EventoCerradoAccesoState as A


def _aviso_denegado() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.icon("shield-x", size=54, color="var(--red-9)"),
            rx.heading(A.motivo, size="5", text_align="center"),
            spacing="4",
            align="center",
        ),
        height="70vh",
        width="100%",
    )


def con_acceso(contenido: rx.Component) -> rx.Component:
    """Muestra `contenido` si el estudiante tiene acceso; si lo perdió, solo el
    aviso con el motivo (para volver está "Regresar" en el navbar)."""
    return rx.cond(A.acceso, contenido, _aviso_denegado())
