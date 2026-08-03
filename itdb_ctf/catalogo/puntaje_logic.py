from sqlmodel import Session,select
from itdb_ctf.models import Evento,Reto,Contiene,ModoPuntaje,Resuelve

# --- FORMULA DE RECALCULACION DE PUNTAJE DINAMICO USADO POR CTFD

def formula_dinamic(inicial:int, minimo:int, resoluciones: int, decay:int=20)->int:
    p=(minimo - inicial) / (decay ** 2) * (resoluciones ** 2) + inicial
    return max(int(p), minimo)

def calcular_puntaje(session:Session,id_reto:int,id_evento:int)->int:
    # --- Estatico no cambia de valor 
    # --- Dinamico se cambia el valor segun la cantidad de resoluciones
    evento = session.get(Evento, id_evento)
    contiene = session.exec(select(Contiene).where(Contiene.id_reto==id_reto, Contiene.id_evento==id_evento)).first()
    if not evento or not contiene:
        return 0
    pts = contiene.puntaje_inicial
    mod_ev = session.get(ModoPuntaje, evento.id_modo_puntaje)
    if not mod_ev or mod_ev.etiqueta == "estatico":
        return pts 
    # --- modo estatico
    mod_ct = session.get(ModoPuntaje, contiene.id_modo_puntaje)
    if not mod_ct or mod_ct.etiqueta == "estatico":
        return pts
    # ---modo dinamico recalaculacion de puntaje dinamico
    resoluciones = len(session.exec(select(Resuelve).where(
        Resuelve.id_reto==id_reto,
        Resuelve.id_evento==id_evento,
        Resuelve.flag_correcta==True)).all())
    return formula_dinamic(pts, contiene.puntaje_minimo or 0, resoluciones)





