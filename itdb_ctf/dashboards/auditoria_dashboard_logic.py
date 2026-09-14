"""Lectura de la bitácora de auditoría (tabla `auditoria`).

Las filas las escriben 13 triggers de Postgres (ver scripts/auditoria_up.sql); aquí
solo se leen. `Auditoria.id_usuario` no tiene FK y puede ser NULL (escrituras de
sistema: seed, scripts), así que el join a Usuario es siempre OUTER.

Regla dura: los JSONB (`datos_antes`/`datos_despues`) NUNCA salen de este módulo.
Se consumen aquí y lo que viaja al State son `str` planos — un dict anidado rompe
el tipado `list[dict]` de Reflex.
"""

from datetime import datetime, timedelta, timezone

from sqlmodel import Session, select, func

from itdb_ctf.db import engine
from itdb_ctf.models import Auditoria, Usuario
from itdb_ctf.evento.evento_logic import listar_evento
from itdb_ctf.utils.auditoria import TABLAS_AUDITADAS
from itdb_ctf.websockets.redis_cliente import hay_redis

# el trigger ya los censura a "***"; aquí ni siquiera se muestra el asterisco
CAMPOS_OCULTOS = {"password_hash", "flag"}

LIMITE_INICIAL = 100
LIMITE_MAXIMO = 500

RESUMEN_VACIO = {
    "total": 0, "inserts": 0, "updates": 0, "deletes": 0,
    "actores": 0, "sistema": 0, "dias": 30,
    "ultimo_texto": "—", "ultima_fecha": "—",
}

SALUD_VACIA = {
    "redis": False, "hay_abierto": False, "evento_abierto": "",
    "eventos_total": 0, "activos": 0, "futuros": 0,
    "concluidos": 0, "congelados": 0,
}

# ENTIDADES: se identifican por su nombre propio (titulo / alias / correo)
_CAMPO_NOMBRE = {
    "usuario": ("alias", "email_inst"),
    "evento": ("titulo",),
    "reto": ("titulo",),
    "pista": ("descripcion",),
}
# ASOCIATIVAS: no tienen nombre propio -> "registro"
_TABLAS_ASOCIATIVAS = ("participa", "contiene")
# el resto de las auditadas son catálogos -> "catalogo"


###     PRIVADAS


def _aware(dt):
    if dt is None:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _desde(dias):
    """None / 0 => sin recorte de fecha (todo el historial)."""
    if not dias:
        return None
    return datetime.now(timezone.utc) - timedelta(days=int(dias))


def _hace(dt) -> str:
    dt = _aware(dt)
    if not dt:
        return "—"
    seg = (datetime.now(timezone.utc) - dt).total_seconds()
    if seg < 60:
        return "hace instantes"
    if seg < 3600:
        return f"hace {int(seg // 60)} min"
    if seg < 86400:
        return f"hace {int(seg // 3600)} h"
    return f"hace {int(seg // 86400)} d"


def _claves_dias(dias: int) -> list:
    hoy = datetime.now(timezone.utc).date()
    return [hoy - timedelta(days=i) for i in range(dias - 1, -1, -1)]


def _nombre_actor(alias, nombre, paterno) -> str:
    if alias:
        return alias
    return f"{nombre or ''} {paterno or ''}".strip() or "—"


def _fmt_valor(v) -> str:
    """Los valores van tal como están en la BD: nada de traducir booleanos
    ni NULL — esto es una bitácora, no una vista de usuario."""
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (dict, list)):
        return "{...}"
    texto = str(v)
    return texto[:28] + "..." if len(texto) > 28 else texto


def _descriptor(tabla: str, antes, despues, id_registro) -> str:
    """Entidad -> su nombre; asociativa -> «registro»; catálogo -> «catalogo»."""
    if tabla in _TABLAS_ASOCIATIVAS:
        return "registro"
    if tabla not in _CAMPO_NOMBRE:
        return "catalogo"

    fuente = despues or antes or {}
    for clave in _CAMPO_NOMBRE[tabla]:
        valor = fuente.get(clave)
        if valor not in (None, ""):
            return _fmt_valor(valor)
    return f"#{id_registro}" if id_registro is not None else tabla


def _resumen_cambios(campos, maximo: int = 4) -> str:
    """Solo los nombres de los campos que cambiaron (la UI los pinta en gris).
    Vacío en INSERT/DELETE: ahí la propia operación es el dato."""
    if not campos:
        return ""
    nombres = list(campos[:maximo])
    resto = len(campos) - maximo
    if resto > 0:
        nombres.append(f"+{resto}")
    return ", ".join(nombres)


def _filtrar(stmt, *, tabla=None, operacion=None, actor=None, dias=None):
    """Único punto donde se traducen los valores de los selects a WHERE."""
    if tabla:
        stmt = stmt.where(Auditoria.tabla == tabla)
    if operacion:
        stmt = stmt.where(Auditoria.operacion == operacion)
    if actor == "sistema":
        stmt = stmt.where(Auditoria.id_usuario == None)  # noqa: E711
    elif actor:
        stmt = stmt.where(Auditoria.id_usuario == int(actor))
    desde = _desde(dias)
    if desde is not None:
        stmt = stmt.where(Auditoria.fec_registro >= desde)
    return stmt


###     PUBLICAS


def resumen_auditoria(dias: int = 30) -> dict:
    desde = _desde(dias)
    with Session(engine) as s:
        por_op = dict(
            s.exec(
                select(Auditoria.operacion, func.count(Auditoria.id_auditoria))
                .where(Auditoria.fec_registro >= desde)
                .group_by(Auditoria.operacion)
            ).all()
        )
        actores = s.exec(
            select(func.count(func.distinct(Auditoria.id_usuario)))
            .where(Auditoria.fec_registro >= desde, Auditoria.id_usuario != None)  # noqa: E711
        ).one()
        sistema = s.exec(
            select(func.count(Auditoria.id_auditoria))
            .where(Auditoria.fec_registro >= desde, Auditoria.id_usuario == None)  # noqa: E711
        ).one()
        ultima = s.exec(select(func.max(Auditoria.fec_registro))).one()

    ultima = _aware(ultima)
    return {
        "total": sum(por_op.values()),
        "inserts": por_op.get("INSERT", 0),
        "updates": por_op.get("UPDATE", 0),
        "deletes": por_op.get("DELETE", 0),
        "actores": actores or 0,
        "sistema": sistema or 0,
        "dias": dias,
        "ultimo_texto": _hace(ultima),
        "ultima_fecha": ultima.strftime("%d/%m/%y %H:%M") if ultima else "—",
    }


def auditoria_por_dia(dias: int = 30) -> list[dict]:
    """Serie CONTINUA de `dias` puntos: sin relleno el sparkline miente."""
    desde = _desde(dias)
    dia = func.date_trunc("day", Auditoria.fec_registro)
    with Session(engine) as s:
        filas = s.exec(
            select(dia, func.count(Auditoria.id_auditoria))
            .where(Auditoria.fec_registro >= desde)
            .group_by(dia)
        ).all()

    mapa = {}
    for d, n in filas:
        d = _aware(d)
        if d:
            mapa[d.date()] = n
    return [
        {"etiqueta": k.strftime("%d/%m"), "valor": mapa.get(k, 0)}
        for k in _claves_dias(dias)
    ]


def salud_plataforma() -> dict:
    """Cero SQL nuevo: se deriva de listar_evento(), que ya trae estado y freeze."""
    salud = dict(SALUD_VACIA)
    salud["redis"] = hay_redis()
    try:
        eventos = listar_evento()
    except Exception:
        return salud

    salud["eventos_total"] = len(eventos)
    for e in eventos:
        estado = e.get("estado")
        if estado == "activo":
            salud["activos"] += 1
        elif estado == "futuro":
            salud["futuros"] += 1
        elif estado == "concluido":
            salud["concluidos"] += 1
        if e.get("freeze"):
            salud["congelados"] += 1
        if e.get("modalidad") == "abierto" and not salud["hay_abierto"]:
            salud["hay_abierto"] = True
            salud["evento_abierto"] = e.get("titulo") or "Evento abierto"
    return salud


def listar_tablas_opciones() -> list[list[str]]:
    return [["todas", "Todas las tablas"]] + [[t, t] for t in TABLAS_AUDITADAS]


def listar_operaciones_opciones() -> list[list[str]]:
    return [
        ["todas", "Todas las operaciones"],
        ["INSERT", "INSERT"],
        ["UPDATE", "UPDATE"],
        ["DELETE", "DELETE"],
    ]


def listar_periodos_opciones() -> list[list[str]]:
    return [
        ["1", "Últimas 24 horas"],
        ["7", "Últimos 7 días"],
        ["30", "Últimos 30 días"],
        ["90", "Últimos 90 días"],
        ["0", "Todo el historial"],
    ]


def listar_actores_opciones() -> list[list[str]]:
    """`sistema` se antepone siempre, haya o no filas sin actor."""
    with Session(engine) as s:
        sub = (
            select(Auditoria.id_usuario)
            .distinct()
            .where(Auditoria.id_usuario != None)  # noqa: E711
        )
        filas = s.exec(
            select(Usuario.id_usuario, Usuario.alias, Usuario.nombre, Usuario.paterno)
            .where(Usuario.id_usuario.in_(sub))
            .order_by(Usuario.alias, Usuario.nombre)
        ).all()
    return (
        [["todos", "Todos los actores"], ["sistema", "Sistema (sin usuario)"]]
        + [[str(uid), _nombre_actor(al, no, pa)] for uid, al, no, pa in filas]
    )


def bitacora(tabla=None, operacion=None, actor=None, dias=7, limite=LIMITE_INICIAL) -> list[dict]:
    stmt = select(
        Auditoria.id_auditoria, Auditoria.fec_registro, Auditoria.operacion,
        Auditoria.tabla, Auditoria.id_registro, Auditoria.id_usuario,
        Auditoria.campos, Auditoria.datos_antes, Auditoria.datos_despues,
        Usuario.alias, Usuario.nombre, Usuario.paterno,
    ).join(Usuario, Usuario.id_usuario == Auditoria.id_usuario, isouter=True)
    stmt = _filtrar(stmt, tabla=tabla, operacion=operacion, actor=actor, dias=dias)
    stmt = stmt.order_by(
        Auditoria.fec_registro.desc(), Auditoria.id_auditoria.desc()
    ).limit(min(limite, LIMITE_MAXIMO))

    with Session(engine) as s:
        filas = s.exec(stmt).all()

    salida = []
    for (aid, fec, op, tab, idreg, idus, campos, antes, despues,
         alias, nombre, paterno) in filas:
        fec = _aware(fec)
        salida.append({
            "id": str(aid),
            "fecha": fec.strftime("%d/%m/%y %H:%M:%S") if fec else "—",
            "hace": _hace(fec),
            "operacion": op,
            "tabla": tab,
            "registro": f"#{idreg}" if idreg is not None else "—",
            "actor": "Sistema" if idus is None else _nombre_actor(alias, nombre, paterno),
            "es_sistema": idus is None,
            "descripcion": _descriptor(tab, antes, despues, idreg),
            "cambios": _resumen_cambios(campos),
        })
    return salida


def contar_bitacora(tabla=None, operacion=None, actor=None, dias=7) -> int:
    stmt = select(func.count(Auditoria.id_auditoria))
    stmt = _filtrar(stmt, tabla=tabla, operacion=operacion, actor=actor, dias=dias)
    with Session(engine) as s:
        return s.exec(stmt).one() or 0


def detalle_auditoria(id_auditoria) -> dict:
    """Todo el cambio, campo por campo. Valores ya en str para la UI."""
    vacio = {
        "hay": False, "fecha": "", "actor": "", "tabla": "",
        "operacion": "", "descripcion": "", "cambios": [],
    }
    if id_auditoria in (None, ""):
        return vacio

    with Session(engine) as s:
        fila = s.exec(
            select(
                Auditoria.id_auditoria, Auditoria.fec_registro, Auditoria.operacion,
                Auditoria.tabla, Auditoria.id_registro, Auditoria.id_usuario,
                Auditoria.campos, Auditoria.datos_antes, Auditoria.datos_despues,
                Usuario.alias, Usuario.nombre, Usuario.paterno,
            )
            .join(Usuario, Usuario.id_usuario == Auditoria.id_usuario, isouter=True)
            .where(Auditoria.id_auditoria == int(id_auditoria))
        ).first()

    if not fila:
        return vacio

    (aid, fec, op, tab, idreg, idus, campos, antes, despues,
     alias, nombre, paterno) = fila
    fec = _aware(fec)
    antes = antes or {}
    despues = despues or {}

    if op == "UPDATE":
        claves = list(campos or [])
    elif op == "INSERT":
        claves = sorted(despues.keys())
    else:
        claves = sorted(antes.keys())

    cambios = []
    for c in claves:
        if c in CAMPOS_OCULTOS:
            cambios.append({"campo": c, "antes": "(oculto)", "despues": "(oculto)"})
            continue
        cambios.append({
            "campo": c,
            "antes": "—" if op == "INSERT" else _fmt_valor(antes.get(c)),
            "despues": "—" if op == "DELETE" else _fmt_valor(despues.get(c)),
        })

    return {
        "hay": True,
        "fecha": fec.strftime("%d/%m/%y %H:%M:%S") if fec else "—",
        "actor": "Sistema" if idus is None else _nombre_actor(alias, nombre, paterno),
        "tabla": tab,
        "operacion": op,
        "descripcion": _descriptor(tab, antes, despues, idreg),
        "cambios": cambios,
    }
