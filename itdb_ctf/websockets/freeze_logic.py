"""Estado de "freeze" del scoreboard, guardado **solo en Redis**.

- `freeze:flag:{id}`  -> "1" cuando el evento está congelado (ausente si no).
- `freeze:fecha:{id}` -> ISO-8601 UTC del instante en que se hizo click a "Congelar".

El freeze **solo afecta la vista de `user` (estudiantes)**. El staff siempre ve en
vivo (pasan `corte=None`).

Todas las funciones son **a prueba de fallo**: cualquier problema con Redis →
`esta_congelado()` = `False`, `corte_freeze()` = `None` (fail-open: preferimos
mostrar de más antes que romper una vista).

Riesgo asumido: si Redis se reinicia durante un evento, el freeze se pierde.
"""

from datetime import datetime, timezone

from itdb_ctf.websockets import canales, redis_cliente

_TTL = 60 * 60 * 24 * 7  # 7 días


def _k_flag(id_evento) -> str:
    return f"itdb:frz:flag:{int(id_evento)}"


def _k_fecha(id_evento) -> str:
    return f"itdb:frz:fecha:{int(id_evento)}"


def congelar(id_evento) -> datetime | None:
    cli = redis_cliente.get_sync()
    if cli is None:
        return None
    ahora = datetime.now(timezone.utc)
    try:
        cli.set(_k_flag(id_evento), "1", ex=_TTL)
        cli.set(_k_fecha(id_evento), ahora.isoformat(), ex=_TTL)
    except Exception:
        redis_cliente.marcar_caido()
        return None
    canales.publicar_freeze(int(id_evento))
    return ahora


def descongelar(id_evento) -> bool:
    cli = redis_cliente.get_sync()
    if cli is None:
        return False
    try:
        cli.delete(_k_flag(id_evento), _k_fecha(id_evento))
    except Exception:
        redis_cliente.marcar_caido()
        return False
    canales.publicar_freeze(int(id_evento))
    return True


def esta_congelado(id_evento) -> bool:
    cli = redis_cliente.get_sync()
    if cli is None:
        return False
    try:
        val = cli.get(_k_flag(id_evento))
        if isinstance(val, bytes):
            val = val.decode("utf-8", "ignore")
        return str(val).strip() == "1"
    except Exception:
        redis_cliente.marcar_caido()
        return False


def corte_freeze(id_evento) -> datetime | None:
    """Instante hasta el que mostrar el scoreboard, o `None` si no está congelado."""
    if not esta_congelado(id_evento):
        return None
    cli = redis_cliente.get_sync()
    if cli is None:
        return None
    try:
        iso = cli.get(_k_fecha(id_evento))
        if isinstance(iso, bytes):
            iso = iso.decode("utf-8", "ignore")
        if not iso:
            return None
        dt = datetime.fromisoformat(str(iso))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        return None
