import reflex as rx
from itdb_ctf.components.navbar import navbar_staff
from itdb_ctf.usuario.form_editar_usuario_view import form_editar_usuario_view
from itdb_ctf.usuario.tabla_usuarios_view import tabla_usuario_view
from itdb_ctf.usuario.credenciales_usuario_view import credenciales_dialog

def admin_usuario_page() -> rx.Component:
    return rx.grid(
        navbar_staff(),
        tabla_usuario_view(),
        credenciales_dialog(),
        form_editar_usuario_view(),
        grid_template_columns=rx.breakpoints(initial="1fr", md="12% 1fr"),
        width="100%",
        justify_items="center",
        spacing="4",
    )
