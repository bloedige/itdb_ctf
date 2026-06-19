from sqlmodel import Session,select
from itdb_ctf.db import engine
from itdb_ctf.models import Reto, Contiene
from itdb_ctf.utils.security import flag_hasher

ROLES_STAFF ={"superadmin","admin","autor"}

def crear_reto(id_usuario,id_categoria,id_modo_puntaje,id_dificultad,
               titulo,descripcion,flag, puntaje_inicial,id_evento,
               puntaje_minimo=None,archivo_original=None, archivo_ruta=None):
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

def desactivar_reto(id_reto) -> bool:
    with Session(engine) as s:
        reto = s.get(Reto, id_reto)
        if not reto:
            return False
        reto.activo = False
        s.add(reto)
        s.commit()
        return True
    
def puede_editar(reto:Reto, id_usuario:int, codigo_rol:str ) -> bool:
    if codigo_rol in ("superadmin","admin"):
        return True
    if codigo_rol == "autor":
        return reto.id_usuario == id_usuario
    return False