"""Consultas del perfil del jugador para un evento dado.

Todas reciben `(id_usuario, id_evento)`, abren su propia `Session` y leen directo
de `models.py`.
"""

from sqlmodel import Session, select
from sqlalchemy import func

from itdb_ctf.db import engine
from itdb_ctf.models import (
    Usuario,
    Participa,
    Resuelve,
    Contiene,
    Reto,
    Categoria,
    Dificultad,
    Compra,
)
from itdb_ctf.core.puntaje_logic import puntaje_total_usuario
from itdb_ctf.scoreboard.scoreboard_logic import scoreboard


def _iniciales(nombre: str | None, paterno: str | None) -> str:
    a = (nombre or "").strip()
    b = (paterno or "").strip()
    return ((a[:1] + b[:1]) or "?").upper()


def participa(id_usuario: int | None, id_evento: int | None) -> bool:
    if not id_usuario or not id_evento:
        return False
    with Session(engine) as s:
        fila = s.exec(
            select(Participa.id_participa).where(
                Participa.id_usuario == id_usuario,
                Participa.id_evento == id_evento,
            )
        ).first()
    return fila is not None


def perfil_datos(id_usuario: int | None, id_evento: int | None) -> dict:
    if not id_usuario or not id_evento:
        return {"inscrito": False}
    with Session(engine) as s:
        u = s.get(Usuario, id_usuario)
        if not u:
            return {"inscrito": False}

        retos_total = s.exec(
            select(func.count(Contiene.id_contiene)).where(Contiene.id_evento == id_evento)
        ).one()
        resueltos = s.exec(
            select(func.count(Resuelve.id_resuelve)).where(
                Resuelve.id_usuario == id_usuario,
                Resuelve.id_evento == id_evento,
                Resuelve.flag_correcta == True,  # noqa: E712
            )
        ).one()
        envios_total = s.exec(
            select(func.count(Resuelve.id_resuelve)).where(
                Resuelve.id_usuario == id_usuario,
                Resuelve.id_evento == id_evento,
            )
        ).one()
        puntaje = puntaje_total_usuario(s, id_usuario, id_evento)

        alias = u.alias
        nombre = f"{u.nombre} {u.paterno}".strip()
        iniciales = _iniciales(u.nombre, u.paterno)
        email = u.email_inst
        avatar = u.avatar or ""

    rank = scoreboard(id_evento)
    total = len(rank)
    posicion = next(
        (r["posicion"] for r in rank if r["id_usuario"] == id_usuario), None
    )

    pct = round(resueltos / retos_total * 100) if retos_total else 0

    return {
        "inscrito": True,
        "alias": alias or nombre,
        "nombre": nombre,
        "iniciales": iniciales,
        "email": email,
        "avatar": avatar,
        "puntaje": puntaje,
        "posicion": str(posicion) if posicion is not None else "—",
        "total": total,
        "resueltos": resueltos,
        "retos_total": retos_total,
        "pct_progreso": pct,
        "envios_correctos": resueltos,
        "envios_incorrectos": envios_total - resueltos,
    }


def retos_resueltos(id_usuario: int | None, id_evento: int | None) -> list[dict]:
    if not id_usuario or not id_evento:
        return []
    with Session(engine) as s:
        filas = s.exec(
            select(
                Reto.titulo,
                Categoria.etiqueta,
                Dificultad.etiqueta,
                Contiene.puntaje_inicial,
                Resuelve.fec_envio,
            )
            .join(Resuelve, Resuelve.id_reto == Reto.id_reto)
            .join(
                Contiene,
                (Contiene.id_reto == Reto.id_reto)
                & (Contiene.id_evento == Resuelve.id_evento),
            )
            .join(Categoria, Categoria.id_categoria == Reto.id_categoria)
            .join(Dificultad, Dificultad.id_dificultad == Reto.id_dificultad)
            .where(
                Resuelve.id_usuario == id_usuario,
                Resuelve.id_evento == id_evento,
                Resuelve.flag_correcta == True,  # noqa: E712
            )
            .order_by(Resuelve.fec_envio)
        ).all()
    return [
        {
            "titulo": titulo,
            "categoria": cat,
            "dificultad": dif,
            "puntaje": puntaje,
            "fecha": fec.strftime("%d/%m/%y %H:%M") if fec else "—",
        }
        for titulo, cat, dif, puntaje, fec in filas
    ]


def distribucion_categorias(id_usuario: int | None, id_evento: int | None) -> list[dict]:
    """Reparto de los retos resueltos por el jugador entre categorías.

    Solo categorías con >0, ordenadas desc; cada una con su porcentaje sobre el
    total de resueltos del jugador ("allocation overview").
    """
    if not id_usuario or not id_evento:
        return []
    with Session(engine) as s:
        filas = s.exec(
            select(Categoria.etiqueta, func.count(Resuelve.id_resuelve))
            .join(Reto, Reto.id_categoria == Categoria.id_categoria)
            .join(Resuelve, Resuelve.id_reto == Reto.id_reto)
            .where(
                Resuelve.id_usuario == id_usuario,
                Resuelve.id_evento == id_evento,
                Resuelve.flag_correcta == True,  # noqa: E712
            )
            .group_by(Categoria.id_categoria, Categoria.etiqueta)
        ).all()

    total = sum(n for _, n in filas)
    if not total:
        return []
    datos = [
        {"etiqueta": et, "valor": n, "pct": round(n / total * 100, 1)}
        for et, n in filas
    ]
    datos.sort(key=lambda d: -d["valor"])
    return datos


def reparto_puntos(id_usuario: int | None, id_evento: int | None) -> list[dict]:
    """Reparto de los puntos brutos del jugador: los que conserva vs. los gastados
    en pistas ("allocation" sobre el total obtenido)."""
    if not id_usuario or not id_evento:
        return []
    with Session(engine) as s:
        ganados = s.exec(
            select(func.coalesce(func.sum(Contiene.puntaje_actual), 0))
            .join(
                Resuelve,
                (Contiene.id_reto == Resuelve.id_reto)
                & (Contiene.id_evento == Resuelve.id_evento),
            )
            .where(
                Resuelve.id_usuario == id_usuario,
                Resuelve.id_evento == id_evento,
                Resuelve.flag_correcta == True,  # noqa: E712
            )
        ).one()
        gastados = s.exec(
            select(func.coalesce(func.sum(Compra.puntos_usados), 0)).where(
                Compra.id_usuario == id_usuario,
                Compra.id_evento == id_evento,
            )
        ).one()

    if not ganados:
        return []
    neto = max(ganados - gastados, 0)
    return [
        {"etiqueta": "Puntaje", "valor": neto, "pct": round(neto / ganados * 100, 1)},
        {"etiqueta": "En pistas", "valor": gastados, "pct": round(gastados / ganados * 100, 1)},
    ]


def aciertos_errores(id_usuario: int | None, id_evento: int | None) -> list[dict]:
    """Reparto de los envíos del jugador: correctos vs. incorrectos."""
    if not id_usuario or not id_evento:
        return []
    with Session(engine) as s:
        total = s.exec(
            select(func.count(Resuelve.id_resuelve)).where(
                Resuelve.id_usuario == id_usuario,
                Resuelve.id_evento == id_evento,
            )
        ).one()
        ok = s.exec(
            select(func.count(Resuelve.id_resuelve)).where(
                Resuelve.id_usuario == id_usuario,
                Resuelve.id_evento == id_evento,
                Resuelve.flag_correcta == True,  # noqa: E712
            )
        ).one()
    if not total:
        return []
    err = total - ok
    return [
        {"etiqueta": "Aciertos", "valor": ok, "pct": round(ok / total * 100, 1)},
        {"etiqueta": "Errores", "valor": err, "pct": round(err / total * 100, 1)},
    ]
