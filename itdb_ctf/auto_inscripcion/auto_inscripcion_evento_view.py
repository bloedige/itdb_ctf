import reflex as rx 
from itdb_ctf.components.form import button
from itdb_ctf.auto_inscripcion.auto_inscripcion_evento_state import AutoInscripcionState

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
            max_width=rx.breakpoints(sm="90vw", md="400px"),
        ),
    )

def icono() -> rx.Component:
    return rx.box(
        rx.image(
            src="/isotipo.svg",
            alt="CTF",
            width="3em",
            object_fit="cover",
        ),
        bg="#0115417E",
        padding=".5em",
        border_radius=".5em",
    )
def evento_titulo_detalle(ev:dict) -> rx.Component:
    return rx.box(
        rx.text(
            ev['titulo'], 
            weight="medium", 
            size="4", 
            ),
        rx.text(
            f"{ev['fi_str']}  •  {ev['modalidad']}  •  {ev['duracion']}",
            weight="light",
            font_size=".8em",
            color="#818181",
            ),
    )

def ver_descripcion(desc) -> rx.components:
    return rx.dialog.root(
        rx.dialog.trigger(
            button(
                "Descripción",
                "gray",
                [],
            ),
        ),
        rx.dialog.content(
            rx.markdown(desc),
        ),
    )

def estado_participante(ev:dict) -> rx.Component:
    return rx.cond(
        ev['estado_usuario'],
        rx.badge(
            ev['estado_usuario'],
            color_scheme="jade",
            variant="surface",
            size='2',
        ),
        rx.text(
            " ",
            weight="light",
            font_size=".8em",
            color="#818181",
        ),
    ),

def time(ev:dict) -> rx.Component:
    return rx.match(
        ev['estado_evento'],
        (
            "futuro",
            rx.box(
                rx.text("Inicia en", weight="light",
                    font_size=".8em",
                    color="#818181",
                ),
                rx.text(ev['contador_inicio'], weight="regular", size="4"),    
            ),
        ),
        (
            "activo",
            rx.box(
                rx.text("Finaliza en", weight="light",
                    font_size=".8em",
                    color="#818181",
                ),
                rx.text(ev['contador_fin'], weight="regular", size="4"),    
            ),
        ),
        rx.text("Finalizado", weight="regular", size="4"),
    ),

def actions(ev:dict) -> rx.Component:
    return rx.match(
        ev['estado_evento'],
        (
            "activo",
            rx.cond(
                ev['inscrito'],
                rx.link(button("Ingresar", "jade", []), href=f"/evento/{ev['id_evento_cerrado']}/informacion"),
                rx.link(button("Scoreboard", "blue", []), href=f"/evento/{ev['id_evento_cerrado']}/scoreboard"),
            ),
        ),
        (
            "concluido",
            rx.link(button("Scoreboard", "blue", []), href=f"/evento/{ev['id_evento_cerrado']}/scoreboard"),  
        ),
        rx.cond(
            ev['auto_inscripcion'] & (ev['estado_evento'] != "concluido") & (ev['estado_evento'] != "activo"),  
            alert_incripcion(ev['id_evento_cerrado'], ev['titulo']),
            rx.cond(
                ~ev['auto_inscripcion'] & (ev['estado_evento'] != "concluido"),
                rx.text(
                    "Inscripción mediante cordinador",
                    font_size=".8em",
                    color="#818181",
                ),
            ),
        ),
    ),


def card_evento(ev:dict) -> rx.Component:
    return rx.card(
        rx.tablet_and_desktop(
            rx.grid(
                rx.grid(
                    icono(),
                    evento_titulo_detalle(ev),
                    width="100%",
                    grid_template_columns="3em 1fr",
                    gap=".8em",
                    align_items="center",
                ),
                estado_participante(ev),
                ver_descripcion(ev['descripcion']), 
                time(ev),
                actions(ev),   
                grid_template_columns="1fr 12% 12% 12% 12%",
                align_items="center",
                justify_items="center",
            ),
        ),
        rx.mobile_only(
            rx.grid(
                rx.grid(
                    icono(),
                    evento_titulo_detalle(ev),
                    width="100%",
                    grid_template_columns="3em 1fr",
                    gap=".8em",
                    align_items="center",
                ),
                actions(ev),   
                grid_template_columns="1fr 12%",
                align_items="center",
                justify_items="center",
            ),
        ),
        width="95%",
    )

def auto_inscripcion_eventos_view() -> rx.Component:
    return rx.vstack(
        rx.moment(
            interval=1000,
            on_change=AutoInscripcionState.actualizar_tiempo,
            style={"display":"none"}
        ),
        rx.heading("Eventos", size="5",),
        rx.grid(
            rx.foreach(AutoInscripcionState.eventos_procesados, card_evento),
            place_items="center",
            width="100%",
            spacing="3"
        ),
        width=rx.breakpoints(sm="95%", md="60%"),
        spacing="4",
    )
