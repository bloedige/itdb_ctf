from datetime import datetime, timezone

from sqlmodel import Session, select
from itdb_ctf.db import engine
from itdb_ctf.models import (
    Resuelve, Usuario, Contiene, Compra, Evento, Modalidad, Participa, EstadoInscripcion,
)
from itdb_ctf.core.puntaje_logic import puntaje_total_usuario
from itdb_ctf.websockets import cache

# Paleta para la curva de evolución (top 10). Los 5 primeros == scoreboard_view.COLORES.
PALETA = [
    "#00ffd0", "#ff7300", "#9dff00", "#8400ff", "#ff006a",
    "#00b8ff", "#ffd000", "#ff5b5b", "#b48cff", "#37ffb0",
]
VERDE = "#00ffc3"   # curva individual (perfil), igual que el gráfico recharts anterior

# Icono bandera (asta + banderín) para la leyenda. ECharts lo rellena con el color de la serie.
FLAG_PATH = "path://M4 2 L6 2 L6 22 L4 22 Z M6 3 L20 8 L6 13 Z"


def scoreboard(id_evento: int, corte: datetime | None = None) -> list[dict]:
    """Ranking del evento. `corte` (freeze): solo cuenta aciertos con
    `fec_envio <= corte` y recalcula puntajes a ese instante."""
    with Session(engine) as s:
        q_filas = (select(Resuelve.id_usuario, Usuario.alias, Usuario.nombre)
                   .join(Usuario, Resuelve.id_usuario == Usuario.id_usuario)
                   .where(Resuelve.id_evento == id_evento, Resuelve.flag_correcta == True))  # noqa: E712
        if corte is not None:
            q_filas = q_filas.where(Resuelve.fec_envio <= corte)
        filas = s.exec(q_filas).all()
        # excluir descalificados del evento
        descal = set(s.exec(
            select(Participa.id_usuario)
            .join(EstadoInscripcion,
                  Participa.id_estado_inscripcion == EstadoInscripcion.id_estado_inscripcion)
            .where(Participa.id_evento == id_evento,
                   EstadoInscripcion.etiqueta == "descalificado")
        ).all())
        vistos = {}
        for id_u, ali, nom in filas:
            if id_u in descal or id_u in vistos:
                continue
            vistos[id_u] = ali if ali else nom
        ultimas = {}
        for id_u in vistos:
            q_ult = (select(Resuelve.fec_envio).where(
                Resuelve.id_usuario == id_u,
                Resuelve.id_evento == id_evento,
                Resuelve.flag_correcta == True)  # noqa: E712
                .order_by(Resuelve.fec_envio.desc()))
            if corte is not None:
                q_ult = q_ult.where(Resuelve.fec_envio <= corte)
            ultimas[id_u] = s.exec(q_ult).first()
        ranking = [
            {
                "id_usuario": id_usuario,
                "nombre": nombre,
                "puntaje": puntaje_total_usuario(s, id_usuario, id_evento, corte),
                "ultima": ultimas[id_usuario],
            }
            for id_usuario, nombre in vistos.items()
        ]
        ranking.sort(key=lambda x: (-x['puntaje'], x['ultima']))
        for i, fila in enumerate(ranking, start=1):
            fila['posicion'] = i
        return ranking


# ------------------------------------------------------------------ evolución (ECharts)

def _modo_evento(s: Session, ev: Evento) -> str:
    """abierto | futuro | activo | concluido."""
    modalidad = s.get(Modalidad, ev.id_modalidad)
    if (modalidad and modalidad.etiqueta == "abierto") or (
        ev.fec_inicio is None and ev.fec_fin is None
    ):
        return "abierto"
    ahora = datetime.now(timezone.utc)
    if ev.fec_inicio is not None and ahora < ev.fec_inicio:
        return "futuro"
    if ev.fec_fin is not None and ahora > ev.fec_fin:
        return "concluido"
    return "activo"


def _timeline_usuario(s: Session, id_usuario: int, id_evento: int, valor_reto: dict,
                      corte: datetime | None = None) -> list[tuple]:
    """[(fec, acumulado_con_piso_0)] ordenado, solo aciertos + compras del usuario."""
    q_solves = select(Resuelve.fec_envio, Resuelve.id_reto).where(
        Resuelve.id_usuario == id_usuario,
        Resuelve.id_evento == id_evento,
        Resuelve.flag_correcta == True,  # noqa: E712
    )
    q_compras = select(Compra.fec_compra, Compra.puntos_usados).where(
        Compra.id_usuario == id_usuario,
        Compra.id_evento == id_evento,
    )
    if corte is not None:
        q_solves = q_solves.where(Resuelve.fec_envio <= corte)
        q_compras = q_compras.where(Compra.fec_compra <= corte)
    solves = s.exec(q_solves).all()
    compras = s.exec(q_compras).all()
    eventos = [(f, valor_reto.get(r, 0)) for f, r in solves if f is not None]
    eventos += [(f, -p) for f, p in compras if f is not None]
    eventos.sort(key=lambda e: e[0])
    acum, salida = 0, []
    for fec, delta in eventos:
        acum = max(acum + delta, 0)
        salida.append((fec, acum))
    return salida


def _construir_opcion(modo: str, ev: Evento, entradas: list[tuple[str, list]],
                      *, con_leyenda: bool, colores: list,
                      corte: datetime | None = None) -> dict:
    """`option` de ECharts a partir de `[(nombre, [(fec, acum), ...]), ...]`.

    Eje X según `modo`: abierto -> fecha/hora real; activo/concluido -> horas
    desde `fec_inicio`. Con `corte` (freeze) el eje termina en ese instante.
    Devuelve `{}` si no hay ninguna actividad.
    """
    if not any(tl for _, tl in entradas):
        return {}

    tiempo_real = modo == "abierto"
    tope = corte if corte is not None else datetime.now(timezone.utc)

    if tiempo_real:
        fechas = [tl[0][0] for _, tl in entradas if tl]
        x_min = int(min(fechas).timestamp() * 1000)
        x_max = int(tope.timestamp() * 1000)

        def to_x(fec):
            return int(fec.timestamp() * 1000)
    else:
        t0 = ev.fec_inicio
        if t0 is None:
            t0 = min(tl[0][0] for _, tl in entradas if tl)
        fin = corte if corte is not None else (ev.fec_fin if ev.fec_fin else tope)
        x_min = 0.0
        x_max = round(max((fin - t0).total_seconds() / 3600, 0.1), 2)

        def to_x(fec):
            return round((fec - t0).total_seconds() / 3600, 4)

    series, leyenda = [], []
    for nombre, tl in entradas:
        leyenda.append(nombre)
        # extremos sin dot; los puntos reales -> dot en el momento exacto en que
        # el puntaje cambió (subió por acierto, bajó por compra de pista)
        puntos = [{"value": [x_min, 0], "symbol": "none"}]
        for fec, acum in tl:
            puntos.append([to_x(fec), acum])
        puntos.append({"value": [x_max, tl[-1][1] if tl else 0], "symbol": "none"})
        series.append({
            "name": nombre,
            "type": "line",
            "smooth": True,
            "showSymbol": True,
            "symbol": "circle",
            "symbolSize": 6,
            "emphasis": {"focus": "series"},
            "lineStyle": {"width": 2},
            "data": puntos,
        })

    x_axis = {
        "type": "time" if tiempo_real else "value",
        "min": x_min,
        "max": x_max,
        "axisLabel": {"color": "#9fb3c8", "hideOverlap": True},
        "axisLine": {"lineStyle": {"color": "#1e3a5f"}},
        "splitLine": {"show": True, "lineStyle": {"color": "#132a47", "type": "dashed"}},
    }
    if not tiempo_real:
        x_axis["axisLabel"]["formatter"] = "{value} h"
        x_axis["name"] = "Horas desde el inicio"
        x_axis["nameLocation"] = "middle"
        x_axis["nameGap"] = 34
        x_axis["nameTextStyle"] = {"color": "#9fb3c8"}

    legend = (
        {
            "type": "scroll",
            "bottom": 6,
            "icon": FLAG_PATH,
            "itemWidth": 16,
            "itemHeight": 16,
            "textStyle": {"color": "#9fb3c8"},
            "inactiveColor": "#3d5a7f",
            "pageIconColor": "#9fb3c8",
            "pageTextStyle": {"color": "#9fb3c8"},
            "data": leyenda,
        }
        if con_leyenda
        else {"show": False}
    )

    return {
        "backgroundColor": "transparent",
        "color": colores,
        "grid": {
            "left": 8, "right": 22, "top": 24,
            "bottom": 64 if con_leyenda else 40,
            "containLabel": True,
        },
        "tooltip": {
            "trigger": "item",
            "confine": True,
            "backgroundColor": "#0b1f3aee",
            "borderColor": "#1e3a5f",
            "textStyle": {"color": "#e6f1ff"},
            "formatter": "{a}<br/>{c1} pts",   # el componente lo reemplaza por una fn JS
        },
        "legend": legend,
        "xAxis": x_axis,
        "yAxis": {
            "type": "value",
            "min": 0,
            "axisLabel": {"color": "#9fb3c8"},
            "splitLine": {"lineStyle": {"color": "#132a47", "type": "dashed"}},
        },
        "series": series,
        "animationDuration": 300,
    }


def opcion_evolucion(id_evento: int, top: int = 10, corte: datetime | None = None) -> dict:
    """`option` de ECharts para la curva multi-participante (scoreboard / dashboards)."""
    with Session(engine) as s:
        ev = s.get(Evento, id_evento)
        if not ev:
            return {}
        modo = _modo_evento(s, ev)
        if modo == "futuro":
            return {}
        rank = scoreboard(id_evento, corte)[:top]
        if not rank:
            return {}
        valor_reto = {
            c.id_reto: c.puntaje_actual
            for c in s.exec(select(Contiene).where(Contiene.id_evento == id_evento)).all()
        }
        entradas = [
            (r["nombre"], _timeline_usuario(s, r["id_usuario"], id_evento, valor_reto, corte))
            for r in rank
        ]
    return _construir_opcion(modo, ev, entradas, con_leyenda=True, colores=PALETA, corte=corte)


def opcion_evolucion_usuario(id_evento: int | None, id_usuario: int | None,
                             corte: datetime | None = None) -> dict:
    """`option` de ECharts para la curva individual del jugador (perfil)."""
    if not id_evento or not id_usuario:
        return {}
    with Session(engine) as s:
        ev = s.get(Evento, id_evento)
        if not ev:
            return {}
        modo = _modo_evento(s, ev)
        if modo == "futuro":
            return {}
        u = s.get(Usuario, id_usuario)
        nombre = (u.alias or u.nombre) if u else "Yo"
        valor_reto = {
            c.id_reto: c.puntaje_actual
            for c in s.exec(select(Contiene).where(Contiene.id_evento == id_evento)).all()
        }
        entradas = [(nombre, _timeline_usuario(s, id_usuario, id_evento, valor_reto, corte))]
    return _construir_opcion(modo, ev, entradas, con_leyenda=False, colores=[VERDE], corte=corte)


def ranking_y_evolucion(id_evento: int | None,
                        corte: datetime | None = None) -> tuple[list[dict], dict]:
    """`(ranking, option_evolucion)` con cache en Redis por `(id_evento, corte)`.

    Se computa una sola vez por combinación sin importar cuántos clientes lo pidan;
    lo invalida `canales.publicar_scoreboard()` al aceptarse una flag / compra /
    cambio de freeze. Sin Redis → recomputa siempre.
    """
    if not id_evento:
        return [], {}
    hit = cache.obtener(id_evento, corte)
    if hit is not None:
        return hit.get("ranking", []), hit.get("opcion", {})
    ranking = scoreboard(id_evento, corte)
    opcion = opcion_evolucion(id_evento, top=10, corte=corte)
    cache.guardar(id_evento, corte, ranking, opcion)
    return ranking, opcion
