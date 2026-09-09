"""Cache del scoreboard en Redis (cliente síncrono).

Guarda `(ranking, opcion_evolucion)` ya computado por `(id_evento, corte)`.
TTL corto como red de seguridad; la invalidación real la dispara
`canales.publicar_scoreboard()`.

Si Redis no está: `obtener()` -> `None`, `guardar()` / `invalidar()` -> no-op
(el scoreboard se recomputa siempre, como antes).
"""

import json
from datetime import datetime

from itdb_ctf.websockets import redis_cliente

_TTL_DEFECTO = 20  # segundos


def _sufijo_corte(corte: datetime | None) -> str:
    return "live" if corte is None else corte.isoformat()


def _key(id_evento: int, corte: datetime | None) -> str:
    return f"itdb:cache:sb:{id_evento}:{_sufijo_corte(corte)}"


def _patron(id_evento: int) -> str:
    return f"itdb:cache:sb:{id_evento}:*"


def _default(o):
    if isinstance(o, datetime):
        return o.isoformat()
    raise TypeError(f"no serializable: {type(o)}")


def obtener(id_evento: int, corte: datetime | None) -> dict | None:
    cli = redis_cliente.get_sync()
    if cli is None:
        return None
    try:
        crudo = cli.get(_key(id_evento, corte))
    except Exception:
        redis_cliente.marcar_caido()
        return None
    if not crudo:
        return None
    try:
        return json.loads(crudo)
    except Exception:
        return None


def guardar(id_evento: int, corte: datetime | None, ranking: list[dict],
            opcion: dict, ttl: int = _TTL_DEFECTO) -> None:
    cli = redis_cliente.get_sync()
    if cli is None:
        return
    try:
        payload = json.dumps({"ranking": ranking, "opcion": opcion}, default=_default)
        cli.setex(_key(id_evento, corte), ttl, payload)
    except Exception:
        redis_cliente.marcar_caido()


def invalidar_scoreboard(id_evento: int) -> None:
    """Borra todas las variantes de cache (live + cada corte) del evento."""
    cli = redis_cliente.get_sync()
    if cli is None:
        return
    try:
        keys = list(cli.scan_iter(match=_patron(id_evento), count=100))
        if keys:
            cli.delete(*keys)
    except Exception:
        redis_cliente.marcar_caido()
