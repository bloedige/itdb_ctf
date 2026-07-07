import reflex as rx
from itdb_ctf.states.reto_states import ListarRetosState
from itdb_ctf.views.form_editar_reto_view import form_editar_reto_view

def fila_reto(reto:dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(reto['id']),
        rx.table.cell(reto['titulo']),
        rx.table.cell(reto['categoria']),
        rx.table.cell(reto['dificultad']),
        rx.table.cell(reto['modalidad']),
        rx.table.cell(reto['puntaje']),
        rx.table.cell(reto['minimo']),        
        rx.table.cell(
            rx.cond(
                reto['activo'],
                rx.badge("Activo",color_scheme="green"),
                rx.badge("Inactivo",color_scheme="gray"),                
            ),
        ),
        rx.table.cell(
            rx.hstack(
                rx.cond(
                    reto['edit'],
                    form_editar_reto_view(reto)
                ),
                rx.button(
                rx.cond(reto['activo'],"Desactivar","Activar"),
                on_click=lambda:ListarRetosState.alternar_activo(reto['id']),
                color_scheme=rx.cond(reto['activo'],"red","green"),
                size="1",
                variant="soft",
                ),
                spacing="2",
            ),
        ),  
    )

def tabla_retos_view()->rx.Component:
    return rx.vstack(
        rx.heading("Retos"),
        rx.card(
            rx.hstack(rx.icon("search", size=16 ),rx.text("Buscar",size="1")),
            rx.input(placeholder="Buscar por titulo...", value=ListarRetosState.busqueda, on_change=ListarRetosState.set_busqueda, size="1", ),
        ),
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("ID"),
                    rx.table.column_header_cell("Titulo"),
                    rx.table.column_header_cell("Categoria"),
                    rx.table.column_header_cell("Dificultad"),
                    rx.table.column_header_cell("Modo"),
                    rx.table.column_header_cell("Puntaje"),
                    rx.table.column_header_cell("Minimo"),
                    rx.table.column_header_cell("Estado"),
                    rx.table.column_header_cell("Acciones"),                    
                ),
            ),
            rx.table.body(
                rx.foreach(ListarRetosState.lista,fila_reto)
            ),  
            width="100%",
        ),
        spacing="2",
        width="100%",
    )