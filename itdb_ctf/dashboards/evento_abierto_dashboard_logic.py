"""Consultas de métricas para el dashboard del evento abierto.

Las consultas genéricas (KPIs, desgloses, ranking de retos) viven en
`dashboard_metricas_logic` parametrizadas por `id_evento`; aquí solo se resuelve
el evento abierto con `id_evento_abierto()` y se añaden las métricas propias del
abierto (`nuevos_mes`, actividad diaria, inscripciones por mes).
"""

from datetime import datetime, timezone, timedelta

from sqlmodel import Session, select
from sqlalchemy import func

from itdb_ctf.db import engine
from itdb_ctf.models import Participa, Resuelve
from itdb_ctf.evento.evento_logic import id_evento_abierto
from itdb_ctf.dashboards import dashboard_metricas_logic as m


def _inicio_mes(dt: datetime) -> datetime:
    return datetime(dt.year, dt.month, 1, tzinfo=timezone.utc)


def resumen_abierto() -> dict:
    """KPIs del evento abierto (los genéricos + `nuevos_mes`)."""
    id_ev = id_evento_abierto()
    datos = m.resumen_evento(id_ev)
    if not id_ev:
        return {**datos, "nuevos_mes": 0}

    inicio_mes = _inicio_mes(datetime.now(timezone.utc))
    with Session(engine) as s:
        nuevos_mes = s.exec(
            select(func.count(Participa.id_participa)).where(
                Participa.id_evento == id_ev,
                Participa.fec_ingreso >= inicio_mes,
            )
        ).one()
    return {**datos, "nuevos_mes": nuevos_mes}


def desglose_categoria() -> list[dict]:
    return m.desglose_categoria(id_evento_abierto())


def desglose_dificultad() -> list[dict]:
    return m.desglose_dificultad(id_evento_abierto())


def ranking_retos_resoluciones() -> list[dict]:
    return m.ranking_retos_resoluciones(id_evento_abierto())


def actividad_diaria(dias: int = 30) -> list[dict]:
    """Envíos y resoluciones por día en los últimos `dias` (serie continua)."""
    id_ev = id_evento_abierto()
    if not id_ev:
        return []
    ahora = datetime.now(timezone.utc)
    desde = (ahora - timedelta(days=dias - 1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    with Session(engine) as s:
        filas = s.exec(
            select(Resuelve.fec_envio, Resuelve.flag_correcta).where(
                Resuelve.id_evento == id_ev,
                Resuelve.fec_envio >= desde,
            )
        ).all()

    envios: dict = {}
    correctos: dict = {}
    for fec, ok in filas:
        d = fec.date()
        envios[d] = envios.get(d, 0) + 1
        if ok:
            correctos[d] = correctos.get(d, 0) + 1

    salida = []
    for i in range(dias):
        d = (desde + timedelta(days=i)).date()
        salida.append(
            {
                "fecha": d.strftime("%d/%m"),
                "envios": envios.get(d, 0),
                "resoluciones": correctos.get(d, 0),
            }
        )
    return salida


def inscripciones_por_mes(meses: int = 12) -> list[dict]:
    """Nuevas inscripciones al evento abierto mes a mes (serie continua)."""
    id_ev = id_evento_abierto()
    if not id_ev:
        return []
    ahora = datetime.now(timezone.utc)
    claves: list[tuple[int, int]] = []
    y, mm = ahora.year, ahora.month
    for _ in range(meses):
        claves.append((y, mm))
        mm -= 1
        if mm == 0:
            mm, y = 12, y - 1
    claves.reverse()

    with Session(engine) as s:
        fechas = s.exec(
            select(Participa.fec_ingreso).where(
                Participa.id_evento == id_ev,
                Participa.fec_ingreso != None,  # noqa: E711
            )
        ).all()

    conteo: dict = {}
    for fec in fechas:
        k = (fec.year, fec.month)
        conteo[k] = conteo.get(k, 0) + 1

    return [
        {"mes": f"{mes:02d}/{str(anio)[2:]}", "cantidad": conteo.get((anio, mes), 0)}
        for anio, mes in claves
    ]
