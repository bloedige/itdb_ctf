from sqlmodel import Session,select
from sqlalchemy import func
from itdb_ctf.models import Evento, Contiene, ModoPuntaje, Resuelve, Compra

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
    if resoluciones > 0:
        resoluciones -= 1
    return formula_dinamic(pts, contiene.puntaje_minimo or 0, resoluciones)

def refrescar_puntaje(session:Session, id_reto:int, id_evento:int) -> int:
    contiene = session.exec(select(Contiene).where(
        Contiene.id_reto == id_reto,
        Contiene.id_evento == id_evento)).first()
    if not contiene:
        return 0
    valor = calcular_puntaje(session, id_reto, id_evento)
    if contiene.puntaje_actual != valor:
        contiene.puntaje_actual = valor
        session.add(contiene)
    return valor

def puntaje_total_usuario(session:Session, id_usuario:int, id_evento:int) -> int:
    gastados = session.exec(select(func.coalesce(func.sum(Compra.puntos_usados),0)).where(
        Compra.id_usuario == id_usuario,
        Compra.id_evento == id_evento)).one()
    ev = session.get(Evento, id_evento)
    mod_ev = session.get(ModoPuntaje, ev.id_modo_puntaje)
    if mod_ev == "estatico":
        total = session.exec(select(func.coalesce(func.sum(Contiene.puntaje_inicial),0))
            .join(Resuelve, (Contiene.id_reto == Resuelve.id_reto) & (Contiene.id_evento == Resuelve.id_evento))
            .where(
                Resuelve.id_usuario == id_usuario,
                Resuelve.id_evento == id_evento,
                Resuelve.flag_correcta == True)).one()
    else:
        total = session.exec(select(func.coalesce(func.sum(Contiene.puntaje_actual),0))
            .join(Resuelve, (Contiene.id_reto == Resuelve.id_reto) & (Contiene.id_evento == Resuelve.id_evento))
            .where(
                Resuelve.id_usuario == id_usuario,
                Resuelve.id_evento == id_evento,
                Resuelve.flag_correcta == True)).one()
    score = total - gastados
    if score < 0:
        return 0
    return score