from sqlmodel import Session, select
from itdb_ctf.db import engine
from itdb_ctf.models import Evento, Contiene, Reto, Categoria
from datetime import datetime, timezone

def estado_evento(ev) -> str:
    if not ev.fec_inicio:
        return "abierto"
    now = datetime.now(timezone.utc)
    fi = ev.fec_inicio if ev.fec_inicio.tzinfo else ev.fec_inicio.replace(tzinfo=timezone.utc)
    ff = None
    if ev.fec_fin:
        ff = ev.fec_fin if ev.fec_fin.tzinfo else ev.fec_fin.replace(tzinfo=timezone.utc)
    if now < fi:
        return "futuro"
    if ev.fec_fin and fi <= now <= ff:
        return "activo"
    return "concluido"

def listar_eventos_validos() -> list[tuple[str,str]]:
    with Session(engine) as s:
        eventos = s.exec(select(Evento)).all()
        return [(str(ev.id_evento),ev.titulo) for ev in eventos if estado_evento(ev) in ("abierto","futuro")]

def validar_asociar_reto(id_reto:int) -> tuple[bool,str]:
    with Session(engine) as s:
        evs = s.exec(select(Contiene, Evento)
                    .join(Evento, Contiene.id_evento == Evento.id_evento)
                    .where(Contiene.id_reto == id_reto)).all()
        for c, ev in evs:
            if ev.fec_inicio and estado_evento(ev) in("futuro","activo"):
                return False, f"El reto se encuantra en un evento cerrado {ev.titulo} (no terminado."
        return True, ""

def asociar_reto(id_reto:int, id_evento:int, puntaje_override:int | None=None):
    ok, msg = validar_asociar_reto(id_reto)
    if not ok:
        raise ValueError(msg)
    with Session(engine) as s:
        exs = s.exec(select(Contiene).where(Contiene.id_reto == id_reto, Contiene.id_evento == id_evento)).first()
        if exs: return False
        s.add(Contiene(id_reto=id_reto,id_evento=id_evento,puntaje_override=puntaje_override))
        s.commit()
        return True
           
def validar_quitar_reto(id_evento:int) -> tuple[bool,str]:
    with Session(engine) as s:
        ev =  s.get(Evento, id_evento)
        if not ev:
            return False, "El evento no existe."
        est = estado_evento(ev)
        if est == "abierto":
            return False, "En el evento abieto los retos son permanentes."
        if est == "futuro":
            return True, ""
        return False, f"No se puede quitar retos de un evento {est.replace('_', ' ')}." 
    
def quitar_reto(id_reto:int, id_evento:int):
    ok , msg = validar_quitar_reto(id_evento)
    if not ok:
        raise ValueError(msg)
    with Session(engine) as s:
        asoc = s.exec(select(Contiene).where(Contiene.id_reto == id_reto, Contiene.id_evento == id_evento)).first()
        if not asoc:
            return False
        s.delete(asoc)
        s.commit()
        return True
                   
def aislado(id_reto:int) -> bool:
    with Session(engine) as s:
        return s.exec(select(Contiene).where(Contiene.id_reto == id_reto)).first() is None
    
def retos_aislados():
    with Session(engine) as s:
        vinculado = select(Contiene).distinct()
        stmt = select(Reto).where(Reto.activo == True, Reto.id_reto.not_in(vinculado))
        return[{
            "id_reto":r.id_reto,
            "titulo":r.titulo,
            "id_categoria":r.id_categoria,
            "id_modo_puntaje":r.id_modo_puntaje,
            "puntaje_inicial":r.puntaje_inicial,
        }for r in s.exec(stmt).all()]
    
def retos_evento(id_evento:int)-> dict:
    with Session(engine) as s:
        cat_map = {c.id_categoria: c.etiqueta for c in s.exec(select(Categoria)).all()}
        stmt = (select(Reto, Contiene.puntaje_override)
                      .join(Contiene, Reto.id_reto == Contiene.id_reto)
                      .where(Contiene.id_evento == id_evento))
        return[{"id":r.id_reto, "titulo":r.titulo, "puntaje_inicial":r.puntaje_inicial, "override":ov, "categoria":cat_map.get(r.id_categoria,"")}
                for r, ov in s.exec(stmt).all()]
    
def retos_asociables(id_evento_dest:int, id_categoria:int | None=None, id_modo_puntaje:int | None=None, id_dificultad:int | None=None, aislados: bool = False):
    with Session(engine) as s:
        cat_map = {c.id_categoria: c.etiqueta for c in s.exec(select(Categoria)).all()}
        vinculados = set()
        if id_evento_dest:
            vinculados = set(s.exec(select(Contiene.id_reto).where(Contiene.id_evento == id_evento_dest)).all())
        resevados = set()
        for c, ev in s.exec(select(Contiene, Evento).join(Evento, Contiene.id_evento == Evento.id_evento)).all():
            if ev.fec_inicio and estado_evento(ev) in ("futuro","activo"):
                resevados.add(c.id_reto)
        candidatos={}
        if aislados:
            for r in s.exec(select(Reto).where(Reto.activo == True)).all():
                if aislado(r.id_reto):
                    candidatos[r.id_reto] = r
        else:
            for c, ev, r in s.exec(select(Contiene, Evento, Reto)
                                   .join(Evento, Contiene.id_evento == Evento.id_evento)
                                   .join(Reto, Contiene.id_reto == Reto.id_reto)).all():
                if estado_evento(ev) in ("abierto","concluido") and r.activo:
                    candidatos[r.id_reto] = r
        resultado=[]
        for id_r, r in candidatos.items():
            if id_r in vinculados or id_r in resevados:
                continue
            if id_categoria and r.id_categoria != id_categoria:
                continue
            if id_modo_puntaje and r.id_modo_puntaje != id_modo_puntaje:
                continue
            if id_dificultad and r.id_dificultad != id_dificultad:
                continue
            resultado.append({
                "id_reto":r.id_reto,
                "titulo":r.titulo,
                "puntaje_inicial":r.puntaje_inicial,
                "categoria":cat_map.get(r.id_categoria,""),
            })
        return resultado
