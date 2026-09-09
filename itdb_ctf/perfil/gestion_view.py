import reflex as rx

from itdb_ctf.perfil.gestion_state import PerfilGestionState as S
from itdb_ctf.components.form import input_box, badge_msg, button, close_dialog_button


def _campos_nombre() -> rx.Component:
    return rx.fragment(
        input_box("Nombre", "Nombre...", S.nombre, S.set_nombre, "text"),
        input_box("Apellido paterno", "Paterno...", S.paterno, S.set_paterno, "text"),
        input_box("Apellido materno (opcional)", "Materno...", S.materno, S.set_materno, "text"),
    )


def _contenido() -> rx.Component:
    return rx.vstack(
        rx.heading("Editar mis datos", size="3"),
        rx.cond(S.edita_nombre, _campos_nombre(), rx.fragment()),
        input_box("Alias", "Tu alias público...", S.alias, S.set_alias, "text"),
        rx.text(
            "Tu alias es público (scoreboard, perfil). Debe ser único y sin lenguaje ofensivo.",
            size="1", weight="light", color_scheme="gray",
        ),
        rx.cond(S.mensaje != "", badge_msg(S.mensaje, "yellow"), rx.spacer()),
        rx.hstack(
            rx.spacer(),
            button("Guardar", "jade", S.guardar),
            button("Cancelar", "ruby", S.cerrar),
            width="100%",
            spacing="2",
        ),
        width="100%",
        spacing="4",
    )


def dialogo_perfil() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            _contenido(),
            close_dialog_button(S.cerrar),
            max_width="460px",
        ),
        open=S.abierto,
        on_open_change=S.set_abierto,
    )
