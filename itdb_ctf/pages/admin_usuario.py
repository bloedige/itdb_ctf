import reflex as rx
from itdb_ctf.components.navbar import navbar_staff
from itdb_ctf.usuario.form_crear_usuario_view import form_crear_usuario_view
from itdb_ctf.usuario.tabla_usuarios_view import tabla_usuario_view
from itdb_ctf.usuario.credenciales_usuario_view import credenciales_dialog

def admin_usuario_page() -> rx.Component:
    return rx.grid(
        navbar_staff(),
        rx.grid(
            tabla_usuario_view(),
            form_crear_usuario_view(),
            grid_template_columns="85% 1fr",
            spacing="5",
            width="100%",
        ),
        credenciales_dialog(),
        spacing="5",
        width="100%",
        grid_template_columns="12% 1fr",
    )
