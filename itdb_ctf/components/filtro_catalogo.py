import reflex as rx

def chip(texto, valor, filtro_actual, on_click, color)->rx.Component:
    return rx.button(
        texto,
        on_click=on_click(valor),
        variant=rx.cond(filtro_actual==valor,"solid","outline"),
        size="2",
        color_scheme=color,
    )

def filtro(values, id_value, set_id_value, color, legend)->rx.Component:
    return rx.vstack(
        rx.text(legend, size="1", weight="medium"),
        rx.flex(
            rx.foreach(
                values,
                lambda par: chip(par[1], par[0], id_value, set_id_value, color),
            ),
            wrap="wrap", spacing="2",
        ),
        spacing="2",
        width="100%",
    )

def filtros(cats, id_cat, set_id_cat, difs, id_dif, set_id_dif, color)->rx.Component:
    return rx.vstack(
        filtro(cats, id_cat, set_id_cat, color, "Categoría"),
        filtro(difs, id_dif, set_id_dif, color, "Dificultad"),
        width="100%",
        spacing="5",
    )