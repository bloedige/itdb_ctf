from itdb_ctf.db import engine
from sqlmodel import Session, select
from itdb_ctf.models import Compra, Pista
from itdb_ctf.core.puntaje_logic import puntaje_total_usuario
from itdb_ctf.websockets import canales

def adquirir_pista(id_usuario:int, id_evento:int, id_reto:int, id_pista:int) -> tuple[bool, str]:
    with Session(engine) as s:
        pista = s.get(Pista, id_pista)
        if not pista:
            return False, "Pista inexistente"
        ad = s.exec(select(Compra).where(
            Compra.id_usuario == id_usuario,
            Compra.id_evento == id_evento,
            Compra.id_reto == id_reto,
            Compra.id_pista == id_pista)).first()
        if ad:
            return False, "Pista adquirida"
        saldo = puntaje_total_usuario(s, id_usuario, id_evento)
        if pista.costo > saldo:
            return False, "Puntos insuficientes para adquirir la pista"
        s.add(Compra(
            id_pista=id_pista,
            id_reto =id_reto,
            id_usuario = id_usuario,
            id_evento = id_evento,
            puntos_usados = pista.costo,
        ))
        s.commit()
        # el saldo del comprador cambió -> refrescar scoreboard + su vista de retos
        canales.publicar_scoreboard(id_evento)
        canales.publicar_evento(id_evento)
        return True, "Pista adquirida."

