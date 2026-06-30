import reflex as rx 
from itdb_ctf.states.reto_states import EditarRetosState
from itdb_ctf.components.form import select_catalog, input_box, text_area

def archivo_edit() -> rx.Component:
    return rx.vstack(
        rx.text("Archivo adjunto", weight="bold", size="2"),
        rx.match(
            EditarRetosState.accion_archivo,
            (
                "conservar",  
                rx.cond(
                    EditarRetosState.archivo_original != "",
                    rx.hstack(    
                        rx.icon("file", color="gray"),
                        rx.text(f"{EditarRetosState.archivo_original} se conserva.", color="gray", size="1"),
                        rx.spacer(),
                        rx.button(
                            "Quitar", color_scheme="red",
                            on_click=EditarRetosState.set_quitar,
                        ),
                    
                    ),
                    rx.hstack(    
                        rx.icon("file_up", color="gray"),
                        rx.text("Sin archivo / Subir arcivo", color="gray", size="1"),
                    ),      
                ),   
            ),
            (
                "quitar",
                rx.hstack(
                    rx.icon("file_x", color="red"),
                    rx.text(f"{EditarRetosState.archivo_original}", color="red", size="1"),
                    rx.spacer(),
                    rx.button("Cancelar", color_scheme="gray",size="1", variant="soft", 
                              on_click=EditarRetosState.set_conservar),
                ),
            ),
            (
                "remplazar",
                rx.hstack(
                    rx.icon("file_check",color="green"),
                    rx.text(f"{EditarRetosState.archivo_temp}", color_scheme="green"),
                    rx.button("Cancelar", color_scheme="gray",size="1", variant="soft", 
                              on_click=[EditarRetosState.set_conservar,rx.clear_selected_files("archivo_edit")]),
                ),
            ),
            ),
        rx.upload(
            rx.text("Arrastra o haz click para (subir / remplzar) el archivo del reto.", size="1"),
            id="archivo_edit",
            max_files=1,
            on_drop=EditarRetosState.on_drop_file(rx.upload_files(upload_id="archivo_edit")),
            border="1px dashed #888", padding="1em",
        ),   
        spacing="2", width="100%",
    )

def form_reto_edit() -> rx.Component:
    return rx.vstack(
        rx.heading("Editar reto"),
            input_box("Titulo", EditarRetosState.titulo, EditarRetosState.set_titulo, "text"),
            text_area("Descripción", EditarRetosState.descripcion, EditarRetosState.set_descripcion),
            input_box("Flag nueva (vacia no cambia)", EditarRetosState.flag, EditarRetosState.set_flag, "text"),
            input_box("Puntaje inicial", EditarRetosState.puntaje_inicial, EditarRetosState.set_puntaje_inicial, "number"),
            input_box("Puntaje minimo (opcional)", EditarRetosState.puntaje_minimo, EditarRetosState.set_puntaje_minimo, "number"),
            select_catalog(EditarRetosState.categorias, "Categoria", EditarRetosState.set_id_categoria,EditarRetosState.id_categoria),
            select_catalog(EditarRetosState.dificultades, "Dificultad", EditarRetosState.set_id_dificultad, EditarRetosState.id_dificultad),
            select_catalog(EditarRetosState.modos, "Modo de puntaje", EditarRetosState.set_id_modo_puntaje, EditarRetosState.id_modo_puntaje),    
    )

def form_pistas_edit() -> rx.Component:
    return rx.vstack(
        rx.heading("Pistas", size="3"),
        rx.divider(),
        rx.foreach(
            EditarRetosState.pistas_existentes,
            lambda p, i: rx.hstack(
                rx.text_area(
                    value=p['descripcion'],
                    on_change= lambda v:EditarRetosState.set_pista_existente_desc(i, v),
                ),
                rx.input(
                    value= p['costo'].to(str),
                    on_change=lambda v:EditarRetosState.set_pista_existente_costo(i, v), 
                    type="number",               
                ),
                rx.button(
                    rx.cond(p['activo'], "Desactivar","Activar"),
                    on_click=lambda: EditarRetosState.toggle_pista(p['id_pista']),
                    color_scheme=rx.cond(p['activo'],"red","green"),
                    size="1",            
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
                    rx.button("Quitar", on_click=lambda: EditarRetosState.quitar_pistas_nuevas(i),color_scheme="red"),
            ),
        ),
        rx.hstack(
            text_area("Descripcion de la nueva pista",EditarRetosState.pista_desc, EditarRetosState.set_pista_desc),
            rx.vstack(
                input_box("costo de pista", EditarRetosState.pista_costo, EditarRetosState.set_pista_costo, "number"),
                rx.button("+ Agregar pista", on_click=EditarRetosState.agregar_pista),
                spacing="2",
            ),
        ),

    )

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
            rx.vstack(
                rx.dialog.title(rx.spacer(),rx.dialog.close(rx.icon_button("x"))),
                rx.hstack(
                    rx.vstack(
                        form_reto_edit(),
                        archivo_edit(),
                    ),
                    form_pistas_edit(),
                ),
            ),
            rx.hstack(
                rx.spacer(),
                rx.button("Guardar", on_click=EditarRetosState.guardar_edit_completo, color_scheme="green"),
                rx.dialog.close(rx.button("Cancelar", color_scheme="red")),               
            ),
            rx.cond(
                EditarRetosState.mensaje != "", rx.badge(EditarRetosState.mensaje),
            ),
        ),
        
    )
