import reflex as rx

def select_calatog(opciones,placeholder,on_change)->rx.Component:
    return rx.select.root(
        rx.select.trigger(placeholder=placeholder),
        rx.select.content(
            rx.foreach(
                opciones,
                lambda par: rx.select.item(par[1],value=par[0])
            )
        ),
        on_change=on_change
    )

def input_box(placeholder,value,on_change)->rx.Component:
    return rx.input(
        placeholder=placeholder,
        on_change=on_change,
        value=value
    )