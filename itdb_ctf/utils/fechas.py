from datetime import datetime
from zoneinfo import ZoneInfo

# Zona horaria de la institución. Explícita para no depender del TZ del
# contenedor (Docker corre en UTC) ni del de PostgreSQL.
ZONA_LOCAL = ZoneInfo("America/La_Paz")

def desde_input(valor: str) -> datetime | None:
    """'YYYY-MM-DDTHH:MM' del input datetime-local -> datetime aware en hora de La Paz."""
    if not valor:
        return None
    return datetime.fromisoformat(valor).replace(tzinfo=ZONA_LOCAL)

def a_local(dt: datetime | None) -> datetime | None:
    """Convierte un datetime (aware o naive UTC) a hora de La Paz."""
    if dt is None:
        return None
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt.astimezone(ZONA_LOCAL)
