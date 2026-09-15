import reflex as rx
from itdb_ctf.components.form import select_catalog,input_box,text_area,card_text, button, badge_msg, close_dialog_button
from itdb_ctf.reto.reto_states import CrearRetosState, EditarRetosState, ListarRetosState

def archivo_up()->rx.Component:
    return rx.vstack(
        rx.cond(
            CrearRetosState.archivo_temp != "",
            rx.badge(              
                rx.icon("file_check"),
                rx.text(CrearRetosState.archivo_temp),
                rx.spacer(),
                rx.button("Cancelar", color_scheme="gray", on_click=[CrearRetosState.set_cancelar, rx.clear_selected_files("archivo_reto")], size="1", aling="right", variant="solid"),
                color_scheme= "jade",
                size="2",
                width="100%",    
            ), 
            rx.badge(
                rx.spacer(),
                rx.icon("file"),
                rx.text("Sin archivo"),
                rx.spacer(),
                color_scheme= "gray",
                size="2",
                width="100%",   
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
        spacing="3",
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
                card_text("Descripción de pista", f"{p['descripcion']}"),
                card_text("Costo de pista", f"{p['costo']}, pts."),
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

def form_crear_reto_view()->rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(rx.button(rx.icon("plus"), "Crear reto", on_click=CrearRetosState.open_close_dialog, variant="solid", color_scheme="jade")),
        rx.dialog.content(
            rx.grid(
                rx.grid(
                    form_reto(),
                    archivo_up(),
                    rows="auto",
                    spacing="2",
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

def button_edit(id_reto) -> rx.Component:
    return rx.button(
        "Editar",
        on_click=EditarRetosState.cargar_reto(id_reto),
        size="1",
        variant="solid",
    ),

def form_editar_reto_view() -> rx.Component:
    return rx.dialog.root(
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

def fila_reto(reto:dict) -> rx.Component:
    return rx.table.row(
        rx.table.cell(reto['id']),
        rx.table.cell(reto['titulo']),
        rx.table.cell(reto['categoria']),
        rx.table.cell(reto['dificultad']),
        rx.table.cell(reto['modo_puntaje']),
        rx.table.cell(reto['puntaje']),
        rx.table.cell(reto['minimo']),        
        rx.table.cell(
            rx.cond(
                reto['activo'],
                rx.text("Activo",color_scheme="jade"),
                rx.text("Inactivo",color_scheme="gray"),                
            ),
        ),
        rx.table.cell(
            rx.grid(
                rx.cond(
                    reto['edit'],
                    rx.grid(
                        button_edit(reto['id']),
                        rx.button(
                        rx.cond(reto['activo'],"Desactivar","Activar"),
                        on_click=lambda:ListarRetosState.alternar_activo(reto['id']),
                        color_scheme=rx.cond(reto['activo'],"ruby","jade"),
                        size="1",
                        variant="solid",
                        ),
                        columns="2",
                        place_items="center",
                    ),
                    None,
                ),
            ),
        ),  
    )

def fila_reto_movil(reto:dict) -> rx.Component:
    return rx.card(
        rx.flex(
            rx.text(reto['titulo'], size="2", weight="medium"),
            rx.cond(
                reto['edit'],
                rx.grid(
                    button_edit(reto['id']),
                    rx.button(
                        rx.cond(reto['activo'],"Desactivar","Activar"),
                        on_click=lambda:ListarRetosState.alternar_activo(reto['id']),
                        color_scheme=rx.cond(reto['activo'],"ruby","jade"),
                        size="1",
                        variant="solid",
                    ),
                    columns="2",
                    place_items="center",
                ),
                None,
            ),
            justify="between",
            width="100%",
        ),
        width="100%",
    )

def tabla_retos_view()->rx.Component:
    return rx.vstack(
        rx.tablet_and_desktop(
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
            width="100%",
        ),
        rx.mobile_only(
            rx.vstack(
                rx.grid(
                    rx.text("Titulo", size="1", weight="medium"),
                    rx.text("Acciones", size="1", weight="medium"),
                    grid_template_columns="1fr 30%",
                    width="100%",
                ),
                rx.foreach(ListarRetosState.lista, fila_reto_movil),
                spacing="2",
                width="100%",
            ),
            width="100%",
        ),
        spacing="2",
        width="100%",
    )


def retos_view() -> rx.Component:
    return rx.flex(
        rx.card(
            rx.flex(
                rx.heading("Gestion — Retos", size="4"),
                rx.grid(
                    input_box("Buscar", "Buscar por titulo...", ListarRetosState.busqueda, ListarRetosState.set_busqueda, "text"),
                    form_crear_reto_view(),
                    width="100%",
                    grid_auto_flow="column",
                    place_items="center",
                    spacing="5",
                ),
                width="100%",
                direction="column",
                spacing="3",
            ),
            position="sticky",
            top="0",
            width="100%",
            z_index="99",
        ),
        tabla_retos_view(),
        form_editar_reto_view(),
        align="center",
        direction="column",
        width=rx.breakpoints(sm="95%", md="90%"),
        spacing="4",
    )