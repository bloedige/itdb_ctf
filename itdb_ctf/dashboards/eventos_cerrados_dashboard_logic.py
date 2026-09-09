"""Consultas propias del dashboard de eventos cerrados.

Los KPIs, desgloses y ranking de retos se sacan de `dashboard_metricas_logic`
(parametrizados por `id_evento`). Aquí van: el listado para el `select`, la
info/estado del evento, la actividad dentro de la ventana y el feed de
resoluciones.
"""

from datetime import datetime, timezone, timedelta

from sqlmodel import Session, select
from sqlalchemy import func

from itdb_ctf.db import engine
from itdb_ctf.models import Evento, Modalidad, Resuelve, Reto, Usuario
from itdb_ctf.asociar.asociar_logic import estado_evento

_ORDEN_ESTADO = {"activo": 0, "futuro": 1, "concluido": 2, "abierto": 3}


def _aware(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _fmt_delta(delta: timedelta) -> str:
    total = int(delta.total_seconds())
    if total < 0:
        total = 0
    dias, resto = divmod(total, 86400)
    horas, resto = divmod(resto, 3600)
    minutos = resto // 60
    partes = []
    if dias:
        partes.append(f"{dias}d")
    if horas or dias:
        partes.append(f"{horas}h")
    partes.append(f"{minutos}m")
    return " ".join(partes)


def listar_eventos_cerrados() -> list[tuple[str, str]]:
    """Opciones para el `select`: (id, "<título> (<estado>)"). Activos primero."""
    with Session(engine) as s:
        modalidad = s.exec(
            select(Modalidad).where(Modalidad.etiqueta == "cerrado")
        ).first()
        if not modalidad:
            return []
        eventos = s.exec(
            select(Evento).where(Evento.id_modalidad == modalidad.id_modalidad)
        ).all()

    eventos.sort(
        key=lambda ev: (
            _ORDEN_ESTADO.get(estado_evento(ev), 9),
            -(_aware(ev.fec_inicio).timestamp() if ev.fec_inicio else 0),
        )
    )
    return [
        (str(ev.id_evento), f"{ev.titulo} ({estado_evento(ev)})")
        for ev in eventos
    ]


def info_evento(id_evento: int | None) -> dict:
    vacio = {
        "hay_evento": False,
        "titulo": "",
        "estado": "",
        "fec_inicio": "",
        "fec_fin": "",
        "freeze": False,
        "pct_transcurrido": 0,
        "tiempo_texto": "",
    }
    if not id_evento:
        return vacio
    with Session(engine) as s:
        ev = s.get(Evento, id_evento)
        if not ev:
            return vacio
        titulo = ev.titulo
        freeze = bool(ev.freeze)
        fi = _aware(ev.fec_inicio)
        ff = _aware(ev.fec_fin)
        estado = estado_evento(ev)

    ahora = datetime.now(timezone.utc)
    pct = 0
    if estado == "activo" and fi and ff:
        total = (ff - fi).total_seconds()
        pct = round((ahora - fi).total_seconds() / total * 100) if total > 0 else 0
        tiempo_texto = f"finaliza en {_fmt_delta(ff - ahora)}"
    elif estado == "futuro" and fi:
        tiempo_texto = f"inicia en {_fmt_delta(fi - ahora)}"
    elif estado == "concluido" and ff:
        pct = 100
        tiempo_texto = f"finalizó el {ff.strftime('%d/%m/%Y %H:%M')}"
    else:
        tiempo_texto = ""

    return {
        "hay_evento": True,
        "titulo": titulo,
        "estado": estado,
        "fec_inicio": fi.strftime("%d/%m/%Y %H:%M") if fi else "—",
        "fec_fin": ff.strftime("%d/%m/%Y %H:%M") if ff else "—",
        "freeze": freeze,
        "pct_transcurrido": max(0, min(100, pct)),
        "tiempo_texto": tiempo_texto,
    }


def actividad_evento(id_evento: int | None) -> list[dict]:
    """Envíos y resoluciones dentro de la ventana del evento (serie continua).

    Buckets por hora; si la ventana supera 10 días, por día.
    """
    if not id_evento:
        return []
    with Session(engine) as s:
        ev = s.get(Evento, id_evento)
        if not ev:
            return []
        fi = _aware(ev.fec_inicio)
        ff = _aware(ev.fec_fin)

    if not fi:
        return []
    ahora = datetime.now(timezone.utc)
    if ahora < fi:
        return []
    fin = min(ff, ahora) if ff else ahora

    por_hora = (fin - fi) <= timedelta(days=10)
    paso = timedelta(hours=1) if por_hora else timedelta(days=1)
    inicio = fi.replace(minute=0, second=0, microsecond=0)

    with Session(engine) as s:
        filas = s.exec(
            select(Resuelve.fec_envio, Resuelve.flag_correcta).where(
                Resuelve.id_evento == id_evento,
                Resuelve.fec_envio >= inicio,
                Resuelve.fec_envio <= fin,
            )
        ).all()

    def clave(dt: datetime) -> datetime:
        dt = _aware(dt)
        if por_hora:
            return dt.replace(minute=0, second=0, microsecond=0)
        return dt.replace(hour=0, minute=0, second=0, microsecond=0)

    envios: dict = {}
    correctos: dict = {}
    for fec, ok in filas:
        k = clave(fec)
        envios[k] = envios.get(k, 0) + 1
        if ok:
            correctos[k] = correctos.get(k, 0) + 1

    etiqueta = "%d/%m %H:00" if por_hora else "%d/%m"
    salida = []
    cursor = clave(inicio)
    tope = clave(fin)
    while cursor <= tope and len(salida) < 400:
        salida.append(
            {
                "t": cursor.strftime(etiqueta),
                "envios": envios.get(cursor, 0),
                "resoluciones": correctos.get(cursor, 0),
            }
        )
        cursor += paso
    return salida


def feed_resoluciones(id_evento: int | None, limite: int = 10) -> list[dict]:
    """Últimas flags correctas del evento: participante · reto · hora."""
    if not id_evento:
        return []
    with Session(engine) as s:
        filas = s.exec(
            select(Usuario.alias, Usuario.nombre, Reto.titulo, Resuelve.fec_envio)
            .join(Usuario, Usuario.id_usuario == Resuelve.id_usuario)
            .join(Reto, Reto.id_reto == Resuelve.id_reto)
            .where(
                Resuelve.id_evento == id_evento,
                Resuelve.flag_correcta == True,  # noqa: E712
            )
            .order_by(Resuelve.fec_envio.desc())
            .limit(limite)
        ).all()
    return [
        {
            "participante": alias or nombre,
            "reto": titulo,
            "hora": _aware(fec).strftime("%d/%m %H:%M") if fec else "—",
        }
        for alias, nombre, titulo, fec in filas
    ]
