"""Consultas para el dashboard de retos.

Todas aceptan:
- `id_evento: int | None` — `None` = todos los eventos; un id = solo los retos de
  ese evento y sus resoluciones.
- `id_autor: int | None` — `None` = todos los autores; un id = solo los retos
  creados por ese usuario.

Abren su propia `Session` y leen directo de `models.py`.
"""

from datetime import datetime, timezone

from sqlmodel import Session, select
from sqlalchemy import func

from itdb_ctf.db import engine
from itdb_ctf.models import (
    Reto,
    Contiene,
    Resuelve,
    Pista,
    Categoria,
    Dificultad,
    ModoPuntaje,
    Usuario,
    Evento,
)


def _scope_reto(stmt, id_evento, id_autor):
    if id_evento:
        stmt = stmt.join(Contiene, Contiene.id_reto == Reto.id_reto).where(
            Contiene.id_evento == id_evento
        )
    if id_autor:
        stmt = stmt.where(Reto.id_usuario == id_autor)
    return stmt


def _scope_resuelve(stmt, id_evento, id_autor):
    if id_evento:
        stmt = stmt.where(Resuelve.id_evento == id_evento)
    if id_autor:
        stmt = stmt.where(
            Resuelve.id_reto.in_(
                select(Reto.id_reto).where(Reto.id_usuario == id_autor)
            )
        )
    return stmt


def _claves_meses(meses: int) -> list[tuple[int, int]]:
    ahora = datetime.now(timezone.utc)
    claves: list[tuple[int, int]] = []
    y, m = ahora.year, ahora.month
    for _ in range(meses):
        claves.append((y, m))
        m -= 1
        if m == 0:
            m, y = 12, y - 1
    claves.reverse()
    return claves


def _serie_por_mes(fechas, meses: int = 12) -> list[dict]:
    conteo: dict = {}
    for fec in fechas:
        if fec is None:
            continue
        k = (fec.year, fec.month)
        conteo[k] = conteo.get(k, 0) + 1
    return [
        {"etiqueta": f"{m:02d}/{str(y)[2:]}", "valor": conteo.get((y, m), 0)}
        for y, m in _claves_meses(meses)
    ]


def resumen_retos(id_evento: int | None = None, id_autor: int | None = None) -> dict:
    with Session(engine) as s:
        filas_activo = s.exec(
            _scope_reto(
                select(Reto.activo, func.count(func.distinct(Reto.id_reto))),
                id_evento, id_autor,
            ).group_by(Reto.activo)
        ).all()
        por_activo = {bool(a): n for a, n in filas_activo}
        activos = por_activo.get(True, 0)
        inactivos = por_activo.get(False, 0)

        if id_evento:
            aislados = 0
        else:
            vinculados = select(Contiene.id_reto).distinct()
            q_ais = select(func.count(Reto.id_reto)).where(
                Reto.activo == True,  # noqa: E712
                Reto.id_reto.not_in(vinculados),
            )
            if id_autor:
                q_ais = q_ais.where(Reto.id_usuario == id_autor)
            aislados = s.exec(q_ais).one()

        resueltos_ids = _scope_resuelve(
            select(Resuelve.id_reto).where(Resuelve.flag_correcta == True),  # noqa: E712
            id_evento, id_autor,
        ).distinct()
        nunca_resueltos = s.exec(
            _scope_reto(
                select(func.count(func.distinct(Reto.id_reto))).where(
                    Reto.id_reto.not_in(resueltos_ids)
                ),
                id_evento, id_autor,
            )
        ).one()

        retos_con_pistas = s.exec(
            _scope_reto(
                select(func.count(func.distinct(Reto.id_reto)))
                .join(Pista, Pista.id_reto == Reto.id_reto),
                id_evento, id_autor,
            )
        ).one()

        sin_archivo = s.exec(
            _scope_reto(
                select(func.count(func.distinct(Reto.id_reto))).where(
                    Reto.archivo_ruta == None  # noqa: E711
                ),
                id_evento, id_autor,
            )
        ).one()

        envios = s.exec(
            _scope_resuelve(select(func.count(Resuelve.id_resuelve)), id_evento, id_autor)
        ).one()
        correctos = s.exec(
            _scope_resuelve(
                select(func.count(Resuelve.id_resuelve)).where(
                    Resuelve.flag_correcta == True  # noqa: E712
                ),
                id_evento, id_autor,
            )
        ).one()

    total = activos + inactivos
    return {
        "total": total,
        "activos": activos,
        "inactivos": inactivos,
        "aislados": aislados,
        "nunca_resueltos": nunca_resueltos,
        "retos_con_pistas": retos_con_pistas,
        "con_archivo": total - sin_archivo,
        "sin_archivo": sin_archivo,
        "resoluciones": correctos,
        "tasa_acierto": round(correctos / envios * 100, 1) if envios else 0.0,
    }


def listar_eventos_opciones() -> list[list[str]]:
    with Session(engine) as s:
        evs = s.exec(
            select(Evento.id_evento, Evento.titulo).order_by(Evento.id_evento)
        ).all()
    return [["todos", "Todos los eventos"]] + [[str(eid), tit] for eid, tit in evs]


def retos_desglose_categoria(id_evento: int | None = None, id_autor: int | None = None) -> list[dict]:
    with Session(engine) as s:
        retos = s.exec(
            _scope_reto(
                select(
                    Categoria.id_categoria,
                    Categoria.etiqueta,
                    func.count(func.distinct(Reto.id_reto)),
                ).join(Reto, Reto.id_categoria == Categoria.id_categoria),
                id_evento, id_autor,
            )
            .group_by(Categoria.id_categoria, Categoria.etiqueta)
            .order_by(Categoria.id_categoria)
        ).all()
        resol = s.exec(
            _scope_resuelve(
                select(Reto.id_categoria, func.count(Resuelve.id_resuelve))
                .join(Resuelve, Resuelve.id_reto == Reto.id_reto)
                .where(Resuelve.flag_correcta == True),  # noqa: E712
                id_evento, id_autor,
            ).group_by(Reto.id_categoria)
        ).all()
        rmap = {cid: n for cid, n in resol}
    return [
        {"etiqueta": et, "retos": n, "resoluciones": rmap.get(cid, 0)}
        for cid, et, n in retos
    ]


def retos_desglose_dificultad(id_evento: int | None = None, id_autor: int | None = None) -> list[dict]:
    with Session(engine) as s:
        retos = s.exec(
            _scope_reto(
                select(
                    Dificultad.id_dificultad,
                    Dificultad.etiqueta,
                    func.count(func.distinct(Reto.id_reto)),
                ).join(Reto, Reto.id_dificultad == Dificultad.id_dificultad),
                id_evento, id_autor,
            )
            .group_by(Dificultad.id_dificultad, Dificultad.etiqueta)
            .order_by(Dificultad.id_dificultad)
        ).all()
        resol = s.exec(
            _scope_resuelve(
                select(Reto.id_dificultad, func.count(Resuelve.id_resuelve))
                .join(Resuelve, Resuelve.id_reto == Reto.id_reto)
                .where(Resuelve.flag_correcta == True),  # noqa: E712
                id_evento, id_autor,
            ).group_by(Reto.id_dificultad)
        ).all()
        rmap = {did: n for did, n in resol}
    return [
        {"etiqueta": et, "retos": n, "resoluciones": rmap.get(did, 0)}
        for did, et, n in retos
    ]


def retos_por_modo(id_evento: int | None = None, id_autor: int | None = None) -> list[dict]:
    with Session(engine) as s:
        filas = s.exec(
            _scope_reto(
                select(ModoPuntaje.etiqueta, func.count(func.distinct(Reto.id_reto)))
                .join(Reto, Reto.id_modo_puntaje == ModoPuntaje.id_modo_puntaje),
                id_evento, id_autor,
            )
            .group_by(ModoPuntaje.id_modo_puntaje, ModoPuntaje.etiqueta)
            .order_by(ModoPuntaje.id_modo_puntaje)
        ).all()
    return [{"etiqueta": et, "valor": n} for et, n in filas]


def retos_creados_por_mes(id_evento: int | None = None, id_autor: int | None = None, meses: int = 12) -> list[dict]:
    with Session(engine) as s:
        filas = s.exec(
            _scope_reto(select(Reto.id_reto, Reto.fec_creacion), id_evento, id_autor)
        ).all()
    return _serie_por_mes([fec for _rid, fec in filas], meses)


def retos_resoluciones_por_evento(id_evento: int | None = None, id_autor: int | None = None) -> list[dict]:
    """Por cada evento: nº de retos (del scope) que contiene y sus resoluciones."""
    with Session(engine) as s:
        q_ev = select(Evento.id_evento, Evento.titulo).order_by(Evento.id_evento)
        if id_evento:
            q_ev = q_ev.where(Evento.id_evento == id_evento)
        eventos = s.exec(q_ev).all()

        q_ret = select(Contiene.id_evento, func.count(func.distinct(Contiene.id_reto)))
        if id_autor:
            q_ret = q_ret.join(Reto, Reto.id_reto == Contiene.id_reto).where(
                Reto.id_usuario == id_autor
            )
        retos = s.exec(q_ret.group_by(Contiene.id_evento)).all()

        q_res = select(Resuelve.id_evento, func.count(Resuelve.id_resuelve)).where(
            Resuelve.flag_correcta == True  # noqa: E712
        )
        if id_autor:
            q_res = q_res.where(
                Resuelve.id_reto.in_(
                    select(Reto.id_reto).where(Reto.id_usuario == id_autor)
                )
            )
        resol = s.exec(q_res.group_by(Resuelve.id_evento)).all()

    r_map = {eid: n for eid, n in retos}
    s_map = {eid: n for eid, n in resol}
    salida = [
        {"titulo": tit, "retos": r_map.get(eid, 0), "resoluciones": s_map.get(eid, 0)}
        for eid, tit in eventos
    ]
    salida.sort(key=lambda x: -x["resoluciones"])
    return salida


def retos_por_autor(id_evento: int | None = None) -> list[dict]:
    """Solo tiene sentido en la vista global (no se filtra por autor)."""
    with Session(engine) as s:
        stmt = (
            select(Usuario.alias, Usuario.nombre, func.count(func.distinct(Reto.id_reto)))
            .join(Reto, Reto.id_usuario == Usuario.id_usuario)
        )
        if id_evento:
            stmt = stmt.join(Contiene, Contiene.id_reto == Reto.id_reto).where(
                Contiene.id_evento == id_evento
            )
        filas = s.exec(
            stmt.group_by(Usuario.id_usuario, Usuario.alias, Usuario.nombre)
            .order_by(func.count(func.distinct(Reto.id_reto)).desc())
        ).all()
    return [{"autor": ali or nom, "retos": n} for ali, nom, n in filas]
