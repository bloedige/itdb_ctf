from datetime import datetime, timezone

from sqlmodel import Session, select
from itdb_ctf.db import engine
from itdb_ctf.models import Resuelve, Usuario, Contiene, Compra, Evento, Modalidad
from itdb_ctf.core.puntaje_logic import puntaje_total_usuario

# Paleta para la curva de evolución (top 10). Los 5 primeros == scoreboard_view.COLORES.
PALETA = [
    "#00ffd0", "#ff7300", "#9dff00", "#8400ff", "#ff006a",
    "#00b8ff", "#ffd000", "#ff5b5b", "#b48cff", "#37ffb0",
]
VERDE = "#00ffc3"   # curva individual (perfil), igual que el gráfico recharts anterior

# Icono bandera (asta + banderín) para la leyenda. ECharts lo rellena con el color de la serie.
FLAG_PATH = "path://M4 2 L6 2 L6 22 L4 22 Z M6 3 L20 8 L6 13 Z"


def scoreboard(id_evento:int) -> list[dict]:
    with Session(engine) as s:
        filas = s.exec(select(Resuelve.id_usuario, Usuario.alias, Usuario.nombre)
                       .join(Usuario, Resuelve.id_usuario == Usuario.id_usuario)
                       .where(Resuelve.id_evento == id_evento, Resuelve.flag_correcta == True)).all()
        vistos = {}
        for id_u, ali, nom in filas:
            if not id_u in vistos:
                vistos[id_u]= ali if ali else nom
        ultimas = {}
        for id_u in vistos:
            ultimas[id_u] = s.exec(select(Resuelve.fec_envio).where(
                Resuelve.id_usuario == id_u,
                Resuelve.id_evento == id_evento,
                Resuelve.flag_correcta == True)
                .order_by(Resuelve.fec_envio.desc())).first()
        ranking = [
            {
                "id_usuario":id_usuario,
                "nombre":nombre,
                "puntaje":puntaje_total_usuario(s, id_usuario, id_evento),
                "ultima":ultimas[id_usuario],
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


def _timeline_usuario(s: Session, id_usuario: int, id_evento: int, valor_reto: dict) -> list[tuple]:
    """[(fec, acumulado_con_piso_0)] ordenado, solo aciertos + compras del usuario."""
    solves = s.exec(
        select(Resuelve.fec_envio, Resuelve.id_reto).where(
            Resuelve.id_usuario == id_usuario,
            Resuelve.id_evento == id_evento,
            Resuelve.flag_correcta == True,  # noqa: E712
        )
    ).all()
    compras = s.exec(
        select(Compra.fec_compra, Compra.puntos_usados).where(
            Compra.id_usuario == id_usuario,
            Compra.id_evento == id_evento,
        )
    ).all()
    eventos = [(f, valor_reto.get(r, 0)) for f, r in solves if f is not None]
    eventos += [(f, -p) for f, p in compras if f is not None]
    eventos.sort(key=lambda e: e[0])
    acum, salida = 0, []
    for fec, delta in eventos:
        acum = max(acum + delta, 0)
        salida.append((fec, acum))
    return salida


def _construir_opcion(modo: str, ev: Evento, entradas: list[tuple[str, list]],
                      *, con_leyenda: bool, colores: list) -> dict:
    """`option` de ECharts a partir de `[(nombre, [(fec, acum), ...]), ...]`.

    Eje X según `modo`: abierto -> fecha/hora real; activo/concluido -> horas
    desde `fec_inicio`. Devuelve `{}` si no hay ninguna actividad.
    """
    if not any(tl for _, tl in entradas):
        return {}

    tiempo_real = modo == "abierto"
    ahora = datetime.now(timezone.utc)

    if tiempo_real:
        fechas = [tl[0][0] for _, tl in entradas if tl]
        x_min = int(min(fechas).timestamp() * 1000)
        x_max = int(ahora.timestamp() * 1000)

        def to_x(fec):
            return int(fec.timestamp() * 1000)
    else:
        t0 = ev.fec_inicio
        if t0 is None:
            t0 = min(tl[0][0] for _, tl in entradas if tl)
        fin = ev.fec_fin if ev.fec_fin else ahora
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


def opcion_evolucion(id_evento: int, top: int = 10) -> dict:
    """`option` de ECharts para la curva multi-participante (scoreboard / dashboards)."""
    with Session(engine) as s:
        ev = s.get(Evento, id_evento)
        if not ev:
            return {}
        modo = _modo_evento(s, ev)
        if modo == "futuro":
            return {}
        rank = scoreboard(id_evento)[:top]
        if not rank:
            return {}
        valor_reto = {
            c.id_reto: c.puntaje_actual
            for c in s.exec(select(Contiene).where(Contiene.id_evento == id_evento)).all()
        }
        entradas = [
            (r["nombre"], _timeline_usuario(s, r["id_usuario"], id_evento, valor_reto))
            for r in rank
        ]
    return _construir_opcion(modo, ev, entradas, con_leyenda=True, colores=PALETA)


def opcion_evolucion_usuario(id_evento: int | None, id_usuario: int | None) -> dict:
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
        entradas = [(nombre, _timeline_usuario(s, id_usuario, id_evento, valor_reto))]
    return _construir_opcion(modo, ev, entradas, con_leyenda=False, colores=[VERDE])
