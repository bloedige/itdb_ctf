import reflex as rx 
from itdb_ctf.states.reto_states import EditarRetosState
from itdb_ctf.components.form import select_catalog, input_box, text_area

def form_editar_reto_view(reto: dict) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                "Editar",
                on_click=lambda:EditarRetosState.cargar_reto(reto['id']),
                size="1", variant="soft",
            ),
        ),
        rx.dialog.content(
            rx.hstack(
                rx.vstack(
                    rx.heading("Editar reto"),
                    input_box("Titulo", EditarRetosState.titulo, EditarRetosState.set_titulo, "text"),
                    text_area("Descripción", EditarRetosState.descripcion, EditarRetosState.set_descripcion),
                    input_box("Flag nueva (vacia no cambia)", EditarRetosState.flag, EditarRetosState.set_flag, "text"),
                    input_box("Puntaje inicial", EditarRetosState.puntaje_inicial, EditarRetosState.set_puntaje_inicial, "number"),
                    input_box("Puntaje minimo (opcional)", EditarRetosState.puntaje_minimo, EditarRetosState.set_puntaje_minimo, "number"),
                    select_catalog(EditarRetosState.categorias, "Categoria", EditarRetosState.set_id_categoria,EditarRetosState.id_categoria),
                    select_catalog(EditarRetosState.dificultades, "Dificultad", EditarRetosState.set_id_dificultad, EditarRetosState.id_dificultad),
                    select_catalog(EditarRetosState.modos, "Modo de puntaje", EditarRetosState.set_id_modo_puntaje, EditarRetosState.id_modo_puntaje),
                    rx.hstack(
                        rx.dialog.close(
                            rx.button("Guardar", on_click=EditarRetosState.guardar, color_scheme="green"),
                        ),
                        rx.dialog.close(
                            rx.button("Cancelar", color_scheme="red"),
                        ),
                    ),

                    rx.cond(
                        EditarRetosState.mensaje != "", rx.badge(EditarRetosState.mensaje),
                    ),
                
                ),
                rx.vstack(
                    rx.text("Aqui van el tema de las pistas"),
                ),
            ),
        ),
        
    )
