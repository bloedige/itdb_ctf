
from sqlmodel import Session, select
from itdb_ctf.db import engine
from itdb_ctf.models import Evento, Participa, EstadoInscripcion, ModoPuntaje
from itdb_ctf.asociar.asociar_logic import estado_evento
from itdb_ctf.websockets import canales

def et_inscrito(s:Session) -> int:
    et = s.exec(select(EstadoInscripcion).where(EstadoInscripcion.etiqueta == "inscrito")).first()
    return et.id_estado_inscripcion if et else None

def auto_inscripcion( id_evento:int, id_usuario:int) -> tuple[bool,str]:
    with Session(engine) as s:
        ev = s.get(Evento, id_evento)
        if not ev or not ev.auto_inscripcion:
            return False, "Evento inexistente o no válido para incripción."
        est = estado_evento(ev)
        if est == "concluido":
            return False, "Evento finalizado."
        inscrito = s.exec(select(Participa).where(
            Participa.id_usuario == id_usuario,
            Participa.id_evento == id_evento)).first()
        if inscrito:
            return False, "Ya estás inscrito en este evento."
        id_estado = et_inscrito(s)
        if id_estado is None:
            return False, "Estado no encontrado."
        s.add(Participa(
            id_usuario=id_usuario,
            id_evento=id_evento,
            id_estado_inscripcion=id_estado,
            ))
        s.commit()
    canales.publicar_inscripcion(id_evento)
    return True, "Inscrito con exito."

def eventos(id_usuario:int) -> list[dict]:
    with Session(engine) as s:
        participaciones = s.exec(select(Participa.id_evento, EstadoInscripcion.etiqueta)
            .join(EstadoInscripcion, Participa.id_estado_inscripcion == EstadoInscripcion.id_estado_inscripcion)
            .where(Participa.id_usuario == id_usuario)).all()

        part_dict={id_ev: et for id_ev, et in participaciones}
        
        stmt = (select(Evento, ModoPuntaje.etiqueta)
            .join(ModoPuntaje, Evento.id_modo_puntaje == ModoPuntaje.id_modo_puntaje)
            .where(Evento.activo == True).order_by(Evento.fec_fin.desc()))
    return [
        {
            "id_evento_cerrado":ev.id_evento,
            "titulo":ev.titulo,
            "descripcion":ev.descripcion or "",
            "modo":md,
            "fec_inicio":ev.fec_inicio,
            "fec_fin":ev.fec_fin,
            "auto_inscripcion":ev.auto_inscripcion,
            "inscrito":ev.id_evento in part_dict,
            "estado_usuario":part_dict.get(ev.id_evento), 
            "estado_evento":estado_evento(ev),   
        }for ev, md in s.exec(stmt).all() if estado_evento(ev) != "abierto"
    ] 

    