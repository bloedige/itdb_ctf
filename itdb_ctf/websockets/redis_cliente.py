"""Conexiones Redis compartidas con **fail-fast**.

Problema que resuelve: el cliente sync de redis-py hace `connect()` bloqueante en
la primera operación. Si Redis está caído, cada `.get()` / `.publish()` bloquea el
*event loop* de asyncio durante el `socket_connect_timeout`. Con ~5 operaciones por
refresco de scoreboard eso congelaba el backend entero.

Solución: `hay_redis()` prueba **una** vez con timeout de 0.15 s y **memoiza** el
resultado (15 s si está caído, 10 s si funciona). `get_sync()` / `get_async()`
devuelven `None` **al instante** mientras Redis esté marcado como caído, así todas
las funciones de `canales` / `cache` / `freeze_logic` son no-ops inmediatos.
"""

import os
import time

import redis
from redis.asyncio import Redis as RedisAsync
from redis.backoff import NoBackoff
from redis.retry import Retry

REDIS_URL = os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/0")
# `localhost` en Windows intenta ::1 (IPv6) y recién después 127.0.0.1 → duplica
# el tiempo del sondeo cuando Redis está apagado. Forzamos IPv4.
REDIS_URL = REDIS_URL.replace("://localhost:", "://127.0.0.1:")

_PROBE_TIMEOUT = 0.1     # segundos para conectar/PING de sondeo
_COOLDOWN_DOWN = 20.0    # si está caído, no re-sondear por 20 s
_COOLDOWN_UP = 15.0      # si funciona, revalidar cada 15 s
_SIN_REINTENTOS = Retry(NoBackoff(), 0)   # redis-py 7 reintenta con backoff por defecto

_sync: "redis.Redis | None" = None
_async: "RedisAsync | None" = None
_estado: "bool | None" = None   # None = sin sondear todavía
_ultimo_sondeo: float = 0.0


def _cliente_sync() -> "redis.Redis":
    """Objeto cliente (conexión perezosa). No garantiza que Redis responda."""
    global _sync
    if _sync is None:
        _sync = redis.Redis.from_url(
            REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=_PROBE_TIMEOUT,
            socket_timeout=1.0,             # ops normales: 1 s de tope
            retry=_SIN_REINTENTOS,
            retry_on_timeout=False,
            retry_on_error=[],
        )
    return _sync


def hay_redis() -> bool:
    """`True` si Redis respondió a un PING reciente. Memoizado (ver cooldowns)."""
    global _estado, _ultimo_sondeo
    ahora = time.monotonic()
    cooldown = _COOLDOWN_DOWN if _estado is False else _COOLDOWN_UP
    if _estado is not None and (ahora - _ultimo_sondeo) < cooldown:
        return _estado
    _ultimo_sondeo = ahora
    try:
        _estado = bool(_cliente_sync().ping())
    except Exception:
        _estado = False
    return _estado


def get_sync() -> "redis.Redis | None":
    """Cliente sync, o `None` inmediato si Redis está (marcado como) caído."""
    return _cliente_sync() if hay_redis() else None


def get_async() -> "RedisAsync | None":
    """Cliente async para pub/sub, o `None` si Redis está caído."""
    global _async
    if not hay_redis():
        return None
    if _async is None:
        try:
            _async = RedisAsync.from_url(
                REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=1,
                socket_timeout=None,          # las suscripciones bloquean a propósito
                health_check_interval=30,
                retry=_SIN_REINTENTOS,
                retry_on_timeout=False,
                retry_on_error=[],
            )
        except Exception:
            return None
    return _async


def marcar_caido() -> None:
    """Fuerza el estado a 'caído' (lo llama un consumidor que vio fallar una op)."""
    global _estado, _ultimo_sondeo
    _estado = False
    _ultimo_sondeo = time.monotonic()
