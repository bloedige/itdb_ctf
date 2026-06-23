from sqlmodel import Session,select
from itdb_ctf.db import engine 
from itdb_ctf.models import Evento,Reto,Contiene,Categoria,ModoPuntaje,Resuelve

# --- FORMULA DE RECALCULACION DE PUNTAJE DINAMICO USADO POR CTFD

def formula_dinamic(inicial:int, minimo:int, resoluciones: int, decay:int=20)->int:

    p=(minimo - inicial) / (decay ** 2) * (resoluciones ** 2) + inicial

    return max(int(p), minimo)

def calcular_puntaje(session:Session,id_reto:int,id_evento:int)->int:
    
    # --- Estatico no cambia de valor 
    # --- Dinamico se cambia el valor segun la cantidad de resoluciones

    reto = session.get(Reto, id_reto)
    evento = session.get(Evento, id_evento)

    if not reto or not evento:
        return 0
    
    # --- Verificamo que contenga puntaje override si no devolvemos puntaje por defecto
    rel = session.exec(select(Contiene).where(Contiene.id_reto==id_reto, Contiene.id_evento==id_evento)).first()
    base = (rel.puntaje_override if rel and rel.puntaje_override else reto.puntaje_inicial)
    
    # --- modo estatico
    modo = session.get(ModoPuntaje, evento.id_modo_puntaje)
    if not modo or modo.etiqueta == "estatico":
        return base
    
    # ---modo dinamico recalaculacion de puntaje dinamico

    resoluciones = len(session.exec(select(Resuelve).where(Resuelve.id_reto==id_reto,Resuelve.id_evento==id_evento,Resuelve.flag_correcta==True)).all())

    return formula_dinamic(base, reto.puntaje_minimo or 0, resoluciones)





