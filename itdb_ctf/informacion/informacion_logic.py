from sqlmodel import Session
from itdb_ctf.db import engine
from itdb_ctf.models import Evento
from itdb_ctf.evento.evento_logic import id_evento_abierto

def obterner_info_abierto() -> str:
    with Session(engine) as s:
        id_abierto = id_evento_abierto()
        ev = s.get(Evento, id_abierto)
        return ev.descripcion if ev else ""