from sqlmodel import Session, select
from itdb_ctf.db import engine
from itdb_ctf.models import Evento,Modalidad,ModoPuntaje
from itdb_ctf.asociar.asociar_logic import estado_evento
from itdb_ctf.websockets.freeze_logic import esta_congelado
from itdb_ctf.websockets import canales
    
def validar_evento(id_modadlidad, id_modo_puntaje, fec_inicio, fec_fin, id_evento=None):
    etiqueta = etiqueta_modalidad(id_modadlidad) 
    mp = etiqueta_modo_puntaje(id_modo_puntaje)
    if etiqueta == "abierto":
        if existe_evento_abierto(id_evento):
            return "El evento abierto ya existe."
        if fec_inicio or fec_fin:
            return "El evento abierto no requiere fechas inicio / fin."
        if mp == "dinamico":
            return "El evento abierto debe ser de modo de puntaje estatico."
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

def etiqueta_modo_puntaje(id_modo_puntaje: int) -> str:
    with Session(engine) as s:
        modo_puntaje = s.get(ModoPuntaje, id_modo_puntaje)
        return modo_puntaje.etiqueta if modo_puntaje else "" 
    
def existe_evento_abierto(excluir_id=None) -> bool:
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
    
    error = validar_evento(id_modalidad,id_modo_puntaje, fec_inicio, fec_fin)
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
        id_ev = ev.id_evento
    canales.publicar_lista_eventos()
    return id_ev

def editar_evento(id_evento, values:dict):
    # Los 5 argumentos, en orden: faltaba id_modo_puntaje y todo se corria un
    # lugar (id_evento caia en fec_fin y excluir_id quedaba en None), asi que
    # editar el evento abierto chocaba con su propia existencia.
    error = validar_evento(
        values.get("id_modalidad"),
        values.get("id_modo_puntaje"),
        values.get("fec_inicio"),
        values.get("fec_fin"),
        id_evento,
    )
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
    canales.publicar_evento(id_evento)
    canales.publicar_lista_eventos()
    return True

def activar_desactivar_evento(id_evento) -> bool:
    with Session(engine) as s:
        ev = s.get(Evento, id_evento)
        if not ev: return False
        ev.activo = not ev.activo
        s.add(ev)
        s.commit()
    canales.publicar_evento(id_evento)
    canales.publicar_lista_eventos()
    return True
    
def listar_evento():
    with Session(engine) as s:
        stmt = (select(Evento, Modalidad.etiqueta, ModoPuntaje.etiqueta)
                      .join(Modalidad, Evento.id_modalidad == Modalidad.id_modalidad)
                      .join(ModoPuntaje, Evento.id_modo_puntaje == ModoPuntaje.id_modo_puntaje)
                      .order_by(Evento.id_modalidad)
                      .order_by(Evento.fec_fin.desc()))
        return[
            {
            "id":e.id_evento,
            "titulo":e.titulo,
            "descripcion":e.descripcion,
            "modalidad":m,
            "modo_puntaje":mp,
            "activo":e.activo,
            "auto_inscripcion":bool(e.auto_inscripcion),
            "freeze":esta_congelado(e.id_evento),
            "estado":estado_evento(e)
            } for e , m, mp in s.exec(stmt).all()
        ]

def obtener_evento(id_evento):
    with Session(engine) as s:
        ev = s.get(Evento,id_evento)
        if not ev:
           return None 
        return ev

def id_evento_abierto()->int:
    with Session(engine) as s:
        abierto = s.exec(select(Modalidad).where(Modalidad.etiqueta == "abierto")).first()
        ev = s.exec(select(Evento).where(Evento.id_modalidad == abierto.id_modalidad)).first()
        return ev.id_evento if ev else None

def catalogos(id_evento:int | None=None) -> dict:
    with Session(engine) as s:
        abierto = existe_evento_abierto()
        if not abierto or id_evento == id_evento_abierto():
            modalidades = [(str(m.id_modalidad),m.etiqueta) for m in s.exec(select(Modalidad).where(Modalidad.etiqueta != "cerrado")).all()]
            modos = [(str(mp.id_modo_puntaje), mp.etiqueta) for mp in s.exec(select(ModoPuntaje).where(ModoPuntaje.etiqueta != "dinamico")).all()]
        else:
            modalidades = [(str(m.id_modalidad),m.etiqueta) for m in s.exec(select(Modalidad).where(Modalidad.etiqueta != "abierto")).all()]
            modos = [(str(mp.id_modo_puntaje), mp.etiqueta) for mp in s.exec(select(ModoPuntaje)).all()]
        return {
            "modalidades":modalidades,
            "modos":modos,
        }