"""Rate limiting (tope de intentos por ventana de tiempo).

**Login** (`auth/local_auth_state.py`): frena la fuerza bruta y el coste de bcrypt
sobre el backend mono-proceso. **Solo cuenta intentos FALLIDOS**; un login exitoso
limpia los contadores. Así una red institucional / NAT (muchos alumnos detrás de
una sola IP pública) no se auto-bloquea mientras escriban bien la contraseña.

**Envío de flag** (`core/envio_logic.py`): anti-spam de la tabla `Resuelve` y
defensa en profundidad contra adivinar flags. Cuenta todos los intentos.

Implementación: contador de **ventana fija en Redis** (`INCR` + `EXPIRE NX` en un
pipeline transaccional → atómico, y el TTL se fija una sola vez, así el bloqueo
nunca dura más que la ventana). El contador se limpia solo; no hay tabla ni
migración.

Sin Redis:
- **login** usa un **respaldo en memoria** del propio proceso (el backend es
  mono-proceso, así que ese diccionario ve *todos* los intentos). Se pierde al
  reiniciar el backend.
- **flag** simplemente permite el intento (fail-open).

API pública:
- `login_bloqueado(ip, email) -> (bloqueado: bool, segundos_restantes: int)` — solo lee.
- `registrar_fallo_login(ip, email)` — llamar tras credenciales inválidas.
- `limpiar_login(ip, email)` — llamar tras un login exitoso.
- `permitir_flag(id_usuario, id_reto) -> (permitido: bool, segundos_restantes: int)`.
"""

import time
from collections import deque

from itdb_ctf.websockets.redis_cliente import get_sync, marcar_caido

# --- Límites: (cantidad_maxima, ventana_en_segundos) ---
# Para login la cantidad es de intentos FALLIDOS; para flag, de intentos totales.
LOGIN_CUENTA = (8, 600)    # 8 logins fallidos por cuenta cada 10 min
LOGIN_IP = (50, 600)       # 50 logins fallidos por IP cada 10 min (red de seguridad)
FLAG = (15, 60)            # 15 envíos por (usuario, reto) cada minuto

_PREFIJO = "itdb:rl:"


def _clave_login_ip(ip: str) -> str:
    return f"{_PREFIJO}login:ip:{ip}"


def _clave_login_cuenta(email: str) -> str:
    return f"{_PREFIJO}login:acc:{email.strip().lower()}"


def _clave_flag(id_usuario: int, id_reto: int) -> str:
    return f"{_PREFIJO}flag:{id_usuario}:{id_reto}"


# ---------------------------------------------------------------------------
# Capa Redis
# ---------------------------------------------------------------------------
def _redis_incr(clave: str, ventana: int) -> "int | None":
    """Suma 1 al contador y devuelve el total. `None` si Redis no está disponible."""
    cli = get_sync()
    if cli is None:
        return None
    try:
        pipe = cli.pipeline(transaction=True)
        pipe.incr(clave)
        pipe.expire(clave, ventana, nx=True)   # fija el TTL solo la 1ª vez
        n, _ = pipe.execute()
        return int(n)
    except Exception:
        marcar_caido()
        return None


def _redis_peek(clave: str) -> "tuple[int, int] | None":
    """`(conteo, segundos_restantes)` sin incrementar. `None` si no hay Redis."""
    cli = get_sync()
    if cli is None:
        return None
    try:
        pipe = cli.pipeline(transaction=True)
        pipe.get(clave)
        pipe.ttl(clave)
        v, ttl = pipe.execute()
        return (int(v) if v else 0), max(int(ttl), 1)
    except Exception:
        marcar_caido()
        return None


def _redis_del(*claves: str) -> None:
    cli = get_sync()
    if cli is None:
        return
    try:
        cli.delete(*claves)
    except Exception:
        marcar_caido()


# ---------------------------------------------------------------------------
# Respaldo en memoria (solo login)
# ---------------------------------------------------------------------------
_memoria: "dict[str, deque]" = {}
_MAX_CLAVES = 10_000   # poda defensiva para que el dict no crezca sin límite


def _memoria_podar(clave: str, ahora: float, ventana: int) -> deque:
    q = _memoria.get(clave)
    if q is None:
        if len(_memoria) > _MAX_CLAVES:
            _memoria.clear()
        q = _memoria[clave] = deque()
    while q and (ahora - q[0]) >= ventana:
        q.popleft()
    return q


def _memoria_peek(clave: str, ventana: int) -> "tuple[int, int]":
    ahora = time.monotonic()
    q = _memoria_podar(clave, ahora, ventana)
    restante = max(int(ventana - (ahora - q[0])), 1) if q else 1
    return len(q), restante


def _memoria_incr(clave: str, ventana: int) -> int:
    ahora = time.monotonic()
    q = _memoria_podar(clave, ahora, ventana)
    q.append(ahora)
    return len(q)


def _memoria_del(*claves: str) -> None:
    for c in claves:
        _memoria.pop(c, None)


# ---------------------------------------------------------------------------
# API pública — LOGIN (cuenta solo intentos fallidos)
# ---------------------------------------------------------------------------
_LOGIN_CLAVES = (
    (_clave_login_cuenta, LOGIN_CUENTA),
    (_clave_login_ip, LOGIN_IP),
)


def login_bloqueado(ip: str, email: str) -> "tuple[bool, int]":
    """`(True, seg)` si la IP o la cuenta superaron su tope de fallos. Solo lee."""
    for hace_clave, (limite, ventana) in _LOGIN_CLAVES:
        clave = hace_clave(email if hace_clave is _clave_login_cuenta else ip)
        r = _redis_peek(clave)
        if r is None:
            r = _memoria_peek(clave, ventana)
        n, restante = r
        if n >= limite:
            return True, restante
    return False, 0


def registrar_fallo_login(ip: str, email: str) -> None:
    """Suma 1 a los contadores de IP y cuenta (tras credenciales inválidas)."""
    for hace_clave, (_, ventana) in _LOGIN_CLAVES:
        clave = hace_clave(email if hace_clave is _clave_login_cuenta else ip)
        if _redis_incr(clave, ventana) is None:
            _memoria_incr(clave, ventana)


def limpiar_login(ip: str, email: str) -> None:
    """Borra los contadores de login tras un ingreso exitoso."""
    claves = (_clave_login_cuenta(email), _clave_login_ip(ip))
    _memoria_del(*claves)
    _redis_del(*claves)


# ---------------------------------------------------------------------------
# API pública — FLAG (cuenta todos los intentos)
# ---------------------------------------------------------------------------
def permitir_flag(id_usuario: int, id_reto: int) -> "tuple[bool, int]":
    clave = _clave_flag(id_usuario, id_reto)
    limite, ventana = FLAG
    n = _redis_incr(clave, ventana)
    if n is None:
        return True, 0   # fail-open
    if n > limite:
        r = _redis_peek(clave)
        return False, (r[1] if r else ventana)
    return True, 0
