import reflex as rx 
from itdb_ctf.states.reto_states import EditarRetosState
from itdb_ctf.components.form import select_catalog, input_box, text_area, close_dialog_button, button, badge_msg

def archivo_edit() -> rx.Component:
    return rx.vstack(
        rx.text("Archivo adjunto", weight="bold", size="1"),
        rx.match(
            EditarRetosState.accion_archivo,
            (
                "conservar",  
                rx.cond(
                    EditarRetosState.archivo_original != "",
                    rx.badge(
                        rx.icon("file"),
                        rx.text(f"{EditarRetosState.archivo_original} se conserva."),
                        rx.spacer(),
                        button("Quitar", "red", EditarRetosState.set_quitar),
                        color_scheme= "gray",
                        size="3",
                        width="100%",
                        padding=".9em",
                    ), 
                    rx.badge( 
                        rx.spacer(),   
                        rx.icon("file_up"),
                        rx.text("Sin archivo / Subir arcivo", color="gray", size="1"),
                        rx.spacer(),
                        color_scheme= "gray",
                        size="3",
                        width="100%",
                        padding=".9em",
                    ),      
                ),   
            ),
            (
                "quitar",
                 rx.badge(
                        rx.icon("file_x"),
                        rx.text(f"{EditarRetosState.archivo_original} se elimina."),
                        rx.spacer(),
                        button("Cancelar", "gray", EditarRetosState.set_conservar),
                        color_scheme= "red",
                        size="3",
                        width="100%",
                        padding=".9em",
                    ),
                
            ),
            (
                "remplazar",
                rx.badge(
                        rx.icon("file_check"),
                        rx.text(f"{EditarRetosState.archivo_temp} se guarda."),
                        rx.spacer(),
                        button("Cancelar", "gray", [EditarRetosState.set_conservar, rx.clear_selected_files("archivo_edit")]),
                        color_scheme= "green",
                        size="3",
                        width="100%",
                        padding=".9em",
                    ),
            ),
            ),
        rx.upload(
            rx.text("Arrastra o haz click para (subir / remplzar) el archivo del reto.", size="1"),
            id="archivo_edit",
            max_files=1,
            on_drop=EditarRetosState.on_drop_file(rx.upload_files(upload_id="archivo_edit")),
            border="1px dashed #888", padding="1em",
            width="100%",
        ),   
        spacing="2",
        width="100%",
    )

def form_reto_edit() -> rx.Component:
    return rx.vstack(
        rx.heading("Editar reto", size="5"),
        input_box("Titulo", "Titulo...", EditarRetosState.titulo, EditarRetosState.set_titulo, "text"),
        text_area("Descripción", "Descripción...", EditarRetosState.descripcion, EditarRetosState.set_descripcion),
        rx.grid(    
            input_box("Flag", "Flag{...} nueva (vacia no cambia)", EditarRetosState.flag, EditarRetosState.set_flag, "text"),
            input_box("Puntaje inicial", "Pts...", EditarRetosState.puntaje_inicial, EditarRetosState.set_puntaje_inicial, "number"),
            input_box("Puntaje minimo", "Pts... (opcional)", EditarRetosState.puntaje_minimo, EditarRetosState.set_puntaje_minimo, "number"),
            select_catalog("Categoria", "Seleccionar...", EditarRetosState.categorias, EditarRetosState.set_id_categoria,EditarRetosState.id_categoria),
            select_catalog("Dificultad", "Seleccionar...", EditarRetosState.dificultades, EditarRetosState.set_id_dificultad, EditarRetosState.id_dificultad),
            select_catalog("Modo", "Seleccionar...", EditarRetosState.modos, EditarRetosState.set_id_modo_puntaje, EditarRetosState.id_modo_puntaje),    
            columns={"base":"1", "md":"2"},
            spacing="2",
            width="100%",
        ),
        spacing="2",
        width="100%",
    )

def form_pistas_edit() -> rx.Component:
    return rx.vstack(
        rx.heading("Pistas", size="5"),
        
        rx.foreach(
            EditarRetosState.pistas_existentes,
            lambda p, i: rx.hstack(
                text_area(
                    legend="Descripcion Pista",
                    placeholder="Descripción...",
                    value=p['descripcion'],
                    on_change= lambda v:EditarRetosState.set_pista_existente_desc(i, v),
                ),
                input_box(
                    legend="Costo pts.",
                    placeholder="Pts...",
                    value= p['costo'].to(str),
                    on_change=lambda v:EditarRetosState.set_pista_existente_costo(i, v), 
                    type="number",               
                ),
                rx.button(
                    rx.cond(p['activo'], "Desactivar","Activar"),
                    on_click=lambda: EditarRetosState.toggle_pista(p['id_pista']),
                    color_scheme=rx.cond(p['activo'],"red","green"),
                    size="1",
                    variant="soft",            
                ),
                spacing="2"  
            ),   
        ),
        rx.divider(),
        rx.text(
            rx.cond(
                EditarRetosState.pistas_nuevas.length() > 0,
                "Pistas nuevas",
                ""
            ),
        ),
        rx.foreach(
            EditarRetosState.pistas_nuevas,
            lambda p, i: rx.hstack(  
                    rx.text(f"{p['costo']} pts.", weight="bold", size="2"),
                    rx.text(f"{p['descripcion']}", weight="medium", size="1"),
                    rx.button(
                        "Quitar", 
                        on_click=lambda: EditarRetosState.quitar_pistas_nuevas(i),
                        color_scheme="red",
                        variant="soft",
                    ),
            ),
        ),
        rx.grid(
            text_area("Descripcion de pista", "Descripción...", EditarRetosState.pista_desc, EditarRetosState.set_pista_desc),
            rx.grid(
                input_box("Costo de pista","Pts...", EditarRetosState.pista_costo, EditarRetosState.set_pista_costo, "number"),
                button("Agregar pista", "cyan", EditarRetosState.agregar_pista),
                spacing="2",
                rows="2",
            ),
            spacing="2",
            columns={"base":"1","md":"2"},
            width="100%",
        ),
        width="100%",
    )

def form_editar_reto_view(reto: dict) -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                "Editar",
                on_click=[lambda:EditarRetosState.cargar_reto(reto['id']), EditarRetosState.open_close_dialog],
                size="1",
                variant="soft",
            ),
        ),
        rx.dialog.content(
            rx.grid(
                rx.grid(
                    form_reto_edit(),
                    archivo_edit(),
                    rows="auto",
                ),
                form_pistas_edit(),
                columns={"base":"1","md":"2"},
                spacing="5",
                width="100%",
            ),

            rx.grid(
                rx.cond(EditarRetosState.mensaje != "", badge_msg(EditarRetosState.mensaje, "red"),rx.spacer()),
                rx.hstack(
                    rx.spacer(),
                    button("Guardar", "green", EditarRetosState.guardar_edit_completo),
                    button("Cancelar", "red", EditarRetosState.open_close_dialog),
                    spacing="2",
                    width="100%",             
                ),
                rows="2",
                spacing="5",
                width="100%",
            ),
            close_dialog_button(EditarRetosState.open_close_dialog),
            width="100%",
            max_width="900px",
        ),
        open=EditarRetosState.dialog_bool,
    )
