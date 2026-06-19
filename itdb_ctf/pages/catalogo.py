import reflex as rx
from sqlmodel import select, Session
from itdb_ctf.db import engine
from itdb_ctf.models import Reto, Categoria, Dificultad, Evento
from itdb_ctf.auth.auth_state import AuthState
from itdb_ctf.components.navbar import navbar

class CatalogoState(AuthState):
    retos:list[dict]=[]
    filtro_categoria:str=""
    filtro_dificultad:str=""
    ## añadir filtro de eventos
    def cargar_retos(self):
        guard = self.requiere_login()
        if guard:
            return guard
        with Session(engine) as s:
            stmt=select(Reto).where(Reto.activo==True)
            if self.filtro_categoria:
                stmt=stmt.where(Reto.id_categoria==int(self.filtro_categoria))
            if self.filtro_dificultad:
                stmt=stmt.where(Reto.id_dificultad==int(self.filtro_dificultad))
            filas=s.exec(stmt).all()

            self.retos=[
                {
                    "id":r.id_reto,
                    "categoria":r.id_categoria,
                    "dificultad":r.id_dificultad,
                    "titulo":r.titulo,
                    "descripcion":r.descripcion,
                    "puntaje":r.puntaje_inicial,
                    "original":r.archivo_original
                }      
                for r in filas             
            ]
## áñadir creador de reto
def tarjeta_reto(reto: dict)->rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.card(
            rx.vstack(
                rx.heading(reto['titulo'],size="4"),
                rx.text(f"{reto['puntaje']} pts."),
                spacing="2",
            ),
        ),
        ),
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.hstack(
                        rx.badge("cate"),
                        rx.badge("difi"),
                    ),
                    rx.spacer(),
                    rx.dialog.close(rx.button(rx.icon("heart"))),
                ),
                rx.dialog.title(reto['titulo']),
                rx.dialog.title(reto['puntaje']),
                rx.divider(),
                rx.dialog.description(reto['descripcion']),
                rx.link(reto['original'],href=f"http://localhost:8000/api/reto/{reto['id']}/descarga"),
                rx.hstack(
                    rx.input(placeholder="flag{...}"),
                    rx.button("Encvia")
                )


            )
           
        )      
    #href=f"/reto/{reto['id']}",
    )
    



def catalogo_page()->rx.Component:
    return rx.vstack(
        navbar(),
        rx.center(
            rx.heading("Retos"),
            rx.foreach(CatalogoState.retos, tarjeta_reto),
            spacing="3",
        )

    )