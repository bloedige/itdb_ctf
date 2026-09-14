"""Actor de auditoria: lleva el id del usuario que ejecuta la escritura hasta
los triggers de Postgres (ver scripts/auditoria_up.sql).

El trigger lee `current_setting('app.id_usuario', true)`. Aqui ese GUC se fija
con `set_config(..., true)` == SET LOCAL: vive solo dentro de la transaccion
del flush, asi que nunca se filtra a otra transaccion ni viaja con la conexion
de vuelta al pool.

El enganche es `Session.before_flush`, que solo dispara cuando la sesion tiene
cambios pendientes (new/dirty/deleted) => las lecturas no ejecutan nada extra.
Ese mismo hook marca la sesion cuando toca una tabla auditada, y `after_commit`
publica en el canal de auditoria para que los paneles abiertos se refresquen.
"""
import logging
from contextvars import ContextVar

import reflex as rx
from sqlalchemy import event, text
from sqlmodel import Session

from itdb_ctf.db import engine
from itdb_ctf.websockets import canales

# las 13 tablas con trigger (scripts/auditoria_up.sql). `resuelve` y `compra`
# quedan fuera a proposito: son las de alto volumen.
TABLAS_AUDITADAS = (
    "rol", "categoria", "dificultad", "modo_puntaje", "modalidad",
    "estado_inscripcion", "metodo_auth", "usuario", "evento",
    "reto", "pista", "participa", "contiene",
)
_AUDITADAS = frozenset(TABLAS_AUDITADAS)

_actor: ContextVar[int | None] = ContextVar("actor_auditoria", default=None)
_log = logging.getLogger(__name__)


def set_actor(id_usuario: int | None) -> None:
    """Fija (o limpia con None) el usuario responsable de las escrituras."""
    _actor.set(id_usuario)


def _toca_auditadas(session: Session) -> bool:
    for obj in list(session.new) + list(session.dirty) + list(session.deleted):
        if getattr(obj, "__tablename__", None) in _AUDITADAS:
            return True
    return False


@event.listens_for(Session, "before_flush")
def _inyectar_actor(session: Session, flush_context, instances) -> None:
    try:
        # solo nuestras sesiones; ignora cualquier otra que use el mismo evento
        if session.get_bind() is not engine:
            return
        if _toca_auditadas(session):
            session.info["_auditado"] = True
    except Exception:
        _log.warning("auditoria: no se pudo inspeccionar el flush", exc_info=True)
        return

    v = _actor.get()
    if v is None:
        # Escritura de sistema (seed, scripts): el trigger registra id_usuario NULL.
        return
    try:
        session.execute(
            text("SELECT set_config('app.id_usuario', :v, true)"),
            {"v": str(int(v))},
        )
    except Exception:
        _log.warning("auditoria: no se pudo fijar el actor", exc_info=True)


@event.listens_for(Session, "after_commit")
def _publicar_auditoria(session: Session) -> None:
    """Ya esta confirmada la escritura: avisa a los paneles abiertos."""
    if not session.info.pop("_auditado", False):
        return
    try:
        canales.publicar_auditoria()
    except Exception:
        _log.warning("auditoria: no se pudo publicar el cambio", exc_info=True)


class ActorMiddleware(rx.Middleware):
    """Marca el actor antes de cada evento y lo limpia al terminar."""

    async def preprocess(self, app, state, event):
        from itdb_ctf.auth.auth_state import AuthState

        try:
            set_actor((await state.get_state(AuthState)).id_usuario)
        except Exception:
            # Nunca tumbar un evento por la auditoria; peor caso, actor NULL.
            set_actor(None)
            _log.warning("auditoria: no se pudo resolver el actor", exc_info=True)
        return None

    async def postprocess(self, app, state, event, update):
        set_actor(None)
        return update
