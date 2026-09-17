import os
import reflex as rx 
from itdb_ctf.components.form import button
from itdb_ctf.components.filtro_catalogo import filtros
from itdb_ctf.evento_cerrado.evento_cerrado_reto_state import EventoCerradoRetoState, EventoCerradoEnvioFlagState, EventoCerradoListarPistaState

# URL del backend (FastAPI). En prod single-port coincide con PUBLIC_URL.
BACKEND_URL = os.environ.get("API_URL") or os.environ.get("PUBLIC_URL") or "http://localhost:8000"

def pista_trigger(pista:dict) -> rx.Component:
    return rx.button(
        rx.grid(
            rx.text(f"Pista {pista['costo']} pts.", weight="regular", size="2"),
            place_items="center",
            width="100%",
        ),
        width="100%",
        bg=rx.cond(pista['adquirido'], "#fab80850", "#B3B3B350"),
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
            rx.flex(
                rx.dialog.close(button("Cancelar", "gray", [], size="2")),
                button("confirmar", "jade", [lambda: EventoCerradoListarPistaState.comprar_pista(pista['id_reto'], pista['id_pista'])], size="2"),
                width="100%",
                spacing="3",
                justify="end",
            ),
            spacing="3",
            place_items="center",
            width="100%",
        )
    )

def dialog_pista(pista:dict) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            pista_trigger(pista),
        ),
        rx.dialog.content(
            pista_content(pista),
            max_width=["90vw", "90vw", "400px", "400px", "400px"],
        )
    )

def reto_trigger(reto: dict) -> rx.Component:
    return rx.card(
        rx.flex(
            rx.text(reto['titulo'], size="3", weight="medium",
                color=rx.cond(reto['resuelto'], "#fab808FF", "")),
            rx.text(f"{reto['puntaje']} pts.", size="2", weight="regular",
                color=rx.cond(reto['resuelto'], "#fab808FF", "")),
            align="center", justify="center", direction="column", height="12vh", width="100%",
        ),
        rx.text(f"by. {reto['creador']}", size="1", weight="light",
            color=rx.cond(reto['resuelto'], "#fab808FF", ""),
            position="absolute", right="1em", bottom="1em",
        ),
        width="100%",
        bg=rx.cond(reto['resuelto'], "#fab80850", ""),
    )


def reto_content(reto: dict) -> rx.Component:
    return rx.vstack(
        rx.flex(
            rx.badge(reto['categoria'], variant="surface", color_scheme="amber", size="1"),
            rx.badge(reto['dificultad'], variant="surface", color_scheme="amber", size="1"),
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
        rx.foreach(EventoCerradoListarPistaState.pistas, dialog_pista),
        rx.cond(
            reto['original'] != None,
            rx.link(
                    rx.grid(
                        rx.icon("file_down", stroke_width=1.5 , size=15),
                        rx.text(reto['original'], size="2", weight="light", 
                            style={
                                "whiteSpace": "nowrap",
                                "overflow": "hidden",
                                "textOverflow": "ellipsis",
                            },
                        ),
                        grid_template_columns="10% 1fr",
                        spacing="2", 
                    ),
                max_width="30%",
                border="1px solid",
                border_radius=".3em",
                padding=".3em",
                bg="#049BFF3E",
                # is_external => target="_blank": sin esto el router de React
                # captura la URL (mismo origen en prod) y muestra su 404 en vez
                # de pedirle el archivo al backend.
                href=f"{BACKEND_URL}/api/reto/{reto['id_reto']}/descarga",
                is_external=True,
                text_decoration="none",
            ),
        ),
        rx.divider(),
        rx.hstack(
            rx.input(
                placeholder="flag{...}",
                on_change=EventoCerradoEnvioFlagState.set_flag,
                width="100%", auto_focus=True,
            ),
            rx.button(
                "Enviar",
                on_click=lambda: EventoCerradoEnvioFlagState.enviar_flag(reto['id_reto']),
            ),
            spacing="3", width="100%",
        ),
        spacing="3", width="100%",
    )


def reto_card_view(reto: dict) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            reto_trigger(reto),
            on_click=lambda: EventoCerradoListarPistaState.cargar_pistas(reto['id_reto']),
        ),
        rx.dialog.content(reto_content(reto), max_width=["90vw", "90vw", "480px", "480px", "480px"]),
        on_open_change=EventoCerradoEnvioFlagState.drop_flag,
    )


def evento_cerrado_retos_view() -> rx.Component:
    return rx.cond(
        EventoCerradoRetoState.acceso,
        rx.vstack(
            rx.grid(
                 rx.heading("Catalogo de retos", size="5"),
                filtros(
                    EventoCerradoRetoState.categorias,
                    EventoCerradoRetoState.id_categoria_filtro,
                    EventoCerradoRetoState.set_id_categoria_filtro,
                    EventoCerradoRetoState.dificultades,
                    EventoCerradoRetoState.id_dificultad_filtro,
                    EventoCerradoRetoState.set_id_dificultad_filtro,
                    "amber"
                ),
                width="100%",   
                spacing="4",
            ),
            rx.grid(
                rx.foreach(EventoCerradoRetoState.retos, reto_card_view),
                columns={"base": "1", "md": "4"},
                spacing="4", width="100%", place_items="center",
            ),
            align="center", spacing="5", width="60%",
        ),
        rx.center(
            rx.text(EventoCerradoRetoState.motivo, weight="medium", size="4", color="gray"),
            height="50vh",
            width="100%",
        ),
    )