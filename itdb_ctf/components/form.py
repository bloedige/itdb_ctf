import reflex as rx

def select_catalog(legend, placeholder, opciones, on_change, value=None)->rx.Component:
    return rx.box(
        rx.text(
            legend, 
            size="1", 
            eight="light",
        ),
        rx.select.root(
            rx.select.trigger(placeholder=placeholder, width="100%",),
            rx.select.content(
                rx.foreach(
                    opciones,
                    lambda par: rx.select.item(par[1],value=par[0])
                ),
                width="100%",
            ),
            width="100%",
            on_change=on_change,
            value=value,
        ),
        width="100%",
    )

def input_box(legend, placeholder, value, on_change, type, disabled=None)->rx.Component:
    return rx.box(
        rx.text(
            legend,
            size="1",
            weight="light",
            ),
        rx.input(
            placeholder=placeholder,
            on_change=on_change,
            value=value,
            type=type,
            width="100%",
            disabled=disabled,
        ),
        width="100%",
    )
    
def text_area(legend, placeholder, value, on_change)->rx.Component:
    return rx.box(
        rx.text(
            legend,
            size="1",
            weight="light",
        ),
        rx.text_area(
            placeholder=placeholder,
            value=value,
            on_change=on_change,
            width="100%",
        ),
        width="100%",
    )

def input_datetime(legend, value, on_change, disabled=False) -> rx.Component:
    return rx.box(
        rx.text(
            legend,
            size="1",
            weight="light"
        ),
        rx.input(
            value=value,
            on_change=on_change,
            type="datetime-local",
            disabled=disabled,
        )
    )

def checked(legend, checked, on_change, disabled=None) -> rx.Component:
    return rx.box(
        rx.checkbox(
            legend,
            checked=checked,
            on_change=on_change,
            disabled=disabled,
        ),
    )
def badge_msg(msg, color) -> rx.Component:
    return rx.center(
        rx.text(
            msg,
            color=color,
            size="1",
            weight="light",
        ),
        width="100%",
        spacing="2",
    )
def card_text(legend, value) -> rx.Component:
    return rx.box(
        rx.text(
            legend,
            weight="bold",
            size="1",
        ),
        rx.text(
            value,
            weight="regular",
            size="1",
        ),
        width="100%",
        spacing="2",
    )

def close_dialog_button(actions) -> rx.Component:
    return rx.button(
                rx.icon("x",color="gray", size=16, stroke_width=3),
                on_click=actions,
                variant="ghost",
                color_scheme="gray",
                position="absolute",
                top=".9em",
                right=".9em",
            ), 

def button(legend, color, actions, disabled=None, size=None) -> rx.Component:
    return rx.button(
        legend,
        color_scheme=color,
        on_click=actions,
        variant="surface",
        disabled=disabled, 
        size=size,                      
    )

