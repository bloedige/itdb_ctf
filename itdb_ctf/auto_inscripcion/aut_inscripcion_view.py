import reflex as rx 
from itdb_ctf.components.form import button
from itdb_ctf.auto_inscripcion.auto_incripcion_state import AutoInscripcionState

def alert_incripcion(id_evento:int, titulo:str) -> rx.Component:
    return rx.alert_dialog.root(
        rx.alert_dialog.trigger(
            button("Inscribirse", "jade",[]),
        ),
        rx.alert_dialog.content(
            rx.vstack(
                rx.text("¿ Deseas inscribirte a: ?", weight="light", size="2"),
                rx.grid(
                    rx.text(titulo, weight="regular", size="3"),
                    width="100%",
                    place_items="center"
                ),
                rx.flex(
                    rx.alert_dialog.cancel(
                        button("Cancelar", "ruby", [])
                    ),
                    rx.alert_dialog.action(
                        button("Confirmar", "jade", AutoInscripcionState.cofirmar_inscrito(id_evento))
                    ),
                    width="100%",
                    justify="end",
                    spacing="4",
                ),
                spacing="4",
            ),
            width="50vh",
        ),
    )

def card_evento(ev:dict) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.grid(
                rx.text(ev['titulo'], weight="bold", size="4"),
                rx.grid(
                    rx.text(f"Modo: {ev['modo']}", weight="medium", size="3"),
                    rx.text(f"Duración: {ev['duracion']}", weight="medium", size="3"),
                    columns="2",
                    place_items="center",
                ),
                grid_template_columns="70% 1fr",
                width="100%",
            ),
            rx.accordion.root(
                rx.accordion.item(
                    header="Descripcion",
                    content=rx.markdown(
                        ev['descripcion'],
                    ),
                ),
                width="100%",
                collapsible=True,
                variant="ghost",
                color_scheme="gray",
            ),
            rx.grid(
                rx.box(
                    rx.text("Inicia", weight="light", size="3"),
                    rx.text(ev['fi_str'], weight="regular", size="6"),
                ),
                rx.box(
                    rx.text("Finaliza", weight="light", size="3"),
                    rx.text(ev['ff_str'], weight="regular", size="6"),
                ),
                rx.match(
                    ev['estado_evento'],
                    (
                        "futuro",
                        rx.box(
                            rx.text("Inicia en", weight="light", size="3"),
                            rx.text(ev['contador_inicio'], weight="regular", size="6"),    
                        ),
                    ),
                    (
                        "activo",
                        rx.box(
                            rx.text("Finaliza en", weight="light", size="3"),
                            rx.text(ev['contador_fin'], weight="regular", size="6"),    
                        ),
                    ),
                    rx.text("Finalizado", weight="regular", size="6"),
                ),
                width="100%",
                columns="3",
                place_items="center",
            ),
            rx.flex(
                rx.cond(
                    ev['inscrito'],
                    rx.badge(
                        "Participando",
                        color_scheme="jade",
                        variant="outline",
                        size='3',
                    ),
                    rx.cond(
                        ev['auto_inscripcion'] & (ev['estado_evento'] != "concluido") & (ev['estado_evento'] != "activo"),  
                        alert_incripcion(ev['id_evento'], ev['titulo']),
                        rx.cond(
                            ~ev['auto_inscripcion'] & (ev['estado_evento'] != "concluido"),
                            rx.badge(
                                "Solicite acceso a evento",
                                color_scheme="amber",
                                variant="outline",
                                size='3',
                            ),
                        ),
                    ),
                ),
                rx.cond(
                    ev['inscrito'],
                    rx.cond(
                        ev['estado_evento'] == "activo",
                        button("Ingresar", "jade", []),
                    ),
                    rx.cond(
                        ev['estado_evento'] != "futuro",
                        button("Scoreboard", "blue", []),
                    ),
                ),
                width="100%",
                justify="end",
                spacing="4",
            ),
            ),
        width="50%",
    ),

def eventos_view() -> rx.Component:
    return rx.vstack(
        rx.moment(
            interval=1000,
            on_change=AutoInscripcionState.actualizar_tiempo,
        ),
        rx.grid(
            rx.foreach(AutoInscripcionState.eventos_procesados, card_evento),
            place_items="center",
            width="100%",
            spacing="4"
        ),
        width="100%",

    )
