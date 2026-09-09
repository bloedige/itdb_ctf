"""Helper del patrón "background task que se suscribe a Redis y recarga el state".

Es una **corrutina** (no un generador): igual que el viejo `auto_refresh`, hace
todo el bucle internamente y muta el state dentro de `async with state:`. No
devuelve/`yield`-ea eventos.

Uso desde un state de Reflex::

    @rx.event(background=True)
    async def escuchar_scoreboard(self):
        await suscriptor.escuchar(
            self,
            id_getter=lambda s: s._id_evento(),
            canales_getter=lambda id_ev: [canales.ch_scoreboard(id_ev),
                                          canales.ch_freeze(id_ev)],
            recargar=lambda s: s.refresh_ranking(),
        )

Robustez:
- El `id_evento` se **re-resuelve en cada vuelta** (el router puede no estar listo
  cuando arranca el `on_mount`) y si cambió se re-suscribe.
- Si Redis no está / se cae → polling cada `polling_seg`, reintentando pub/sub más
  tarde (cuando `redis_cliente` vuelva a marcarlo como disponible).
- Corta cuando `state.streaming` es `False` o `state.tick_token` cambió.
"""

import asyncio

import reflex as rx

from itdb_ctf.websockets import redis_cliente

_FALLBACK_SEG = 10   # recarga "de seguridad" aunque no llegue ningún mensaje
_POLLING_SEG = 5     # cadencia cuando no hay Redis


class SuscriptorMixin(rx.State, mixin=True):
    """Vars que `escuchar()` necesita en el state. Cada state que la use define
    su propio handler `@rx.event(background=True) async def escuchar_X` + un
    `parar_X` que hace `self.streaming = False`."""

    streaming: bool = False
    tick_token: int = 0


def _corta(state, token) -> bool:
    return (not state.streaming) or (state.tick_token != token)


def _recargar_seguro(state, recargar) -> None:
    try:
        recargar(state)
    except Exception:
        pass


async def _cerrar_pubsub(pubsub) -> None:
    try:
        await pubsub.unsubscribe()
    except Exception:
        pass
    for nombre in ("aclose", "close"):
        cerrar = getattr(pubsub, nombre, None)
        if cerrar is None:
            continue
        try:
            res = cerrar()
            if asyncio.iscoroutine(res):
                await res
            return
        except Exception:
            return


async def escuchar(state, clave_getter, canales_getter, recargar,
                   *, fallback_seg: int = _FALLBACK_SEG, polling_seg: int = _POLLING_SEG):
    """`clave_getter(state)` -> valor hashable que identifica a qué se está
    suscrito (o `None` = nada → polling). `canales_getter(state)` -> lista de
    canales. Si la clave cambia (p. ej. el admin selecciona otro evento) se
    re-suscribe."""
    async with state:
        state.tick_token = (state.tick_token or 0) + 1
        token = state.tick_token
        state.streaming = True

    while True:
        # (re)resolver clave + canales + recarga de esta vuelta
        async with state:
            if _corta(state, token):
                return
            clave = clave_getter(state)
            chans = list(canales_getter(state)) if clave is not None else []
            _recargar_seguro(state, recargar)

        r = redis_cliente.get_async()
        if r is None or not chans:
            await asyncio.sleep(polling_seg)
            continue

        # --- pub/sub ---
        try:
            pubsub = r.pubsub()
            await pubsub.subscribe(*chans)
        except Exception:
            redis_cliente.marcar_caido()
            await asyncio.sleep(polling_seg)
            continue

        try:
            while True:
                try:
                    await pubsub.get_message(ignore_subscribe_messages=True, timeout=fallback_seg)
                except Exception:
                    redis_cliente.marcar_caido()
                    break  # -> reintenta desde el principio (polling / re-suscribe)
                async with state:
                    if _corta(state, token):
                        return
                    if clave_getter(state) != clave:
                        break  # cambió el objetivo -> re-suscribir
                    _recargar_seguro(state, recargar)
        finally:
            await _cerrar_pubsub(pubsub)
