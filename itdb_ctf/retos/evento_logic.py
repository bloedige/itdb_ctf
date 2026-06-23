import os 
from sqlmodel import Session, select
from itdb_ctf.db import engine
from itdb_ctf.models import Evento,Modalidad



def id_evento_abierto()->int:
    titulo=os.environ.get("EVENTO_ABIERTO_TITULO", "Plataforma ITDB - Práctica Libre CTF")


    with Session(engine) as s:
        et = s.exec(select(Modalidad).where(Modalidad.etiqueta=="abierto")).one()
        ev = s.exec(select(Evento).where(Evento.titulo==titulo)).first() or s.exec(select(Evento).where(Evento.id_evento==1 and Evento.id_modalidad==et.id_modalidad))
        return ev.id_evento if ev else None