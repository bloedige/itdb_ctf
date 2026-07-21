import reflex as rx
from itdb_ctf.states.usuario_states import ListarUsuarioState
from itdb_ctf.views.form_editar_usuario_view import form_editar_usuario_view
from itdb_ctf.views.credenciales_usuario_view import alert_reset_password, alert_estado
from itdb_ctf.components.form import select_catalog, input_box

def fila_usuario(u:dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(
            rx.hstack(
                rx.text(u['alias'], color_scheme=rx.cond(u['mismo'], "blue", "")),
                rx.cond(u['mismo'], rx.text("tú",color_scheme="blue")),
                spacing="2",
            ),          
        ),
        rx.table.cell(rx.text(u['email_inst'],color_scheme=rx.cond(u['mismo'], "blue", ""))),
        rx.table.cell(
            rx.match(
                u['codigo'],
                ("superadmin", rx.text(u['rol'], color_scheme=rx.cond(u['mismo'], "blue", ""))),
                ("admin", rx.text(u['rol'], color_scheme=rx.cond(u['mismo'], "blue", ""))),
                ("autor", rx.text(u['rol'], color_scheme=rx.cond(u['mismo'], "blue", ""))),
                rx.text(u['rol'], color_scheme="gray"),
            ),
        ),
        rx.table.cell(
            rx.cond(
                u['metodo'] != "local",
                rx.text(u['metodo'], color_scheme="blue"),
                rx.text(u['metodo'], color_scheme=rx.cond(u['mismo'], "blue", "gray")),
            ),
        ),
        rx.table.cell(
            rx.cond(
                u['activo'],
                rx.text("Activo", color_scheme="jade"),
                rx.text("Inactivo", color_scheme="gray"),
            )
        ),       
        rx.table.cell(    
            rx.grid(
                rx.cond(
                    u['edit'], 
                    form_editar_usuario_view(u['id_usuario']),
                    rx.spacer(),
                ),
                rx.cond(
                    u['reset'],
                    alert_reset_password(u['id_usuario'], u['email_inst'], u['alias'], u['rol']),
                    rx.spacer(),
                ),
                rx.cond(
                    u['estado'],
                    alert_estado(u['id_usuario'],u['activo'],u['email_inst']),
                    rx.spacer(),
                ),
                place_items="center",
                columns="3",
                width="100%",
                spacing="2",
            ),  
        ),
        rx.table.cell(rx.text(u['reset'])),
        bg=rx.cond(
            u['mismo'],
            "#3b83f637",
            rx.cond(
                ~u['estado'],
                "#80808045",
                "",
            )
        )
    )

def filtros() -> rx.Component:
    return rx.card(
        rx.heading("Filtros", size="3"),
        rx.grid(
            input_box("Buscar por correo", "example@example.com", ListarUsuarioState.busqueda, ListarUsuarioState.set_busqueda, "email"),
            select_catalog("Filtrar por rol","Todos...", ListarUsuarioState.roles, ListarUsuarioState.set_id_rol_filtro, ListarUsuarioState.id_rol_filtro),
            select_catalog("Filtrar por metodo auth","Todos...", ListarUsuarioState.metodos , ListarUsuarioState.set_id_metodo_filtro, ListarUsuarioState.id_metodo_filtro),
            select_catalog("Filtrar por estado", "todos..", ListarUsuarioState.estados, ListarUsuarioState.set_activo_filtro, ListarUsuarioState.activo_filtro),
            grid_template_columns="40% 1fr 1fr 1fr",
            place_items="center",
            width="100%",
            spacing="2",
        ),
        width="100%",
    )


def tabla_usuario_view() -> rx.Component:
    return rx.vstack(
        rx.card(
            filtros(),
            width="100%",
        ),
        rx.card(
            rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Alias"),
                    rx.table.column_header_cell("Correo"),
                    rx.table.column_header_cell("Rol"),
                    rx.table.column_header_cell("Metodo"),
                    rx.table.column_header_cell("Estado"),
                    rx.table.column_header_cell("Acciones"),
                ),
            ),
            rx.table.body(rx.foreach(ListarUsuarioState.lista, fila_usuario)),
            width="100%",
            ),
            width="100%",
        ),
        spacing="5",
        width="100%",
    )