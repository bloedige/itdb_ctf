from sqlmodel import Session, select
from itdb_ctf.db import engine
from itdb_ctf.models import Evento,Modalidad,ModoPuntaje
    
def validar_evento(id_modadlidad, fec_inicio, fec_fin, id_evento=None):
    etiqueta = etiqueta_modalidad(id_modadlidad) 
    if etiqueta == "abierto":
        if existe_evento_avierto(id_evento):
            return "El evento abierto ya existe."
        if fec_inicio or fec_fin:
            return "El evento abierto no requiere fechas inicio / fin."
    elif etiqueta == "cerrado":
        if not (fec_inicio and fec_fin):
            return "EL evento cerrado requiere de fecha inicio y fin."
        if fec_fin <= fec_inicio:
            return "la fecha de fin deve ser posterior a la de inicio."
    return None

def etiqueta_modalidad(id_modalidad: int) -> str:
    with Session(engine) as s:
        modalidad = s.get(Modalidad, id_modalidad)
        return modalidad.etiqueta if modalidad else "" 

def existe_evento_avierto(excluir_id=None) -> bool:
    with Session(engine) as s:
        abierto = s.exec(select(Modalidad).where(Modalidad.etiqueta == "abierto")).first()
        if not abierto:
            return False
        stmt = select(Evento).where(Evento.id_modalidad == abierto.id_modalidad)
        if excluir_id is not None:
            stmt = stmt.where(Evento.id_evento != excluir_id)
        return s.exec(stmt).first() is not None
    
def crear_evento(id_usuario,id_modalidad,id_modo_puntaje,titulo,descripcion=None,
                 fec_inicio=None,fec_fin=None,auto_inscripcion=False):
    
    error = validar_evento(id_modalidad, fec_inicio, fec_fin)
    if error:
        raise ValueError(error)
    with Session(engine)as s:
        ev = Evento(
            id_usuario=id_usuario,
            id_modalidad=id_modalidad,
            id_modo_puntaje=id_modo_puntaje,
            titulo=titulo,
            descripcion=descripcion,
            fec_inicio=fec_inicio,
            fec_fin=fec_fin,
            auto_inscripcion=auto_inscripcion,
        )
        s.add(ev)
        s.commit()
        s.refresh(ev)
    return ev.id_evento

def editar_evento(id_evento, values:dict):
    error = validar_evento(values.get("id_modalidad"), values.get("fec_inicio"), values.get("fec_fin"), id_evento)
    if error:
        raise ValueError(error)
    with Session(engine) as s:
        ev = s.get(Evento, id_evento)
        if not ev:
            return None
        for campo,valor in values.items():
            setattr(ev, campo, valor)
        s.add(ev)
        s.commit()
        return True

def activar_desactivar_evento(id_evento) -> bool:
    with Session(engine) as s:
        ev = s.get(Evento, id_evento)
        if not ev: return False
        ev.activo = not ev.activo
        s.add(ev)
        s.commit()
        return True
    
def listar_evento():
    with Session(engine) as s:
        stmt = (select(Evento, Modalidad.etiqueta, ModoPuntaje.etiqueta)
                      .join(Modalidad, Evento.id_modalidad == Modalidad.id_modalidad)
                      .join(ModoPuntaje, Evento.id_modo_puntaje == ModoPuntaje.id_modo_puntaje))
        return[
            {
            "id":e.id_evento,
            "titulo":e.titulo,
            "descripcion":e.descripcion,
            "modalidad":m,
            "modo_puntaje":mp,
            "activo":e.activo,
            "auto_inscripcion":bool(e.auto_inscripcion),
            "freeze":bool(e.freeze),
            } for e , m, mp in s.exec(stmt).all()
        ]
        
def freeze_scoreboard(id_evento) -> bool:
    with Session(engine) as s:
        ev =  s.get(Evento, id_evento)
        if not ev: return False
        ev.freeze = not ev.freeze
        s.add(ev)
        s.commit()
        return True

def obtener_evento(id_evento):
    with Session(engine) as s:
        ev = s.get(Evento,id_evento)
        return ev

def id_evento_abierto()->int:
    with Session(engine) as s:
        abierto = s.exec(select(Modalidad).where(Modalidad.etiqueta == "abierto")).first()
        ev = s.exec(select(Evento).where(Evento.id_modalidad == abierto.id_modalidad)).first()
        return ev.id_evento if ev else None