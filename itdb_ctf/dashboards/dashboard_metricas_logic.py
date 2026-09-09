"""Consultas de métricas compartidas por los dashboards de eventos.

Todas las funciones reciben un `id_evento` y abren su propia `Session`, leyendo
directo de `models.py`. Sirven tanto para el evento abierto como para los
eventos cerrados. Si `id_evento` es falsy devuelven estructuras vacías.
"""

from sqlmodel import Session, select
from sqlalchemy import func

from itdb_ctf.db import engine
from itdb_ctf.models import (
    Participa,
    EstadoInscripcion,
    Resuelve,
    Contiene,
    Reto,
    Categoria,
    Dificultad,
    Pista,
    Compra,
)

RESUMEN_VACIO: dict = {
    "hay_evento": False,
    "participantes_total": 0,
    "participantes_inscritos": 0,
    "participantes_descalificados": 0,
    "participantes_activos": 0,
    "pct_participacion": 0.0,
    "retos_total": 0,
    "retos_activos": 0,
    "retos_inactivos": 0,
    "envios_total": 0,
    "envios_correctos": 0,
    "envios_incorrectos": 0,
    "tasa_acierto": 0.0,
    "resoluciones_total": 0,
    "puntaje_en_juego": 0,
    "pistas_disponibles": 0,
    "pistas_compradas": 0,
    "puntos_gastados_pistas": 0,
}


def resumen_evento(id_evento: int | None) -> dict:
    """KPIs numéricos de un evento (participación, envíos, puntaje, pistas)."""
    if not id_evento:
        return dict(RESUMEN_VACIO)

    with Session(engine) as s:
        filas_estado = s.exec(
            select(EstadoInscripcion.etiqueta, func.count(Participa.id_participa))
            .join(Participa, Participa.id_estado_inscripcion == EstadoInscripcion.id_estado_inscripcion)
            .where(Participa.id_evento == id_evento)
            .group_by(EstadoInscripcion.etiqueta)
        ).all()
        por_estado = {et: n for et, n in filas_estado}
        inscritos = por_estado.get("inscrito", 0)
        descalificados = por_estado.get("descalificado", 0)

        activos = s.exec(
            select(func.count(func.distinct(Resuelve.id_usuario))).where(
                Resuelve.id_evento == id_evento
            )
        ).one()

        filas_retos = s.exec(
            select(Reto.activo, func.count(Contiene.id_contiene))
            .join(Reto, Reto.id_reto == Contiene.id_reto)
            .where(Contiene.id_evento == id_evento)
            .group_by(Reto.activo)
        ).all()
        por_activo = {bool(a): n for a, n in filas_retos}
        retos_activos = por_activo.get(True, 0)
        retos_inactivos = por_activo.get(False, 0)

        envios_total = s.exec(
            select(func.count(Resuelve.id_resuelve)).where(Resuelve.id_evento == id_evento)
        ).one()
        envios_correctos = s.exec(
            select(func.count(Resuelve.id_resuelve)).where(
                Resuelve.id_evento == id_evento,
                Resuelve.flag_correcta == True,  # noqa: E712
            )
        ).one()

        puntaje_en_juego = s.exec(
            select(func.coalesce(func.sum(Contiene.puntaje_inicial), 0)).where(
                Contiene.id_evento == id_evento
            )
        ).one()

        pistas_disponibles = s.exec(
            select(func.count(Pista.id_pista))
            .join(Reto, Reto.id_reto == Pista.id_reto)
            .join(Contiene, Contiene.id_reto == Reto.id_reto)
            .where(Contiene.id_evento == id_evento, Pista.activo == True)  # noqa: E712
        ).one()
        pistas_compradas = s.exec(
            select(func.count(Compra.id_compra)).where(Compra.id_evento == id_evento)
        ).one()
        puntos_gastados = s.exec(
            select(func.coalesce(func.sum(Compra.puntos_usados), 0)).where(
                Compra.id_evento == id_evento
            )
        ).one()

    envios_incorrectos = envios_total - envios_correctos
    tasa = round(envios_correctos / envios_total * 100, 1) if envios_total else 0.0
    pct_part = round(activos / inscritos * 100, 1) if inscritos else 0.0

    return {
        "hay_evento": True,
        "participantes_total": inscritos + descalificados,
        "participantes_inscritos": inscritos,
        "participantes_descalificados": descalificados,
        "participantes_activos": activos,
        "pct_participacion": pct_part,
        "retos_total": retos_activos + retos_inactivos,
        "retos_activos": retos_activos,
        "retos_inactivos": retos_inactivos,
        "envios_total": envios_total,
        "envios_correctos": envios_correctos,
        "envios_incorrectos": envios_incorrectos,
        "tasa_acierto": tasa,
        "resoluciones_total": envios_correctos,
        "puntaje_en_juego": puntaje_en_juego,
        "pistas_disponibles": pistas_disponibles,
        "pistas_compradas": pistas_compradas,
        "puntos_gastados_pistas": puntos_gastados,
    }


def desglose_categoria(id_evento: int | None) -> list[dict]:
    """Retos y resoluciones del evento agrupados por categoría."""
    if not id_evento:
        return []
    with Session(engine) as s:
        filas_retos = s.exec(
            select(
                Categoria.id_categoria,
                Categoria.etiqueta,
                func.count(func.distinct(Contiene.id_contiene)),
            )
            .join(Reto, Reto.id_categoria == Categoria.id_categoria)
            .join(Contiene, Contiene.id_reto == Reto.id_reto)
            .where(Contiene.id_evento == id_evento)
            .group_by(Categoria.id_categoria, Categoria.etiqueta)
            .order_by(Categoria.id_categoria)
        ).all()

        filas_resol = s.exec(
            select(Reto.id_categoria, func.count(Resuelve.id_resuelve))
            .join(Resuelve, Resuelve.id_reto == Reto.id_reto)
            .where(
                Resuelve.id_evento == id_evento,
                Resuelve.flag_correcta == True,  # noqa: E712
            )
            .group_by(Reto.id_categoria)
        ).all()
        resol_map = {cid: n for cid, n in filas_resol}

    return [
        {"etiqueta": etiqueta, "retos": n_retos, "resoluciones": resol_map.get(cid, 0)}
        for cid, etiqueta, n_retos in filas_retos
    ]


def desglose_dificultad(id_evento: int | None) -> list[dict]:
    """Retos y resoluciones del evento agrupados por dificultad."""
    if not id_evento:
        return []
    with Session(engine) as s:
        filas_retos = s.exec(
            select(
                Dificultad.id_dificultad,
                Dificultad.etiqueta,
                func.count(func.distinct(Contiene.id_contiene)),
            )
            .join(Reto, Reto.id_dificultad == Dificultad.id_dificultad)
            .join(Contiene, Contiene.id_reto == Reto.id_reto)
            .where(Contiene.id_evento == id_evento)
            .group_by(Dificultad.id_dificultad, Dificultad.etiqueta)
            .order_by(Dificultad.id_dificultad)
        ).all()

        filas_resol = s.exec(
            select(Reto.id_dificultad, func.count(Resuelve.id_resuelve))
            .join(Resuelve, Resuelve.id_reto == Reto.id_reto)
            .where(
                Resuelve.id_evento == id_evento,
                Resuelve.flag_correcta == True,  # noqa: E712
            )
            .group_by(Reto.id_dificultad)
        ).all()
        resol_map = {did: n for did, n in filas_resol}

    return [
        {"etiqueta": etiqueta, "retos": n_retos, "resoluciones": resol_map.get(did, 0)}
        for did, etiqueta, n_retos in filas_retos
    ]


def ranking_retos_resoluciones(id_evento: int | None) -> list[dict]:
    """Retos del evento ordenados por nº de resoluciones (desc). Incluye los de 0."""
    if not id_evento:
        return []
    with Session(engine) as s:
        retos = s.exec(
            select(
                Reto.id_reto,
                Reto.titulo,
                Categoria.etiqueta,
                Dificultad.etiqueta,
                Contiene.puntaje_inicial,
                Reto.activo,
            )
            .join(Contiene, Contiene.id_reto == Reto.id_reto)
            .join(Categoria, Categoria.id_categoria == Reto.id_categoria)
            .join(Dificultad, Dificultad.id_dificultad == Reto.id_dificultad)
            .where(Contiene.id_evento == id_evento)
        ).all()

        filas_resol = s.exec(
            select(Resuelve.id_reto, func.count(Resuelve.id_resuelve))
            .where(
                Resuelve.id_evento == id_evento,
                Resuelve.flag_correcta == True,  # noqa: E712
            )
            .group_by(Resuelve.id_reto)
        ).all()
        resol_map = {rid: n for rid, n in filas_resol}

    salida = [
        {
            "titulo": titulo,
            "categoria": cat,
            "dificultad": dif,
            "puntaje": puntaje,
            "resoluciones": resol_map.get(rid, 0),
            "sin_resolver": resol_map.get(rid, 0) == 0,
            "activo": bool(activo),
        }
        for rid, titulo, cat, dif, puntaje, activo in retos
    ]
    salida.sort(key=lambda r: -r["resoluciones"])
    return salida
