from datetime import datetime

from sqlmodel import Session, select
from sqlalchemy import func
from itdb_ctf.models import Evento, Contiene, ModoPuntaje, Resuelve, Compra

# --- FORMULA DE RECALCULACION DE PUNTAJE DINAMICO USADO POR CTFD

def formula_dinamic(inicial:int, minimo:int, resoluciones: int, decay:int=20)->int:
    p=(minimo - inicial) / (decay ** 2) * (resoluciones ** 2) + inicial
    return max(int(p), minimo)

def calcular_puntaje(session:Session, id_reto:int, id_evento:int, corte: datetime | None = None) -> int:
    # --- Estatico no cambia de valor
    # --- Dinamico se recalcula segun la cantidad de resoluciones
    # `corte` (freeze): cuenta solo las resoluciones hasta ese instante, para
    #   reproducir el decay tal como estaba al congelar el scoreboard.
    evento = session.get(Evento, id_evento)
    contiene = session.exec(select(Contiene).where(Contiene.id_reto==id_reto, Contiene.id_evento==id_evento)).first()
    if not evento or not contiene:
        return 0
    pts = contiene.puntaje_inicial
    mod_ev = session.get(ModoPuntaje, evento.id_modo_puntaje)
    if not mod_ev or mod_ev.etiqueta == "estatico":
        return pts
    mod_ct = session.get(ModoPuntaje, contiene.id_modo_puntaje)
    if not mod_ct or mod_ct.etiqueta == "estatico":
        return pts
    # ---modo dinamico: recalculo
    q = select(func.count(Resuelve.id_resuelve)).where(
        Resuelve.id_reto == id_reto,
        Resuelve.id_evento == id_evento,
        Resuelve.flag_correcta == True,  # noqa: E712
    )
    if corte is not None:
        q = q.where(Resuelve.fec_envio <= corte)
    resoluciones = session.exec(q).one() or 0
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

def puntaje_total_usuario(session:Session, id_usuario:int, id_evento:int,
                          corte: datetime | None = None) -> int:
    # `corte` (freeze): solo cuenta aciertos/compras con fecha <= corte y, en
    #   eventos dinámicos, recalcula el puntaje de cada reto a ese instante.
    q_gastados = select(func.coalesce(func.sum(Compra.puntos_usados), 0)).where(
        Compra.id_usuario == id_usuario,
        Compra.id_evento == id_evento,
    )
    if corte is not None:
        q_gastados = q_gastados.where(Compra.fec_compra <= corte)
    gastados = session.exec(q_gastados).one()

    ev = session.get(Evento, id_evento)
    mod_ev = session.get(ModoPuntaje, ev.id_modo_puntaje) if ev else None
    estatico = (mod_ev is None) or (mod_ev.etiqueta == "estatico")

    if estatico:
        q = (select(func.coalesce(func.sum(Contiene.puntaje_inicial), 0))
             .join(Resuelve, (Contiene.id_reto == Resuelve.id_reto) & (Contiene.id_evento == Resuelve.id_evento))
             .where(
                 Resuelve.id_usuario == id_usuario,
                 Resuelve.id_evento == id_evento,
                 Resuelve.flag_correcta == True))  # noqa: E712
        if corte is not None:
            q = q.where(Resuelve.fec_envio <= corte)
        total = session.exec(q).one()
    elif corte is None:
        # dinámico en vivo: usa el puntaje_actual ya recalculado
        total = session.exec(
            select(func.coalesce(func.sum(Contiene.puntaje_actual), 0))
            .join(Resuelve, (Contiene.id_reto == Resuelve.id_reto) & (Contiene.id_evento == Resuelve.id_evento))
            .where(
                Resuelve.id_usuario == id_usuario,
                Resuelve.id_evento == id_evento,
                Resuelve.flag_correcta == True)).one()  # noqa: E712
    else:
        # dinámico congelado: recalcula el valor de cada reto resuelto a `corte`
        retos = session.exec(
            select(Resuelve.id_reto).where(
                Resuelve.id_usuario == id_usuario,
                Resuelve.id_evento == id_evento,
                Resuelve.flag_correcta == True,  # noqa: E712
                Resuelve.fec_envio <= corte,
            )
        ).all()
        total = sum(calcular_puntaje(session, id_reto, id_evento, corte) for id_reto in retos)

    score = total - gastados
    return score if score > 0 else 0
