"""Consultas del padrón de usuarios para el dashboard de usuarios.

Las métricas de padrón (total, roles, métodos, registros, placeholders,
sin participar) son siempre globales. El `id_evento` solo filtra lo relativo a
participación: participantes, descalificados, top solvers y autores.
Todas abren su propia `Session` y leen directo de `models.py`.
"""

from datetime import datetime, timezone

from sqlmodel import Session, select
from sqlalchemy import func

from itdb_ctf.db import engine
from itdb_ctf.models import (
    Usuario,
    Rol,
    MetodoAuth,
    Participa,
    EstadoInscripcion,
    Resuelve,
    Reto,
    Contiene,
    Evento,
    Modalidad,
)
from itdb_ctf.dashboards.retos_dashboard_logic import listar_eventos_opciones  # noqa: F401


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


def _id_estado(s, etiqueta: str):
    return s.exec(
        select(EstadoInscripcion.id_estado_inscripcion).where(
            EstadoInscripcion.etiqueta == etiqueta
        )
    ).first()


def resumen_usuarios(id_evento: int | None = None) -> dict:
    with Session(engine) as s:
        filas_activo = s.exec(
            select(Usuario.activo, func.count(Usuario.id_usuario)).group_by(Usuario.activo)
        ).all()
        por_activo = {bool(a): n for a, n in filas_activo}
        activos = por_activo.get(True, 0)
        inactivos = por_activo.get(False, 0)

        filas_rol = s.exec(
            select(Rol.codigo, func.count(Usuario.id_usuario))
            .join(Usuario, Usuario.id_rol == Rol.id_rol)
            .group_by(Rol.codigo)
        ).all()
        por_rol = {cod: n for cod, n in filas_rol}

        filas_metodo = s.exec(
            select(MetodoAuth.etiqueta, func.count(Usuario.id_usuario))
            .join(Usuario, Usuario.id_metodo_auth == MetodoAuth.id_metodo_auth)
            .group_by(MetodoAuth.etiqueta)
        ).all()
        por_metodo = {et: n for et, n in filas_metodo}

        placeholders = s.exec(
            select(func.count(Usuario.id_usuario)).where(
                Usuario.paterno == "placeholder",
                Usuario.materno == "placeholder",
            )
        ).one()

        q_part = select(func.count(func.distinct(Participa.id_usuario)))
        if id_evento:
            q_part = q_part.where(Participa.id_evento == id_evento)
        participantes = s.exec(q_part).one()

        est_descal = _id_estado(s, "descalificado")
        descalificados = 0
        if est_descal is not None:
            q_des = (
                select(func.count(func.distinct(Participa.id_usuario)))
                .join(Evento, Evento.id_evento == Participa.id_evento)
                .join(Modalidad, Modalidad.id_modalidad == Evento.id_modalidad)
                .where(
                    Participa.id_estado_inscripcion == est_descal,
                    Modalidad.etiqueta == "cerrado",
                )
            )
            if id_evento:
                q_des = q_des.where(Participa.id_evento == id_evento)
            descalificados = s.exec(q_des).one()

        rol_user = s.exec(select(Rol.id_rol).where(Rol.codigo == "user")).first()
        con_participacion = select(Participa.id_usuario).distinct()
        sin_participar = 0
        if rol_user is not None:
            sin_participar = s.exec(
                select(func.count(Usuario.id_usuario)).where(
                    Usuario.id_rol == rol_user,
                    Usuario.activo == True,  # noqa: E712
                    Usuario.id_usuario.not_in(con_participacion),
                )
            ).one()

    return {
        "total": activos + inactivos,
        "activos": activos,
        "inactivos": inactivos,
        "superadmin": por_rol.get("superadmin", 0),
        "admin": por_rol.get("admin", 0),
        "autor": por_rol.get("autor", 0),
        "user": por_rol.get("user", 0),
        "google": por_metodo.get("google", 0),
        "local": por_metodo.get("local", 0),
        "placeholders": placeholders,
        "participantes": participantes,
        "descalificados": descalificados,
        "sin_participar": sin_participar,
    }


def usuarios_por_rol() -> list[dict]:
    with Session(engine) as s:
        filas = s.exec(
            select(Rol.etiqueta, func.count(Usuario.id_usuario))
            .join(Usuario, Usuario.id_rol == Rol.id_rol)
            .group_by(Rol.id_rol, Rol.etiqueta)
            .order_by(Rol.id_rol)
        ).all()
    return [{"etiqueta": et, "valor": n} for et, n in filas]


def usuarios_por_metodo() -> list[dict]:
    with Session(engine) as s:
        filas = s.exec(
            select(MetodoAuth.etiqueta, func.count(Usuario.id_usuario))
            .join(Usuario, Usuario.id_metodo_auth == MetodoAuth.id_metodo_auth)
            .group_by(MetodoAuth.id_metodo_auth, MetodoAuth.etiqueta)
            .order_by(MetodoAuth.id_metodo_auth)
        ).all()
    return [{"etiqueta": et, "valor": n} for et, n in filas]


def registros_por_mes(meses: int = 12) -> list[dict]:
    with Session(engine) as s:
        fechas = s.exec(select(Usuario.fec_registro)).all()
    return _serie_por_mes(fechas, meses)


def top_solvers(id_evento: int | None = None, limite: int = 15) -> list[dict]:
    with Session(engine) as s:
        stmt = (
            select(Usuario.alias, Usuario.nombre, func.count(Resuelve.id_resuelve))
            .join(Resuelve, Resuelve.id_usuario == Usuario.id_usuario)
            .where(Resuelve.flag_correcta == True)  # noqa: E712
        )
        if id_evento:
            stmt = stmt.where(Resuelve.id_evento == id_evento)
        filas = s.exec(
            stmt.group_by(Usuario.id_usuario, Usuario.alias, Usuario.nombre)
            .order_by(func.count(Resuelve.id_resuelve).desc())
            .limit(limite)
        ).all()
    return [{"alias": ali or nom, "resoluciones": n} for ali, nom, n in filas]


def usuarios_sin_participar() -> list[dict]:
    """Siempre global: estudiantes activos sin NINGUNA participación."""
    with Session(engine) as s:
        rol_user = s.exec(select(Rol.id_rol).where(Rol.codigo == "user")).first()
        if rol_user is None:
            return []
        con_participacion = select(Participa.id_usuario).distinct()
        filas = s.exec(
            select(Usuario.alias, Usuario.nombre, Usuario.email_inst, Usuario.fec_registro)
            .where(
                Usuario.id_rol == rol_user,
                Usuario.activo == True,  # noqa: E712
                Usuario.id_usuario.not_in(con_participacion),
            )
            .order_by(Usuario.fec_registro.desc())
        ).all()
    return [
        {
            "alias": ali or nom,
            "email": email,
            "registro": fec.strftime("%d/%m/%y") if fec else "—",
        }
        for ali, nom, email, fec in filas
    ]


def descalificados_lista(id_evento: int | None = None) -> list[dict]:
    """Usuarios descalificados de eventos cerrados: alias · correo · evento."""
    with Session(engine) as s:
        est_descal = _id_estado(s, "descalificado")
        if est_descal is None:
            return []
        stmt = (
            select(Usuario.alias, Usuario.nombre, Usuario.email_inst, Evento.titulo)
            .join(Participa, Participa.id_usuario == Usuario.id_usuario)
            .join(Evento, Evento.id_evento == Participa.id_evento)
            .join(Modalidad, Modalidad.id_modalidad == Evento.id_modalidad)
            .where(
                Participa.id_estado_inscripcion == est_descal,
                Modalidad.etiqueta == "cerrado",
            )
        )
        if id_evento:
            stmt = stmt.where(Participa.id_evento == id_evento)
        filas = s.exec(stmt.order_by(Evento.id_evento)).all()
    return [
        {"alias": ali or nom, "email": email, "evento": titulo}
        for ali, nom, email, titulo in filas
    ]


def autores_por_retos(id_evento: int | None = None) -> list[dict]:
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
