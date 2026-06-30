import reflex as rx

def select_catalog(opciones,placeholder,on_change,value=None)->rx.Component:
    return rx.select.root(
        rx.select.trigger(placeholder=placeholder),
        rx.select.content(
            rx.foreach(
                opciones,
                lambda par: rx.select.item(par[1],value=par[0])
            )
        ),
        on_change=on_change,
        value=value,
        width="100%",
    )

def input_box(placeholder,value,on_change,type)->rx.Component:
    return rx.input(
        placeholder=placeholder,
        on_change=on_change,
        value=value,
        type=type,
        width="100%",
    )


def text_area(placeholder,value,on_change)->rx.Component:
    return rx.text_area(
        placeholder=placeholder,
        value=value,
        on_change=on_change,
        width="100%",
    )