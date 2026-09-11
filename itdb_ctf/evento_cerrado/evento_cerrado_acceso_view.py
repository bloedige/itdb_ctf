"""Wrapper de acceso para las páginas de evento cerrado."""

import reflex as rx

from itdb_ctf.evento_cerrado.evento_cerrado_acceso_state import EventoCerradoAccesoState as A


def _aviso_denegado() -> rx.Component:
    """Mismo estilo simple (texto centrado) en las 4 pestañas de evento cerrado —
    antes acá había un icono y en la vista de Retos era solo texto; se unificó."""
    return rx.center(
        rx.text(A.motivo, weight="medium", size="4", color="gray"),
        height="50vh",
        width="100%",
    )


def con_acceso(contenido: rx.Component) -> rx.Component:
    """Muestra `contenido` si el estudiante tiene acceso; si lo perdió, solo el
    aviso con el motivo (para volver está "Regresar" en el navbar)."""
    return rx.cond(A.acceso, contenido, _aviso_denegado())
