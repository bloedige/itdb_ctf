import reflex as rx

from itdb_ctf.auth.auth_state import AuthState
from itdb_ctf.components.nav_state import NavState
from itdb_ctf.perfil.gestion_state import PerfilGestionState
from itdb_ctf.perfil.gestion_view import dialogo_perfil
from itdb_ctf.evento_cerrado.evento_cerrado_informacion_state import EventoCerradoInfromacionState

# --- Paleta de marca (local al navbar) --------------------------------------
AZUL      = "#011541"                # fondo de las tres barras
AZUL_2    = "#04205a"                # menús / drawers sobre el fondo
ORO       = "#fab808"                # acento: link activo, avatar, foco
ORO_TENUE = "rgba(250,184,8,.14)"    # píldora del ítem activo
NAV_INK   = "#c6cfe2"                # texto de link inactivo
NAV_INK_2 = "#8fa0c1"                # texto secundario (correo, labels)
BORDE     = "rgba(250,184,8,.22)"
LINEA     = "rgba(255,255,255,.10)"
PELIGRO   = "#ff6b6b"

# breakpoints: [base, sm, md, lg, xl] — los links se ven desde `md`
_VER_LINKS = ["none", "none", "flex", "flex", "flex"]
_VER_MOVIL = ["flex", "flex", "none", "none", "none"]


def _path():
    return rx.State.router.url.path


def _activa(url, prefijo: bool = False):
    if prefijo:
        return _path().startswith(url)
    return _path() == url


# --- piezas compartidas ----------------------------------------------------
def logo() -> rx.Component:
    return rx.link(
        rx.hstack(
            rx.image(src="/isotipo.svg", alt="ITDB CTF", width="2.4em", height="2.4em"),
            rx.hstack(
                rx.text("ITDB", weight="bold", size="4", letter_spacing="0.04em"),
                rx.text("·", weight="bold", size="4", color=ORO),
                rx.text("CTF", weight="bold", size="4", letter_spacing="0.04em"),
                spacing="1",
                align="center",
            ),
            align="center",
            spacing="2",
        ),
        href="/informacion",
        underline="none",
        color="white",
        flex_shrink="0",
    )


def _texto_ellipsis(*children, **props) -> rx.Component:
    """`rx.text` que recorta con puntos suspensivos si el contenido se desborda."""
    return rx.text(
        *children,
        white_space="nowrap",
        overflow="hidden",
        text_overflow="ellipsis",
        max_width="100%",
        **props,
    )


def _identidad(alias, email, alias_props: dict | None = None, email_props: dict | None = None) -> rx.Component:
    """Bloque alias + correo; ambos se recortan con ellipsis si no caben."""
    return rx.vstack(
        _texto_ellipsis(alias, **(alias_props or {})),
        _texto_ellipsis(email, **(email_props or {})),
        spacing="0",
        align="start",
        min_width="0",
        width="100%",
        flex="1",
    )


def _avatar(iniciales, size: str = "30px") -> rx.Component:
    return rx.center(
        rx.text(iniciales, weight="bold", size="2", color=ORO),
        width=size,
        height=size,
        flex_shrink="0",
        background=ORO_TENUE,
    )


def _nav_link(texto: str, url, prefijo: bool = False) -> rx.Component:
    activa = _activa(url, prefijo)
    return rx.link(
        texto,
        href=url,
        underline="none",
        white_space="nowrap",
        font_size="0.92rem",
        font_weight="500",
        padding_block="0.55rem",
        border_bottom="2px solid transparent",
        color=rx.cond(activa, ORO, NAV_INK),
        border_bottom_color=rx.cond(activa, ORO, "transparent"),
        _hover={"color": ORO},
    )


def _perfil_menu() -> rx.Component:
    """Menú desplegable de la barra superior (evento abierto / público)."""
    p = NavState.perfil_min
    return rx.menu.root(
        rx.menu.trigger(
            rx.hstack(
                _avatar(p["iniciales"]),
                _identidad(
                    p["alias"], p["email"],
                    {"weight": "medium", "size": "2", "color": "white", "line_height": "1.2"},
                    {"size": "1", "color": NAV_INK_2, "line_height": "1.2"},
                ),
                rx.icon("chevron_down", size=15, color=NAV_INK_2, flex_shrink="0"),
                align="center",
                spacing="2",
                padding="0.25rem 0.3rem",
                cursor="pointer",
                min_width="0",
                max_width="230px",
                _hover={"opacity": "0.85"},
            ),
            as_child=True,
        ),
        rx.menu.content(
            rx.hstack(
                _avatar(p["iniciales"]),
                _identidad(
                    p["nombre"], p["email"],
                    {"weight": "bold", "size": "2"},
                    {"size": "1", "color_scheme": "gray"},
                ),
                spacing="2",
                align="center",
                padding="0.4rem 0.5rem",
                min_width="0",
                max_width="260px",
            ),
            rx.menu.separator(),
            rx.menu.item(rx.icon("user", size=16), "Mi perfil", on_click=rx.redirect("/perfil")),
            rx.menu.item(rx.icon("pencil", size=16), "Editar perfil", on_click=PerfilGestionState.abrir),
            rx.menu.separator(),
            rx.menu.item(rx.icon("log_out", size=16), "Cerrar sesión", color=PELIGRO, on_click=AuthState.logout),
        ),
    )


def _hamburguesa(accion=None) -> rx.Component:
    return rx.center(
        rx.cond(NavState.menu_movil, rx.icon("x", size=20), rx.icon("menu", size=20)),
        on_click=accion if accion is not None else NavState.toggle_menu,
        display=_VER_MOVIL,
        width="38px",
        height="38px",
        border="1px solid rgba(255,255,255,.16)",
        border_radius="8px",
        color=rx.cond(NavState.menu_movil, ORO, "white"),
        cursor="pointer",
    )


def _drawer_accion(texto: str, icono: str, accion, color: str = "white") -> rx.Component:
    return rx.hstack(
        rx.icon(icono, size=16),
        rx.text(texto, size="2"),
        on_click=accion,
        color=color,
        align="center",
        spacing="2",
        width="100%",
        padding="0.5rem 0.6rem",
        border_radius="8px",
        cursor="pointer",
        _hover={"background": "rgba(255,255,255,.05)"},
    )


def _accion_perfil(icono: str, texto: str, accion, color: str = NAV_INK) -> rx.Component:
    """Misma pinta que los ítems de navegación del sidebar, pero dispara una acción."""
    return rx.hstack(
        rx.icon(icono, size=16),
        rx.text(texto, size="2"),
        on_click=accion,
        align="center",
        spacing="2",
        width="100%",
        padding="0.5rem 0.6rem",
        border_radius="8px",
        color=color,
        cursor="pointer",
        _hover={"background": "rgba(255,255,255,.05)"},
    )


def _drawer(cuerpo) -> rx.Component:
    """Panel deslizante para móvil. `cuerpo` es una lista de componentes."""
    return rx.box(
        rx.box(  # fondo oscuro
            on_click=NavState.cerrar_menu,
            position="fixed",
            inset="0",
            background="rgba(1,8,26,.55)",
            opacity=rx.cond(NavState.menu_movil, "1", "0"),
            pointer_events=rx.cond(NavState.menu_movil, "auto", "none"),
            transition="opacity .2s ease",
            z_index="200",
        ),
        rx.vstack(
            rx.hstack(
                rx.spacer(),
                rx.center(
                    rx.icon("x", size=20),
                    on_click=NavState.cerrar_menu,
                    width="36px",
                    height="36px",
                    border_radius="8px",
                    color="white",
                    cursor="pointer",
                    _hover={"background": "rgba(255,255,255,.06)"},
                ),
                width="100%",
                align="center",
                margin_bottom="0.25em",
            ),
            *cuerpo,
            position="fixed",
            top="0",
            bottom="0",
            right="0",
            width="60vw",
            background=AZUL_2,
            border_left=f"1px solid {BORDE}",
            padding="1em",
            spacing="1",
            align="stretch",
            overflow_y="auto",
            transform=rx.cond(NavState.menu_movil, "translateX(0)", "translateX(100%)"),
            transition="transform .22s ease",
            z_index="201",
        ),
        display=_VER_MOVIL,
    )


def _link_drawer(texto: str, url, icono: str | None = None, prefijo: bool = False) -> rx.Component:
    activa = _activa(url, prefijo)
    return rx.link(
        rx.hstack(
            rx.icon(icono, size=16) if icono else rx.fragment(),
            rx.text(texto, size="2"),
            align="center",
            spacing="2",
        ),
        href=url,
        underline="none",
        on_click=NavState.cerrar_menu,
        color=rx.cond(activa, ORO, NAV_INK),
        background=rx.cond(activa, ORO_TENUE, "transparent"),
        width="100%",
        padding="0.5rem 0.6rem",
        border_radius="8px",
    )


# --- barra superior: evento abierto / páginas públicas --------------------
# (texto, ruta, icono)
_LINKS_ABIERTO = [
    ("Información", "/informacion", "info"),
    ("Retos", "/retos", "flag"),
    ("Scoreboard", "/scoreboard", "trophy"),
    ("Eventos", "/eventos", "calendar"),
]


def navbar() -> rx.Component:
    return rx.box(
        rx.hstack(
            logo(),
            rx.spacer(),
            rx.hstack(
                *[_nav_link(t, u) for t, u, _ in _LINKS_ABIERTO],
                spacing="5",
                align="center",
                display=_VER_LINKS,
            ),
            rx.box(
                rx.cond(AuthState.autenticado, _perfil_menu()),
                display=_VER_LINKS,
                margin_left="1.5em",
            ),
            _hamburguesa(),
            width="100%",
            align="center",
            spacing="3",
        ),
        _drawer(
            [
                *[_link_drawer(t, u, ic) for t, u, ic in _LINKS_ABIERTO],
                rx.cond(
                    AuthState.autenticado,
                    rx.vstack(
                        rx.divider(margin_block="0.5em"),
                        rx.hstack(
                            _avatar(NavState.perfil_min["iniciales"]),
                            _identidad(
                                NavState.perfil_min["alias"], NavState.perfil_min["email"],
                                {"weight": "medium", "size": "2", "color": "white"},
                                {"size": "1", "color": NAV_INK_2},
                            ),
                            spacing="2",
                            align="center",
                            padding="0.4rem 0.6rem",
                            min_width="0",
                            width="100%",
                        ),
                        _drawer_accion("Mi perfil", "user", [NavState.cerrar_menu, rx.redirect("/perfil")]),
                        _drawer_accion("Editar perfil", "pencil", [NavState.cerrar_menu, PerfilGestionState.abrir]),
                        _drawer_accion("Cerrar sesión", "log_out", AuthState.logout, PELIGRO),
                        width="100%",
                        spacing="1",
                        align="stretch",
                    ),
                ),
            ]
        ),
        dialogo_perfil(),
        position="sticky",
        top="0",
        z_index="100",
        width="100%",
        padding="0.55rem 1.15rem",
        background=AZUL,
        border_bottom=f"1px solid {BORDE}",
    )


# --- barra superior: dentro de un evento cerrado -------------------------
def _badge_estado(estado) -> rx.Component:
    return rx.match(
        estado,
        ("activo", rx.badge("En curso", color_scheme="green", variant="soft")),
        ("futuro", rx.badge("Próximo", color_scheme="amber", variant="soft")),
        ("concluido", rx.badge("Finalizado", color_scheme="gray", variant="soft")),
        rx.fragment(),
    )


def navbar_cerrado(id_evento) -> rx.Component:
    links = [
        ("Información", f"/evento/{id_evento}/informacion", "info"),
        ("Retos", f"/evento/{id_evento}/retos", "flag"),
        ("Scoreboard", f"/evento/{id_evento}/scoreboard", "trophy"),
        ("Perfil", f"/evento/{id_evento}/perfil", "user"),
    ]
    titulo = EventoCerradoInfromacionState.titulo
    volver = rx.button(
        rx.icon("arrow_left", size=14),
        "Volver a eventos",
        color_scheme="amber",
        variant="soft",
        size="2",
        on_click=rx.redirect("/eventos"),
    )
    return rx.box(
        rx.hstack(
            logo(),
            rx.cond(
                titulo != "",
                rx.hstack(
                    rx.text(f"// {titulo}", size="2", color=NAV_INK_2, white_space="nowrap"),
                    _badge_estado(EventoCerradoInfromacionState.estado_evento),
                    align="center",
                    spacing="2",
                    padding_left="1em",
                    border_left=f"1px solid {LINEA}",
                    display=_VER_LINKS,
                ),
            ),
            rx.spacer(),
            rx.hstack(
                *[_nav_link(t, u) for t, u, _ in links],
                spacing="5",
                align="center",
                display=_VER_LINKS,
            ),
            rx.box(
                volver,
                _avatar(NavState.perfil_min["iniciales"]),
                display=_VER_LINKS,
                margin_left="1.5em",
                align_items="center",
                gap="0.8em",
            ),
            _hamburguesa(),
            width="100%",
            align="center",
            spacing="3",
        ),
        _drawer(
            [
                *[_link_drawer(t, u, ic) for t, u, ic in links],
                rx.divider(margin_block="0.5em"),
                _drawer_accion("Volver a eventos", "arrow_left", [NavState.cerrar_menu, rx.redirect("/eventos")]),
            ]
        ),
        position="sticky",
        top="0",
        left="0",
        z_index="100",
        width="100%",
        padding="0.55rem 1.15rem",
        background=AZUL,
        border_bottom=f"1px solid {BORDE}",
    )


# --- barra lateral: panel de administración -----------------------------
# (titulo, roles con acceso, [(texto, ruta, icono), ...])
SECCIONES_STAFF = [
    ("Dashboards", {"admin", "superadmin"}, [
        ("Resumen", "/admin/dashboard", "layout_dashboard"),
        ("Eventos", "/admin/dashboard/eventos-cerrados", "calendar"),
        ("Retos", "/admin/dashboard/retos", "flag"),
        ("Usuarios", "/admin/dashboard/usuarios", "users"),
    ]),
    ("Eventos", {"admin", "superadmin"}, [
        ("Gestionar eventos", "/admin/eventos", "calendar"),
        ("Asociar retos", "/admin/asociar", "link"),
        ("Retos de evento", "/admin/asociar/gestionar", "list"),
    ]),
    ("Inscripciones", {"admin", "superadmin"}, [
        ("Inscribir usuarios", "/admin/inscribir", "user_plus"),
        ("Participantes", "/admin/inscribir/gestionar", "users"),
    ]),
    ("Panel de autor", {"autor"}, [
        ("Dashboard retos", "/admin/dashboard/retos", "flag"),
    ]),
    ("Retos", {"autor", "admin", "superadmin"}, [
        ("Gestionar retos", "/admin/retos", "flag"),
    ]),
    ("Usuarios", {"admin", "superadmin"}, [
        ("Gestionar usuarios", "/admin/usuarios", "users"),
    ]),
]


def _rol_en(roles) -> rx.Var:
    it = iter(roles)
    cond = AuthState.codigo_rol == next(it)
    for r in it:
        cond = cond | (AuthState.codigo_rol == r)
    return cond


def _item_sidebar(texto: str, url: str, icono: str) -> rx.Component:
    activa = _path() == url
    return rx.link(
        rx.hstack(
            rx.icon(icono, size=16),
            rx.text(texto, size="2"),
            align="center",
            spacing="2",
        ),
        href=url,
        underline="none",
        on_click=NavState.cerrar_menu,
        width="100%",
        padding="0.5rem 0.6rem",
        border_radius="8px",
        border_left="2px solid transparent",
        color=rx.cond(activa, ORO, NAV_INK),
        background=rx.cond(activa, ORO_TENUE, "transparent"),
        border_left_color=rx.cond(activa, ORO, "transparent"),
        _hover={"background": "rgba(255,255,255,.05)", "color": "white"},
    )


def _seccion_sidebar(titulo: str, items) -> rx.Component:
    return rx.vstack(
        rx.text(
            titulo.upper(),
            size="1",
            weight="medium",
            color=NAV_INK_2,
            letter_spacing="0.14em",
            padding="0.35rem 0.5rem",
        ),
        *[_item_sidebar(t, u, ic) for t, u, ic in items],
        spacing="0",
        align="stretch",
        width="100%",
    )


def _secciones_por_rol() -> list[rx.Component]:
    return [
        rx.cond(_rol_en(roles), _seccion_sidebar(titulo, items), rx.fragment())
        for titulo, roles, items in SECCIONES_STAFF
    ]


def _tarjeta_perfil_staff() -> rx.Component:
    p = NavState.perfil_min
    return rx.vstack(
        rx.hstack(
            _avatar(p["iniciales"]),
            _identidad(
                p["alias"], p["email"],
                {"weight": "medium", "size": "2", "color": "white", "line_height": "1.2"},
                {"size": "1", "color": NAV_INK_2, "line_height": "1.2"},
            ),
            align="center",
            spacing="2",
            width="100%",
            min_width="0",
        ),
        rx.cond(
            AuthState.codigo_rol == "autor",
            _accion_perfil("pencil", "Editar perfil", [NavState.cerrar_menu, PerfilGestionState.abrir]),
        ),
        _accion_perfil("log_out", "Cerrar sesión", AuthState.logout, PELIGRO),
        spacing="1",
        align="stretch",
        width="100%",
    )


def navbar_staff() -> rx.Component:
    return rx.box(
        # --- sidebar (escritorio) ---
        rx.vstack(
            rx.box(
                logo(),
                padding="0.9rem 1rem",
                border_bottom=f"1px solid {LINEA}",
                width="100%",
            ),
            rx.vstack(
                *_secciones_por_rol(),
                align="stretch",
                width="100%",
                flex="1",
                min_height="0",
                overflow_y="auto",
                padding="0.75rem 0.6rem",
            ),
            rx.box(
                _tarjeta_perfil_staff(),
                padding="0.9rem",
                border_top=f"1px solid {LINEA}",
                width="100%",
                flex_shrink="0",
            ),
            display=["none", "none", "flex", "flex", "flex"],
            width="100%",
            height="100%",
            spacing="0",
            background=AZUL,
            border_right=f"1px solid {BORDE}",
        ),
        # --- barra superior (móvil) ---
        rx.hstack(
            logo(),
            rx.spacer(),
            _hamburguesa(),
            display=_VER_MOVIL,
            position="sticky",
            top="0",
            z_index="100",
            width="100%",
            padding="0.55rem 0.8rem",
            background=AZUL,
            border_bottom=f"1px solid {BORDE}",
            align="center",
            spacing="2",
        ),
        _drawer(
            [
                *_secciones_por_rol(),
                rx.divider(margin_block="0.5em"),
                _tarjeta_perfil_staff(),
            ]
        ),
        dialogo_perfil(),
        width="100%",
        # El `sticky` va en la celda del grid (no en el vstack de adentro): su
        # bloque contenedor es el grid de la página —tan alto como el contenido—,
        # así hay recorrido para fijarse. `align_self=start` impide que el grid la
        # estire a esa altura; `height=100vh` la topa a una pantalla. En móvil
        # vuelve a fluir (la barra superior se fija por su cuenta).
        align_self="start",
        height=["auto", "auto", "100vh", "100vh", "100vh"],
        position=["static", "static", "sticky", "sticky", "sticky"],
        top="0",
        z_index="100",
    )
