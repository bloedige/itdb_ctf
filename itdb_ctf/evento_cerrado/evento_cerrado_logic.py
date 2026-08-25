from sqlmodel import Session, select
from itdb_ctf.db import engine
from itdb_ctf.models import Evento, EstadoInscripcion, Participa
from itdb_ctf.asociar.asociar_logic import estado_evento
from itdb_ctf.evento.evento_logic import etiqueta_modalidad

def estado_inscripcion(id_usuario:int, id_evento:int) -> tuple[bool,str]:
    with Session(engine) as s:
        et_part = s.exec(select(EstadoInscripcion.etiqueta)
            .join(Participa, EstadoInscripcion.id_estado_inscripcion == Participa.id_estado_inscripcion)
            .where(
                Participa.id_usuario == id_usuario,
                Participa.id_evento == id_evento,
        )).first()
        if not et_part:
            return False, "No estas inscrito en este evento."
        if et_part == "descalificado":
            return False, "Has sido desacalificado de el evento."
        return True, ""

def acceso_evento_cerrado(id_evento:int, id_usuario:int) -> tuple[bool,str]:
    with Session(engine) as s:
        ev = s.get(Evento, id_evento)
        if not ev or not ev.activo or etiqueta_modalidad(ev.id_modalidad) != "cerrado":
            return False, "Evento no encontrado."
        est = estado_evento(ev)
        if est == "concluido":
            return False, "Evento culminado."
        if est == "futuro":
            return False, "El evento aún no inicia."
        ok, msg = estado_inscripcion(id_usuario, id_evento)
        
        return ok, msg
        

def info_evento_cerrado(id_evento:int) -> dict | None:
    with Session(engine) as s:
        ev = s.get(Evento,id_evento)
        if not ev or not ev.activo or etiqueta_modalidad(ev.id_modalidad) != "cerrado":
            return None
        return{
            "titulo": ev.titulo,
            "descripcion":ev.descripcion,
            "fec_inicio": ev.fec_inicio,
            "fec_fin": ev.fec_fin,
            "estado_evento": estado_evento(ev),
        }