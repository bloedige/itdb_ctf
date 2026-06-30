from sqlmodel import Session,select
from itdb_ctf.db import engine
from itdb_ctf.models import Reto, Contiene, Pista
from itdb_ctf.utils.security import flag_hasher

ROLES_STAFF ={"superadmin","admin","autor"}

def crear_reto(id_usuario,id_categoria,id_modo_puntaje,id_dificultad,
               titulo,descripcion,flag, puntaje_inicial,id_evento,
               puntaje_minimo=None,archivo_original=None, archivo_ruta=None, pistas=None):
    with Session(engine) as s:
        reto=Reto(
            id_usuario=id_usuario,
            id_categoria=id_categoria,
            id_dificultad=id_dificultad,
            id_modo_puntaje=id_modo_puntaje,
            titulo=titulo,
            descripcion=descripcion,
            flag=flag_hasher.hashear(flag),
            puntaje_inicial=puntaje_inicial,
            puntaje_minimo=puntaje_minimo,
            archivo_original=archivo_original,
            archivo_ruta=archivo_ruta,
        )
        s.add(reto)
        s.flush()
        asoc=Contiene(id_reto=reto.id_reto,id_evento=id_evento)
        s.add(asoc)
        for p in (pistas or []):
            if p.get("descripcion"):
                s.add(Pista(
                    id_reto = reto.id_reto,
                    costo = int(p.get("costo") or 0),
                    descripcion = p['descripcion'],
                ))

        s.commit()
        s.refresh(reto)
        return reto

def asociar_reto(id_reto:int, id_evento:int, puntaje_override:int|None=None):
    with Session(engine) as s:
        existe=s.exec(select(Contiene).where(Contiene.id_reto==id_reto,Contiene.id_evento==id_evento)).first()
        if existe:
            return False
        s.add(Contiene(id_reto=id_reto,id_evento=id_evento,puntaje_override=puntaje_override))
        s.commit()
        return True

def editar_reto(id_reto, values:dict):
    with Session(engine) as s:
        reto = s.get(Reto, id_reto)
        if not reto:
            return None
        for campo,valor in values.items():
            if campo == "flag":
                valor = flag_hasher.hashear(valor)
            setattr(reto, campo, valor)

        s.add(reto)
        s.commit()
        s.refresh(reto)
        return reto
    
def activar_desactivar_reto(id_reto) -> bool:
    with Session(engine) as s:
        reto = s.get(Reto,id_reto)
        if not reto: return False
        reto.activo = not reto.activo
        s.add(reto)
        s.commit()
        return True
    
def puede_editar(reto:Reto, id_usuario:int, codigo_rol:str ) -> bool:
    if codigo_rol in ("superadmin","admin"):
        return True
    if codigo_rol == "autor":
        return reto.id_usuario == id_usuario
    return False

def crear_pista(id_reto, costo, desc):
    with Session(engine) as s:
        p = Pista(id_reto=id_reto,costo=int(costo or 0), descripcion=desc)
        s.add(p)
        s.commit()
        s.refresh(p)
        return p.id_pista 
    
def editar_pista(id_pista, costo, desc):
    with Session(engine) as s:
        p = s.get(Pista, id_pista)
        if not p:
            return False
        p.costo = int(costo or 0),
        p.descripcion = desc
        s.add(p)
        s.commit()
        return True
    
def activar_desactivar_pista(id_pista):
    with Session(engine) as s:
        p = s.get(Pista, id_pista)
        if not p:
            return False
        p.activo = not p.activo
        s.add(p)
        s.commit()       
        return True

def listar_pista(id_reto):
    with Session(engine) as s:
        return[
            {
                "id_pista":p.id_pista,
                "costo":p.costo,
                "descripcion":p.descripcion,
                "activo":p.activo,
            }
            for p in s.exec(select(Pista).where(Pista.id_reto==id_reto)).all()
        ]