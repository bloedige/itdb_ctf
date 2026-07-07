import reflex as rx

from itdb_ctf.components.form import select_catalog,input_box,text_area,card_text, button, badge_msg, close_dialog_button
from itdb_ctf.states.reto_states import CrearRetosState

def archivo_up()->rx.Component:
    return rx.vstack(
        rx.cond(
            CrearRetosState.archivo_temp != "",
            rx.badge(
                rx.icon("file_check"),
                rx.text(CrearRetosState.archivo_temp),
                rx.spacer(),
                rx.button("Cancelar", color_scheme="gray", on_click=[CrearRetosState.set_cancelar, rx.clear_selected_files("archivo_reto")]),
                color_scheme= "green",
                size="3",
                width="100%",
                padding=".9em",
            ), 
            rx.badge(
                rx.spacer(),
                rx.icon("file"),
                rx.text("Sin archivo"),
                rx.spacer(),
                color_scheme= "gray",
                size="3",
                width="100%",
                padding=".9em", 
            ),  
        ),
        ## subida de archivos
        rx.upload(
            rx.text("Arrastra o haz click para subir el archivo del reto."),
            id="archivo_reto",
            max_files=1,
            on_drop=CrearRetosState.on_drop_file(rx.upload_files(upload_id="archivo_reto")),
            border="1px dashed #888", padding="1em",
            width="100%",
        ), 
        width="100%", 
        spacing="2",
    )

def form_reto()->rx.Component:
    return rx.vstack(
        rx.heading("Crear Reto", size="5"),
        input_box("Titulo", "Titulo...", CrearRetosState.titulo, CrearRetosState.set_titulo, "text"),
        text_area("Descripción","Descripción...",CrearRetosState.descripcion,CrearRetosState.set_descripcion),
        input_box("Flag", "flag{...}",CrearRetosState.flag,CrearRetosState.set_flag,"text"),
        rx.grid(
            input_box("Punataje inicial", "Pts...",CrearRetosState.puntaje_inicial,CrearRetosState.set_puntaje_inicial,"number"),
            input_box("Puntaje minimo", "Pts... (opcional)",CrearRetosState.puntaje_minimo,CrearRetosState.set_puntaje_minimo,"number"),
            select_catalog("Categoria", "Seleccionar...", CrearRetosState.categorias, CrearRetosState.set_id_categoria),
            select_catalog("Dificultad", "Seleccionar...", CrearRetosState.dificultades, CrearRetosState.set_id_dificultad),
            select_catalog("Modo de puntaje", "Seleccionar...", CrearRetosState.modos, CrearRetosState.set_id_modo_puntaje),
            columns={"base":"1","md":"2"},
            spacing="2",
            width="100%" 
        ),
        select_catalog("Evento", "Seleccionar...", CrearRetosState.eventos, CrearRetosState.set_id_evento),              
        width="100%",
        spacing="2",
    ),

def form_pistas()->rx.Component:
    return rx.vstack(
        rx.heading("Pistas (Opcional)", size="5"),
        rx.foreach(
            CrearRetosState.pistas,
            lambda p, i: rx.hstack(
                card_text("Costo de pista", f"{p['costo']}, pts."),
                card_text("Descripción de pista", f"{p['descripcion']}"),
                rx.spacer(),
                rx.button(
                    "Quitar",
                    on_click=lambda: CrearRetosState.quitar_pista(i),
                    color_scheme="red", size="1", variant="soft",  
                ),
            width="100%"
            ),
        ),
        rx.grid(
            text_area("Descripción de pista", "Descripción...", CrearRetosState.pista_desc, CrearRetosState.set_pista_desc),
            rx.grid(
                input_box("Costo de pista", "Pts...", CrearRetosState.pista_costo, CrearRetosState.set_pista_costo, "number"),
                button("Agregar pista","cyan",[CrearRetosState.agregar_pista]),
                spacing="2",
                columns={"base":"2","md":"1"},
                rows={"base":"2","md":"1"},
            ),
            columns={"base":"1","md":"2"},
            spacing="2", 
            width="100%", 
        ),
        width="100%",
    )

def form_crear_reto()->rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button("Crear reto", on_click=CrearRetosState.open_close_dialog)
        ),
        rx.dialog.content(
            rx.grid(
                rx.grid(
                    form_reto(),
                    archivo_up(),
                    rows="auto",
                ),
                form_pistas(),
                columns={"base":"1", "md":"2"},
                spacing="5",
                whidth="100%",
            ),
            rx.grid(
                rx.cond(CrearRetosState.mensaje != "", badge_msg(CrearRetosState.mensaje, "red"),rx.spacer()),
                rx.hstack(
                    rx.spacer(),
                    button("Guardar", "green", [CrearRetosState.guardar_reto_completo]),
                    button("Cancelar", "red", [CrearRetosState.limpiar, CrearRetosState.open_close_dialog]),
                    spacing="2",
                    width="100%",
                ),
                rows="2",
                spacing="5",
                width="100%",
            ),
            close_dialog_button(CrearRetosState.open_close_dialog),     
            width="100%",
            max_width="900px",
        ),
        on_open_change=CrearRetosState.set_drop_mensaje,
        open=CrearRetosState.dialog_bool,
    )