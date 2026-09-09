import reflex as rx
from itdb_ctf.auth.auth_state import AuthState
from itdb_ctf.perfil.gestion_state import PerfilGestionState
from itdb_ctf.perfil.gestion_view import dialogo_perfil

def link(legend:str, url:str) -> rx.Component:
    return rx.link(
        legend,
        href=url,
        underline="none", 
        color=rx.cond(
            rx.State.router.url.path == url,
            "#fab808",
            "#ffffff",
        ),
        _hover={
            "color":"#fab808",
        }     
    )

def logo() -> rx.Component:
    return rx.grid(           
        rx.image(
            src="/isotipo.svg",
            alt="ITDB - CTF",
            width="7.5vh",
        ),
        rx.flex(
            rx.flex(
                rx.text("I", size="5", weight="bold"),
                rx.text("T", size="5", weight="bold"),
                rx.text("D", size="5", weight="bold"),
                rx.text("B", size="5", weight="bold"),
                width="100%",
                justify="between",
             ),
            rx.flex(
                rx.text("Capture", weight="regular"),
                rx.text("The", weight="regular"),
                rx.text("Flag", weight="regular", color_scheme="amber"),
                width="100%",
                justify="center",
                gap=".3em",
                margin_top="-5px",
                style={"font-size":".7em"}
            ),
            direction="column",
            width="100%",
            place_items="center",
        ),
        width="100%",
        grid_auto_flow="column",
        justify="between",
        align="center",
    ),

def _item_menu(icono: str, texto: str, accion, color: str) -> rx.Component:
    """Botón con el mismo formato que 'Cerrar sesión' (ghost, icono + texto)."""
    return rx.button(
        rx.hstack(
            rx.icon(icono, size=20),
            rx.text(texto),
            direction=rx.cond(AuthState.codigo_rol == "user", "row-reverse", "row"),
        ),
        on_click=accion,
        variant="ghost",
        color_scheme=color,
        width="100%",
    )


def log_out() -> rx.Component:
    return _item_menu("log_out", "Cerrar Sesion", AuthState.logout, "red")


def _boton_editar_perfil() -> rx.Component:
    return _item_menu("pencil", "Editar perfil", PerfilGestionState.abrir, "gray")

def _boton_perfil() -> rx.Component:
    return rx.button(
        rx.flex(
            rx.icon(
                "user",
                size=25,
            ),
            rx.flex(
                rx.text("alias", weight="medium"),
                rx.text("correo@correo", weight="light"),
                align=rx.cond(
                    AuthState.codigo_rol == "user",
                    "end",
                    "start",
                ),
                direction="column",
            ),
            width="100%",
            direction=rx.cond(AuthState.codigo_rol == "user", "row-reverse", "row"),
            align="center",
            justify_content="space-evenly",
        ),
        color_scheme="amber",
        variant="ghost",
        width="100%",
    )


def perfil() -> rx.Component:
    # Solo top bar (navbar): menú desplegable Perfil · (Editar perfil, solo autor) · Cerrar sesión.
    return rx.fragment(
        rx.menu.root(
            rx.menu.trigger(_boton_perfil()),
            rx.menu.content(
                _item_menu("user", "Perfil", rx.redirect("/perfil"), "amber"),
                _boton_editar_perfil(),
                log_out(),
            ),
        ),
        dialogo_perfil(),
    )

def navbar() -> rx.Component: 
    return rx.box(
            rx.grid(
                logo(),
                rx.flex(
                    link("Información", "/informacion"),
                    link("Retos", "/retos"),
                    link("Scoreboard", "/scoreboard"),
                    link("Eventos", "/eventos"),
                    width="100%",
                    justify="end",
                    spacing="4",
                    margin_right="5em",
                ),
                rx.cond(
                    AuthState.autenticado,
                    perfil(),
                ),
                grid_template_columns="10% 1fr 10%",
                place_items="center",
                width="100%",
            ),
            top="0",
            width="100%",
            padding=".5em",
            bg="#011541",
            position="sticky",
            z_index="100"
    )

def navbar_cerrado(id_evento) -> rx.Component:
    return rx.box(
        rx.grid(
            logo(),
            rx.flex(
                link("Información", f"/evento/{id_evento}/informacion"),
                link("Retos", f"/evento/{id_evento}/retos"),
                link("Scoreboard", f"/evento/{id_evento}/scoreboard"),
                link("Perfil", f"/evento/{id_evento}/perfil"),
                width="100%",
                justify="end",
                spacing="4",
                margin_right="10em",
            ),
           
            rx.button(
                "Regresar",
                color_scheme="amber",
                on_click=rx.redirect("/eventos")
            ), 
            grid_template_columns="10% 1fr 10%",
            place_items="center",
            width="100%",
        ),
        width="100%",
        padding=".5em",
        spacing="4",
        bg="#011541",
        position="sticky",
        z_index="100",
        top="0",
        left="0",
    )

def navbar_staff() -> rx.Component:
    return rx.flex(
        logo(),
        rx.divider(),
        rx.grid(
            rx.match(
                AuthState.codigo_rol,
                (
                    "autor",
                    rx.grid(
                        link("Gestion de retos", "/admin/retos"),
                        link("Dashboard retos", "/admin/dashboard/retos"),
                        width="100%", spacing="1", justify="start",
                    ),
                ),
                (
                    "admin",
                    rx.grid(
                        link("Dashboard", "/admin/dashboard"),
                        link("Dashboard eventos", "/admin/dashboard/eventos-cerrados"),
                        link("Dashboard retos", "/admin/dashboard/retos"),
                        link("Dashboard usuarios", "/admin/dashboard/usuarios"),
                        link("Gestion de evento", "/admin/eventos"),
                        link("Gestion de retos", "/admin/retos"),
                        link("Retos en eventos", "/admin/asociar"),
                        link("Gestion de usuario", "/admin/usuarios"),
                        link("Inscribir usuarios", "/admin/inscribir"),
                        width="100%", spacing="1", justify="start",
                    ),
                ),
                (
                    "superadmin",
                    rx.grid(
                        link("Dashboard", "/admin/dashboard"),
                        link("Dashboard eventos", "/admin/dashboard/eventos-cerrados"),
                        link("Dashboard retos", "/admin/dashboard/retos"),
                        link("Dashboard usuarios", "/admin/dashboard/usuarios"),
                        link("Gestion de evento", "/admin/eventos"),
                        link("Gestion de retos", "/admin/retos"),
                        link("Retos en eventos", "/admin/asociar"),
                        link("Gestion de usuario", "/admin/usuarios"),
                        link("Inscribir usuarios", "/admin/inscribir"),
                        width="100%", spacing="1", align="start",
                    ),
                ),
            ),
            width="100%",
            align="start",
            justify="center",
            spacing="1",
        ),
        rx.spacer(),
        rx.cond(AuthState.codigo_rol == "autor", _boton_editar_perfil(), rx.fragment()),
        log_out(),
        rx.divider(),
        _boton_perfil(),
        dialogo_perfil(),
        width="100%",
        height="100vh",
        direction="column",
        padding="1em",
        spacing="1",
        bg="#011541",
        position="sticky",
        z_index="100",
        top="0",
    )