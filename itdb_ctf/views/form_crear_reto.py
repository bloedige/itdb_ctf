import reflex as rx

from itdb_ctf.components.form import select_catalog,input_box,text_area
from itdb_ctf.states.reto_states import CrearRetosState

def form_crear_reto()->rx.Component:
    return rx.dialog.root(
            rx.dialog.trigger(
                rx.button("Crear reto")
            ),
            rx.dialog.content(
                rx.center(
                    rx.vstack(
                        rx.heading("Crear Reto"),
                        input_box("Titulo",CrearRetosState.titulo,CrearRetosState.set_titulo,"text"),
                        text_area("Descripcion",CrearRetosState.descripcion,CrearRetosState.set_descripcion),
                        input_box("Flag de reto (se hashea)",CrearRetosState.flag,CrearRetosState.set_flag,"text"),
                        input_box("Puntaje inicial",CrearRetosState.puntaje_inicial,CrearRetosState.set_puntaje_inicial,"number"),
                        input_box("Puntaje minimo (opcional)",CrearRetosState.puntaje_minimo,CrearRetosState.set_puntaje_minimo,"number"),
                        select_catalog(CrearRetosState.categorias, "Categoria", CrearRetosState.set_id_categoria),
                        select_catalog(CrearRetosState.dificultades, "Dificultad", CrearRetosState.set_id_dificultad),
                        select_catalog(CrearRetosState.modos, "Modo de puntaje", CrearRetosState.set_id_modo_puntaje),
                        select_catalog(CrearRetosState.eventos, "Evento", CrearRetosState.set_id_evento),
                        ## subida de archivos
                        rx.upload(
                            rx.text("Arrastra o haz click para subir el archivo del reto."),
                            id="archivo_reto",
                            max_files=1,
                            border="1px dashed #888", padding="1em",
                        ),         
                        rx.cond(
                            CrearRetosState.nombre_subido != "",
                            rx.text(f"Adjunto: {CrearRetosState.nombre_subido}",color="green")
                        ),
                        rx.button("Guardar Reto", on_click=CrearRetosState.guardar_reto_completo(rx.upload_files(upload_id="archivo_reto"))),
                        rx.cond(CrearRetosState.mensaje != "", rx.text(CrearRetosState.mensaje)),
                        spacing="3", width="400px",
                    ),
                )       
            )
        )