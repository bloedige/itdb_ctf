from sqlmodel import Session, select
from itdb_ctf.db import engine
from itdb_ctf.models import Evento, Contiene, Reto, Categoria, ModoPuntaje, Dificultad
from datetime import datetime, timezone

def cargar_catalogos():
    with Session(engine) as s:
        dest, gest = [], []
        for ev in s.exec(select(Evento)).all():
            est = estado_evento(ev)
            if est in ("abierto","futuro"):
                dest.append((str(ev.id_evento),ev.titulo))
            if est == "futuro":
                gest.append((str(ev.id_evento),ev.titulo))
        return{
            "categorias":[("","Todos")] + [(str(c.id_categoria),c.etiqueta)for c in s.exec(select(Categoria)).all()],
            "dificultades":[("","Todos")] + [(str(d.id_dificultad),d.etiqueta)for d in s.exec(select(Dificultad)).all()],
            "modos":[("","Todos")] + [(str(m.id_modo_puntaje),m.etiqueta)for m in s.exec(select(ModoPuntaje)).all()],
            "eventos_dest":dest,
            "eventos_gest":gest
        }

def dinamico_estatico(value:str) -> int:
    with Session(engine) as s:
        modo = s.exec(select(ModoPuntaje).where(ModoPuntaje.etiqueta == value)).first()
        return modo.id_modo_puntaje if modo else None

def es_dinamico(id_modo:int) -> bool:
   with Session(engine) as s:
       modo = s.get(ModoPuntaje, id_modo)
       return modo.etiqueta == "dinamico"
    
def modo_puntaje(id_modo_puntaje:int) -> str:
    with Session(engine) as s:
        modo = s.get(ModoPuntaje,id_modo_puntaje)
        return modo.etiqueta if modo else None
    
def modo_evento(id_evento:int) -> str:
    with Session(engine) as s:
        ev = s.get(Evento, id_evento)
        modo = s.get(ModoPuntaje, ev.id_modo_puntaje)
        return modo.etiqueta if modo else None

def estado_evento(ev) -> str:
    if not ev.fec_fin:
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
        eventos = s.exec(select(Evento).where(Evento.activo == True)).all()
        return [(str(ev.id_evento),ev.titulo) for ev in eventos if estado_evento(ev) in ("abierto","futuro")]


def validar_asociar_reto(id_reto:int, id_evento:int, id_modo_puntaje:int, inicial:int, minimo:int | None=None) -> tuple[bool,str]:
    with Session(engine) as s:
        evs = s.exec(select(Contiene, Evento)
                    .join(Evento, Contiene.id_evento == Evento.id_evento)
                    .where(Contiene.id_reto == id_reto)).all()
        futuro_activo = False
        reutilizable = False
        for c, ev in evs:
            estado = estado_evento(ev)
            if estado in ("futuro", "activo"):
                futuro_activo = True
            if estado in ("abierto", "concluido"):
                reutilizable = True
            if futuro_activo and not reutilizable:
                return False, f"El reto se encuantra en un evento cerrado {ev.titulo} (no terminado)."

        ev_dest = s.get(Evento, id_evento)
        if not ev_dest:
            return False, "Evento inexistente."
        
        modo_ev = s.get(ModoPuntaje, ev_dest.id_modo_puntaje)
        modo_ct = s.get(ModoPuntaje, id_modo_puntaje)
        dinamico = bool(modo_ct and modo_ct.etiqueta == "dinamico")
        if modo_ev and modo_ev.etiqueta == "estatico" and dinamico:
            return False, "Evento estatico solo admite puntaje unico"
        
        if inicial is None or inicial <= 0:
                return False, "El puntaje inicial obligatorio mayor 0."
        if dinamico:
            if minimo is None or minimo <= 0:
                return False, "Puntaje minimo obligatorio mayor a 0 en modo dinamico."
            if minimo >= inicial:
                return False, "Puntaje minimo debe ser menor a el inicial."
            
        return True, ""

def asociar_reto(id_reto:int, id_evento:int, id_modo_puntaje:int, puntaje_inicial:int, puntaje_minimo:int | None=None):
    ok, msg = validar_asociar_reto(id_reto, id_evento, id_modo_puntaje, puntaje_inicial, puntaje_minimo)
    if not ok:
        raise ValueError(msg)
    with Session(engine) as s:
        if s.exec(select(Contiene).where(Contiene.id_reto == id_reto, Contiene.id_evento == id_evento)).first(): 
            return False
        s.add(Contiene(
            id_reto=id_reto,
            id_evento=id_evento,
            id_modo_puntaje=id_modo_puntaje,
            puntaje_inicial=puntaje_inicial,
            puntaje_minimo=puntaje_minimo,
            puntaje_actual=puntaje_inicial,
        ))
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
    
def retos_aislados(busqueda:str | None=None, id_categoria:int | None=None, id_dificultad:int | None=None, id_modo_puntaje:int | None=None): 
    with Session(engine) as s:
        vinculado = select(Contiene).distinct()
        stmt = (select(Reto, Categoria.etiqueta, Dificultad.etiqueta)
            .join(Categoria, Reto.id_categoria == Categoria.id_categoria)
            .join(Dificultad, Reto.id_dificultad == Dificultad.id_dificultad)   
            .where(Reto.activo == True, Reto.id_reto.not_in(vinculado)))
        if busqueda:
            stmt = stmt.where(Reto.titulo.ilike(f"%{busqueda}%"))
        if id_categoria:
            stmt = stmt.where(Reto.id_categoria == id_categoria)
        if id_dificultad:
            stmt = stmt.where(Reto.id_dificultad == id_dificultad)
        if id_modo_puntaje:
            stmt = stmt.where(Reto.id_modo_puntaje == id_modo_puntaje)
        return[{
            "id_reto":r.id_reto,
            "titulo":r.titulo,
            "categoria":cat,
            "dificultad":dif,
            "id_modo_puntaje":r.id_modo_puntaje,
            "puntaje_inicial":r.puntaje_inicial,
            "puntaje_minimo":r.puntaje_minimo,
        }for r, cat, dif in s.exec(stmt).all()]
    
def retos_evento(id_evento:int, busqueda:str | None=None, id_categoria:int | None=None, id_dificultad:int | None=None, id_modo_puntaje:int | None=None)-> dict: 
    with Session(engine) as s:

        stmt = (select(Reto, Contiene, Categoria.etiqueta, Dificultad.etiqueta, ModoPuntaje.etiqueta)
                      .join(Contiene, Reto.id_reto == Contiene.id_reto)
                      .join(Categoria, Reto.id_categoria == Categoria.id_categoria)
                      .join(Dificultad, Reto.id_dificultad == Dificultad.id_dificultad)
                      .join(ModoPuntaje, Reto.id_modo_puntaje == ModoPuntaje.id_modo_puntaje)
                      .order_by(Categoria.id_categoria)
                      .where(Contiene.id_evento == id_evento))
        if busqueda:
            stmt = stmt.where(Reto.titulo.ilike(f"%{busqueda}%"))
        if id_categoria:
            stmt = stmt.where(Reto.id_categoria == id_categoria)
        if id_dificultad:
            stmt = stmt.where(Reto.id_dificultad == id_dificultad)
        if id_modo_puntaje:
            stmt = stmt.where(Reto.id_modo_puntaje == id_modo_puntaje)
        return[
            {
            "id_contine":c.id_contiene,
            "id_reto":r.id_reto, 
            "titulo":r.titulo, 
            "categoria":cat,
            "dificultad":dif,
            "modo_puntaje":mod,
            "puntaje_inicial":c.puntaje_inicial,
            "puntaje_minimo":c.puntaje_minimo, 
            }
            for r, c, cat, dif, mod in s.exec(stmt).all()
        ]
    
def retos_asociables(id_evento_dest:int, busqueda:str | None=None, id_categoria:int | None=None, id_dificultad:int | None=None, id_modo_puntaje:int | None=None, aislados: bool = False):
    with Session(engine) as s:
        vinculados = set()
        if id_evento_dest:
            vinculados = set(s.exec(select(Contiene.id_reto).where(Contiene.id_evento == id_evento_dest)).all())

        reutilizable = set()
        for c, ev in s.exec(select(Contiene, Evento).join(Evento, Contiene.id_evento == Evento.id_evento)).all():
            estado = estado_evento(ev)
            if estado in ("abierto","concluido"):
                reutilizable.add(c.id_reto)

        stmt = (select(Reto, Categoria.etiqueta, Dificultad.etiqueta, ModoPuntaje.etiqueta)
                .join(Categoria, Reto.id_categoria == Categoria.id_categoria)
                .join(Dificultad, Reto.id_dificultad == Dificultad.id_dificultad)
                .join(ModoPuntaje, Reto.id_modo_puntaje == ModoPuntaje.id_modo_puntaje)
                .order_by(Reto.id_categoria)
                .where(Reto.activo == True))
        if busqueda:
            stmt = stmt.where(Reto.titulo.ilike(f"%{busqueda}%"))
        if id_categoria:
            stmt = stmt.where(Reto.id_categoria == id_categoria)
        if id_dificultad:
            stmt = stmt.where(Reto.id_dificultad == id_dificultad)
        if id_modo_puntaje:
            stmt = stmt.where(Reto.id_modo_puntaje == id_modo_puntaje)

        candidatos={}
        if aislados:
            for r, cat, dif, mod in s.exec(stmt).all():
                if aislado(r.id_reto):
                    candidatos[r.id_reto] = (r, cat, dif, mod)
        else:
            for r, cat, dif, mod in s.exec(stmt).all():
                if r.id_reto in reutilizable:
                    candidatos[r.id_reto] = (r, cat, dif, mod)
        resultado=[]
        for id_r, (r, cat, dif, mod) in candidatos.items():
            if id_r in vinculados:
                continue
            resultado.append({
                "id_reto":r.id_reto,
                "titulo":r.titulo,
                "categoria":cat,
                "dificultad":dif,
                "modo":mod,
                "id_modo_puntaje":r.id_modo_puntaje,
                "puntaje_inicial":r.puntaje_inicial,
                "puntaje_minimo":r.puntaje_minimo,
            })
        return resultado

def prev_retos(id_evento:int):
    with Session(engine) as s:
            stmt = (select(Reto, Contiene, Categoria.etiqueta, Dificultad.etiqueta, ModoPuntaje.etiqueta)
                          .join(Contiene, Reto.id_reto == Contiene.id_reto)
                          .join(Categoria, Reto.id_categoria == Categoria.id_categoria)
                          .join(Dificultad, Reto.id_dificultad == Dificultad.id_dificultad)
                          .join(ModoPuntaje, Reto.id_modo_puntaje == ModoPuntaje.id_modo_puntaje)
                          .order_by(Categoria.id_categoria)
                          .where(Contiene.id_evento == id_evento))
            return[
                {
                "titulo":r.titulo, 
                "categoria":cat,
                "dificultad":dif,
                "modo":mod,
                "puntaje_inicial":c.puntaje_inicial,
                "puntaje_minimo":c.puntaje_minimo, 
                }
                for r, c, cat, dif, mod in s.exec(stmt).all()
            ]
     
def obtener_contiene(id_contiene:int):
    with Session(engine) as s:
        c = s.get(Contiene,id_contiene)
        if not c:
            return None
        return{
            "id_contiene":c.id_contiene,
            "id_evento":c.id_evento,
            "id_modo_puntaje":c.id_modo_puntaje,
            "puntaje_inicial":c.puntaje_inicial,
            "puntaje_minimo":c.puntaje_minimo,
        }

def editar_contiene(id_contiene:int, id_modo_puntaje:int, inicial:int, minimo:int | None=None):
    with Session(engine) as s:
        c = s.get(Contiene, id_contiene)
        if not c:
            raise ValueError("Registro inexistente.")
        ev = s.get(Evento, c.id_evento)
        if not ev:
            raise ValueError("Evento inexistente.")
        if estado_evento(ev) != "futuro":
            raise ValueError("Solo editable en eventos futuros.")
        modo_ev = s.get(ModoPuntaje, ev.id_modo_puntaje)
        modo_ct = s.get(ModoPuntaje, id_modo_puntaje)
        if not modo_ct:
            raise ValueError("Modo de puntaje invalido")
        dinamico = bool(modo_ct and modo_ct.etiqueta == "dinamico")
        if modo_ev and modo_ev.etiqueta == "estatico" and dinamico:
            raise ValueError("Evento estatico solo admite puntaje único.")
        if inicial is None or inicial <= 0:
            raise ValueError("Puntaje inicial obligatorio mayor a 0.")
        if dinamico:
            if minimo is None or minimo <= 0:
                raise ValueError("Puntaje minimo obligatorio mayor a 0.")
            if minimo >= inicial:
                raise ValueError("Puntaje minimo de ser menor a el inicial.")

        c.id_modo_puntaje = id_modo_puntaje
        c.puntaje_inicial = inicial
        c.puntaje_minimo = minimo if dinamico else None
        s.add(c)
        s.commit()
        return True