"""Canales pub/sub y publicadores.

Los publicadores son **síncronos** (se llaman desde funciones `*_logic`) y
**tolerantes a fallo**: si Redis no responde, no hacen nada y la mutación de BD
igual se completa. El payload es mínimo ("algo cambió en el canal X"); el
suscriptor solo re-ejecuta su handler de recarga.
"""

from itdb_ctf.websockets import cache, redis_cliente

# --- nombres de canal ---

def ch_scoreboard(id_evento: int) -> str:
    return f"itdb:sb:{id_evento}"


def ch_evento(id_evento: int) -> str:
    """retos / pistas / asociaciones / descripción de un evento."""
    return f"itdb:ev:{id_evento}"


def ch_inscripcion(id_evento: int) -> str:
    return f"itdb:insc:{id_evento}"


def ch_freeze(id_evento: int) -> str:
    return f"itdb:frz:{id_evento}"


# alta / baja / edición de eventos → afecta la lista de /eventos y /admin/eventos
CH_EVENTOS = "itdb:eventos"
# cualquier cambio de reto / pista / asociación → listas de admin sin filtro por evento
CH_RETOS = "itdb:retos"
# cualquier escritura auditada (la publica utils/auditoria.py tras el commit)
CH_AUDITORIA = "itdb:auditoria"


# --- publicadores (sync, degradación silenciosa) ---

def _pub(canal: str, msg: str = "1") -> None:
    cli = redis_cliente.get_sync()
    if cli is None:
        return
    try:
        cli.publish(canal, msg)
    except Exception:
        redis_cliente.marcar_caido()


def publicar_scoreboard(id_evento: int) -> None:
    """Aceptación de flag / compra de pista / cambio de inscripción / freeze."""
    cache.invalidar_scoreboard(id_evento)
    _pub(ch_scoreboard(id_evento))


def publicar_freeze(id_evento: int) -> None:
    _pub(ch_freeze(id_evento))
    publicar_scoreboard(id_evento)


def publicar_evento(id_evento: int) -> None:
    _pub(ch_evento(id_evento))


def publicar_inscripcion(id_evento: int) -> None:
    _pub(ch_inscripcion(id_evento))
    publicar_scoreboard(id_evento)


def publicar_lista_eventos() -> None:
    _pub(CH_EVENTOS)


def publicar_retos() -> None:
    _pub(CH_RETOS)


def publicar_reto_en_eventos(id_eventos) -> None:
    """Un reto/pista cambió: avisa a cada evento afectado + a las listas de admin."""
    for id_ev in id_eventos:
        _pub(ch_evento(id_ev))
    _pub(CH_RETOS)


def publicar_auditoria() -> None:
    """Se acaba de confirmar una escritura sobre una tabla con trigger."""
    _pub(CH_AUDITORIA)
