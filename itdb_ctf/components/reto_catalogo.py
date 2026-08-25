import reflex as rx
from itdb_ctf.components.form import button

def pista_trigger(pista:dict) -> rx.Component:
    return rx.button(
        rx.grid(
            rx.text(f"Pista {pista['costo']} pts.", weight="regular", size="2"),
            place_items="center",
            width="100%",
        ),
        width="100%",
        bg=rx.cond(pista['adquirido'], "#00FFC350", ""),
    )

def pista_content(pista:dict) -> rx.Component:
    return rx.cond(
        pista['adquirido'],
        rx.grid(
            rx.text(f"Pista {pista['costo']} pts.", weight="bold", size="3"),
            rx.text(pista['descripcion'], weight="regular", width="100%", size="2"),
            spacing="3",
            place_items="center",
            width="100%",
        ),
        rx.grid(
            rx.text(f"Pista {pista['costo']} pts.", weight="bold", size="3"),
            rx.text("¿Desea adquirir la pista?", weight="regular", width="100%", size="2"),
            spacing="3",
            place_items="center",
            width="100%",
        )
    )

def dialog_pista(pista:dict, state_comprar_pista) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            pista_trigger(pista),
        ),
        rx.dialog.content(
            pista_content(pista),
            rx.cond(
                ~pista['adquirido'],
                rx.flex(
                    rx.dialog.close(button("Cancelar", "gray", [], size="2")),
                    button("confirmar", "jade", [lambda: state_comprar_pista(pista['id_reto'],pista['id_pista'])], size="2"),
                    spacing="3",
                    justify="end",
                ),
            ),
            max_width="45vh"
        )
    )


def reto_trigger(reto: dict) -> rx.Component:
    return rx.card(
        rx.flex(
            rx.text(reto['titulo'], size="3", weight="medium",
                color=rx.cond(reto['resuelto'], "#00FFC3FF", "")),
            rx.text(f"{reto['puntaje']} pts.", size="2", weight="regular",
                color=rx.cond(reto['resuelto'], "#00FFC3FF", "")),
            align="center", justify="center", direction="column", height="8vh", width="100%",
        ),
        rx.text(f"by. {reto['creador']}", size="1", weight="light",
            color=rx.cond(reto['resuelto'], "#00FFC3FF", ""),
            position="absolute", right="1em", bottom="1em",
        ),
        width="100%",
        bg=rx.cond(reto['resuelto'], "#00FFC350", ""),
    )


def reto_content(reto:dict, state_pistas, state_comprar_pista, set_flag, enviar_flag) -> rx.Component:
    return rx.vstack(
        rx.flex(
            rx.badge(reto['categoria'], variant="surface", color_scheme="jade", size="1"),
            rx.badge(reto['dificultad'], variant="surface", color_scheme="jade", size="1"),
            justify="end", spacing="2", width="100%",
        ),
        rx.divider(),
        rx.grid(
            rx.text(reto['titulo'], weight="bold", size="3"),
            rx.text(f"{reto['puntaje']} pts.", size="2", weight="medium"),
            place_items="center", width="100%",
        ),
        rx.divider(),
        rx.text(reto['descripcion'], weight="regular", width="100%"),
        rx.foreach(state_pistas, lambda p: dialog_pista(p, state_comprar_pista)),
        rx.divider(),
        rx.hstack(
            rx.input(
                placeholder="flag{...}",
                on_change=set_flag,
                width="100%", auto_focus=True,
            ),
            rx.button(
                "Enviar",
                on_click = lambda:enviar_flag(reto['id_reto']),
            ),
            spacing="3", width="100%",
        ),
        spacing="3", width="100%",
    )


def reto_card_view(reto: dict, state_pistas, state_comprar_pista, set_flag, drop_flag, enviar_flag) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            reto_trigger(reto),
            on_click=lambda: ListarPistaCerradoState.cargar_pistas(EventoCerradoState.id_evento, reto['id_reto']),
        ),
        rx.dialog.content(reto_content(reto), max_width="50vh"),
        on_open_change=EnvioFlagCerradoState.drop_flag,
    )