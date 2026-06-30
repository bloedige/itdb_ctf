import reflex as rx

from itdb_ctf.components.form import select_catalog,input_box,text_area
from itdb_ctf.states.reto_states import CrearRetosState
def archivo_up()->rx.Component:
    return rx.vstack(
        rx.cond(
            CrearRetosState.archivo_temp != "",
            rx.hstack(
                rx.icon("file_check", color="gray"),
                rx.text(f"{CrearRetosState.archivo_temp}"),
                rx.button("Cancelar", color_scheme="gray", on_click=[CrearRetosState.set_cancelar, rx.clear_selected_files("archivo_reto")])
            ),
            rx.hstack(
                rx.icon("file", color="gray"),
                rx.text("Sin archivo"),
            ),  
        ),
        ## subida de archivos
        rx.upload(
            rx.text("Arrastra o haz click para subir el archivo del reto."),
            id="archivo_reto",
            max_files=1,
            on_drop=CrearRetosState.on_drop_file(rx.upload_files(upload_id="archivo_reto")),
            border="1px dashed #888", padding="1em",
        ),  
    )

def form_reto()->rx.Component:
    return rx.vstack(
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
               
        rx.cond(
            CrearRetosState.nombre_subido != "",
            rx.text(f"Adjunto: {CrearRetosState.nombre_subido}",color="green")
        ),
    ),

def form_pistas()->rx.Component:
    return rx.vstack(
        rx.heading("Pistas (Opcional)"),
        rx.foreach(
            CrearRetosState.pistas,
            lambda p, i: rx.hstack(
                rx.text(f"{p['costo']}, pts.", weight="bold", size="1"),
                rx.text(f"{p['descripcion']}", size="1"),
                rx.spacer(),
                rx.button(
                    "Quitar",
                    on_click=lambda: CrearRetosState.quitar_pista(i),
                    color_scheme="red", size="1",
                ),
            width="100%"
            ),
        ),
        rx.divider(),
        rx.hstack(
            text_area("Descripcion de la pista", CrearRetosState.pista_desc, CrearRetosState.set_pista_desc ),
            rx.divider(orientation="vertical"),#borrar
            rx.vstack(
                rx.divider(orientation="vertical"),#borrar
                input_box("Costo de puntas", CrearRetosState.pista_costo, CrearRetosState.set_pista_costo, "number"),
                rx.button(
                    "Agregar pista",
                    on_click=CrearRetosState.agregar_pista,
                    size="2", variant="soft",
                ),
                width="30%"
            ),
            spacing="2", width="100%",
        ),

    )



def form_crear_reto()->rx.Component:
    return rx.dialog.root(
            rx.dialog.trigger(
                rx.button("Crear reto")
            ),
            rx.dialog.content(
                rx.hstack(
                    rx.vstack(
                        form_reto(),
                        archivo_up(),
                    ),
                    rx.separator(orientation="vertical"),
                    form_pistas(),
                ),
                
                rx.hstack(
                    rx.spacer(),
                    rx.button("Guardar Reto", on_click=CrearRetosState.guardar_reto_completo),
                    rx.dialog.close(rx.button("Cancelar", on_click=CrearRetosState.set_cancelar, color_scheme="red"),),
                ),
                rx.cond(CrearRetosState.mensaje != "", rx.text(CrearRetosState.mensaje)),
                spacing="2", width="50%",              
            ),
            width="800px"
        )