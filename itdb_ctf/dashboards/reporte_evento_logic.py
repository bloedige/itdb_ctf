"""Reporte PDF de un evento cerrado (fpdf2).

Función pura: entra un `id_evento`, sale `(bytes, nombre_archivo)`. **Sin Reflex.**
No hay SQL nuevo: todos los bloques se arman con las funciones que ya alimentan
el dashboard de eventos cerrados. El corte es siempre **en vivo** (`corte=None`),
igual que ve el admin en pantalla, aunque el scoreboard esté congelado.
"""

from datetime import datetime, timezone
from pathlib import Path

from fpdf import FPDF
from fpdf.fonts import FontFace
from sqlmodel import Session, select

from itdb_ctf.db import engine
from itdb_ctf.models import Evento, Contiene, Usuario
from itdb_ctf.reto.archivo_logic import nombre_seguro
from itdb_ctf.scoreboard import scoreboard_logic
from itdb_ctf.scoreboard.scoreboard_logic import ranking_y_evolucion
from itdb_ctf.dashboards import dashboard_metricas_logic as m
from itdb_ctf.dashboards.eventos_cerrados_dashboard_logic import (
    info_evento,
    actividad_evento,
)
from itdb_ctf.dashboards.reporte_graficos import (
    PALETA_PDF,
    NARANJA_PDF,
    VERDE_PDF,
    TINTA,
    GRIS,
    MARCO,
    hex_a_rgb,
    grafico_lineas,
)

TOP = 10
_MARGEN = 15.0
_ANCHO = 180.0       # 210 - 2 * margen

# .../ITDB_CTF/itdb_ctf/dashboards/este_archivo.py -> .../ITDB_CTF/assets/
# El isotipo es el logo de la plataforma: el mismo que sirve `navbar.py`.
# Son 6 `<path>` sin `<text>`, así que fpdf2 lo embebe vectorial y no pesa nada.
_LOGO = Path(__file__).resolve().parents[2] / "assets" / "isotipo.svg"

_ALTO_TITULO = 9.0
_ALTO_DETALLE = 5.0
# 80% del bloque de cabecera (título + detalle del evento)
_LOGO_ALTO_MM = 0.8 * (_ALTO_TITULO + _ALTO_DETALLE)
_LOGO_RATIO = 1041 / 797     # viewBox del isotipo
_LOGO_PAD_MM = 1.6           # aire interior del badge
_LOGO_SEP_MM = 2.2           # aire entre el isotipo y el texto, dentro del badge
_ORO = "#fab808"             # `navbar.ORO`
_BLANCO = "#f9f9fa"          # el mismo casi-blanco de los paths del isotipo


def _dibujar_logo(pdf: FPDF, derecha: float, y: float) -> float:
    """Dibuja el logo del navbar —isotipo + `ITDB · CTF`— dentro de un badge
    oscuro que termina en `derecha`. Devuelve el ancho ocupado, 0 si no se pudo.

    El fondo oscuro no es decoración: de los 6 paths del isotipo, 3 son casi
    blancos (`#f9f9fa`, `#fafafb`, `#fbfbfc`) porque está dibujado para la barra
    de navegación, y sobre el papel desaparecerían. El texto va en el mismo
    blanco y el punto en oro, igual que en `navbar.logo()`.

    `pdf.image()` no sirve: el SVG declara `width="100%" height="100%"` y sin
    tamaño intrínseco se escala a la página entera. `transform_to_rect_viewport`
    con `ignore_svg_top_attrs` lo mide por el viewBox y lo encaja en la caja dada.
    """
    if not _LOGO.is_file():
        return 0.0
    try:
        from fpdf.svg import SVGObject
        from fpdf.drawing import Transform

        alto = _LOGO_ALTO_MM
        alto_iso = alto - 2 * _LOGO_PAD_MM
        ancho_iso = alto_iso * _LOGO_RATIO

        pdf.set_font("Helvetica", "B", 9)
        partes = [("ITDB", _BLANCO), (" · ", _ORO), ("CTF", _BLANCO)]
        ancho_texto = sum(pdf.get_string_width(t) for t, _ in partes)
        ancho = _LOGO_PAD_MM + ancho_iso + _LOGO_SEP_MM + ancho_texto + _LOGO_PAD_MM + 1.0
        x = derecha - ancho

        pdf.set_fill_color(*hex_a_rgb(TINTA))
        pdf.rect(x, y, ancho, alto, style="F", round_corners=True, corner_radius=1.8)

        svg = SVGObject.from_file(str(_LOGO))
        _, _, path = svg.transform_to_rect_viewport(
            scale=1, width=ancho_iso, height=alto_iso, ignore_svg_top_attrs=True,
        )
        antes = (pdf.x, pdf.y)
        pdf.set_xy(0, 0)
        path.transform = path.transform @ Transform.translation(
            x + _LOGO_PAD_MM, y + _LOGO_PAD_MM)
        pdf.draw_path(path)
        pdf.set_xy(*antes)
        pdf.set_fill_color(255, 255, 255)

        cx = x + _LOGO_PAD_MM + ancho_iso + _LOGO_SEP_MM
        linea_base = y + alto / 2 + pdf.font_size * 0.36
        for texto, color in partes:
            pdf.set_text_color(*hex_a_rgb(color))
            pdf.text(cx, linea_base, texto)
            cx += pdf.get_string_width(texto)
        return ancho
    except Exception:
        return 0.0


# ------------------------------------------------------------------ utilidades

def _aware(dt) -> datetime | None:
    """Normaliza a datetime con tz.

    Acepta texto ISO porque `ranking_y_evolucion` puede venir del cache de Redis,
    que serializa los `datetime` a ISO (`websockets/cache.py`): el mismo ranking
    llega como objeto si se recomputa y como str si sale del cache.
    """
    if dt is None:
        return None
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except ValueError:
            return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _latin(texto: str) -> str:
    """Helvetica es una fuente core latin-1: los acentos salen bien, pero un
    caracter fuera del juego (—, →, emoji) reventaría el `output()`."""
    return str(texto).encode("latin-1", "replace").decode("latin-1")


def _recortar(pdf: FPDF, texto: str, ancho: float) -> str:
    texto = _latin(texto)
    if pdf.get_string_width(texto) <= ancho:
        return texto
    while texto and pdf.get_string_width(texto + "...") > ancho:
        texto = texto[:-1]
    return texto + "..."


def _correos(ids: list[int]) -> dict[int, str]:
    """`{id_usuario: email_inst}` del top del ranking. `scoreboard()` solo
    devuelve alias/nombre, así que el correo hay que traerlo aparte."""
    if not ids:
        return {}
    with Session(engine) as s:
        filas = s.exec(
            select(Usuario.id_usuario, Usuario.email_inst)
            .where(Usuario.id_usuario.in_(ids))
        ).all()
    return {i: c for i, c in filas}


# ------------------------------------------------------------------ datos crudos

def _series_evolucion(id_evento: int, ranking: list[dict]) -> list[dict]:
    """Series de la curva de evolución, con el eje X en horas desde `fec_inicio`.

    Reutiliza `scoreboard_logic._timeline_usuario` (privada) para no duplicar su
    SQL; `opcion_evolucion()` no sirve aquí porque devuelve la `option` de
    ECharts ya armada, no las series crudas.
    """
    if not ranking:
        return []
    with Session(engine) as s:
        ev = s.get(Evento, id_evento)
        if not ev:
            return []
        valor_reto = {
            c.id_reto: c.puntaje_actual
            for c in s.exec(select(Contiene).where(Contiene.id_evento == id_evento)).all()
        }
        crudas = [
            (r["nombre"],
             scoreboard_logic._timeline_usuario(s, r["id_usuario"], id_evento, valor_reto))
            for r in ranking
        ]
        t0 = _aware(ev.fec_inicio)
        ff = _aware(ev.fec_fin)

    if t0 is None:
        fechas = [tl[0][0] for _, tl in crudas if tl]
        if not fechas:
            return []
        t0 = _aware(min(fechas))

    ahora = datetime.now(timezone.utc)
    fin = min(ff, ahora) if ff else ahora
    x_max = round(max((fin - t0).total_seconds() / 3600, 0.1), 2)

    series = []
    for i, (nombre, tl) in enumerate(crudas):
        if not tl:
            continue
        reales = [
            (round((_aware(fec) - t0).total_seconds() / 3600, 4), float(acum))
            for fec, acum in tl
        ]
        # los dos extremos solo cierran la línea: en ECharts van con `symbol: none`
        puntos = [(0.0, 0.0)] + reales + [(x_max, float(tl[-1][1]))]
        series.append({
            "nombre": _latin(nombre),
            "color": PALETA_PDF[i % len(PALETA_PDF)],
            "puntos": puntos,
            "marcas": reales,
        })
    return series


def _series_actividad(actividad: list[dict]) -> tuple[list[dict], list[str]]:
    if not actividad:
        return [], []
    etiquetas = [str(f["t"]) for f in actividad]
    envios = [(float(i), float(f["envios"])) for i, f in enumerate(actividad)]
    resol = [(float(i), float(f["resoluciones"])) for i, f in enumerate(actividad)]
    return (
        [
            {"nombre": "Envíos", "color": NARANJA_PDF, "puntos": envios},
            {"nombre": "Resoluciones", "color": VERDE_PDF, "puntos": resol},
        ],
        etiquetas,
    )


# ------------------------------------------------------------------ bloques PDF

class _Reporte(FPDF):
    generado: str = ""

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", size=7)
        self.set_text_color(*hex_a_rgb(GRIS))
        tercio = _ANCHO / 3
        self.set_x(_MARGEN)
        self.cell(tercio, 5, "ITDB CTF", align="L")
        self.cell(tercio, 5, f"{self.page_no()}/{{nb}}", align="C")
        self.cell(tercio, 5, self.generado, align="R")


def _cabecera(pdf: _Reporte, info: dict) -> None:
    ancho_logo = _dibujar_logo(pdf, _MARGEN + _ANCHO, _MARGEN + 1)
    ancho_texto = _ANCHO - (ancho_logo + 6 if ancho_logo else 0)

    pdf.set_xy(_MARGEN, _MARGEN)
    titulo = _latin(info.get("titulo", ""))
    pdf.set_text_color(*hex_a_rgb(TINTA))
    for cuerpo in (17, 15, 13, 11):   # bajar el cuerpo antes que recortar el titulo
        pdf.set_font("Helvetica", "B", cuerpo)
        if pdf.get_string_width(titulo) <= ancho_texto:
            break
    pdf.cell(ancho_texto, _ALTO_TITULO, _recortar(pdf, titulo, ancho_texto),
             new_x="LMARGIN", new_y="NEXT")

    estado = str(info.get("estado", "")).capitalize()
    linea = f"{estado}  |  {info.get('fec_inicio', '')} - {info.get('fec_fin', '')}"
    if info.get("tiempo_texto"):
        linea += f"  |  {info['tiempo_texto']}"
    pdf.set_font("Helvetica", size=9)
    pdf.set_text_color(*hex_a_rgb(GRIS))
    pdf.cell(ancho_texto, _ALTO_DETALLE, _recortar(pdf, linea, ancho_texto),
             new_x="LMARGIN", new_y="NEXT")

    y = max(pdf.get_y() + 1.5, _MARGEN + 1 + _LOGO_ALTO_MM if ancho_logo else 0)
    pdf.set_draw_color(*hex_a_rgb(MARCO))
    pdf.set_line_width(0.3)
    pdf.line(_MARGEN, y, _MARGEN + _ANCHO, y)
    pdf.set_y(y + 4)


def _kpi(pdf: _Reporte, x: float, y: float, w: float, h: float,
         titulo: str, valor: str, detalle: str) -> None:
    """Misma jerarquía que `dashboard_componentes.kpi()`: tarjeta blanca de
    esquinas redondeadas, rótulo en gris, cifra grande y detalle tenue."""
    pdf.set_draw_color(215, 222, 230)
    pdf.set_fill_color(255, 255, 255)
    pdf.set_line_width(0.2)
    pdf.rect(x, y, w, h, style="DF", round_corners=True, corner_radius=1.6)

    pdf.set_font("Helvetica", size=8)
    pdf.set_text_color(*hex_a_rgb(GRIS))
    pdf.text(x + 4, y + 6, _recortar(pdf, titulo, w - 8))

    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*hex_a_rgb(TINTA))
    pdf.text(x + 4, y + 14.5, _recortar(pdf, valor, w - 8))

    pdf.set_font("Helvetica", size=7)
    pdf.set_text_color(150, 160, 175)
    pdf.text(x + 4, y + 19.5, _recortar(pdf, detalle, w - 8))


def _fila_kpis(pdf: _Reporte, y: float, r: dict) -> float:
    ancho = (_ANCHO - 2 * 4) / 3
    datos = [
        ("Participantes", str(r.get("participantes_total", 0)),
         f"{r.get('participantes_inscritos', 0)} inscritos, "
         f"{r.get('participantes_descalificados', 0)} descalificados"),
        ("Participación real", f"{r.get('pct_participacion', 0)}%",
         f"{r.get('participantes_activos', 0)} con al menos un envío"),
        ("Tasa de acierto", f"{r.get('tasa_acierto', 0)}%",
         f"{r.get('envios_correctos', 0)} correctos de {r.get('envios_total', 0)} envíos"),
    ]
    for i, (t, v, d) in enumerate(datos):
        _kpi(pdf, _MARGEN + i * (ancho + 4), y, ancho, 23, t, v, d)
    return y + 23


def _titulo_seccion(pdf: _Reporte, y: float, texto: str) -> float:
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(*hex_a_rgb(TINTA))
    pdf.text(_MARGEN, y, _latin(texto))
    return y + 2.5


def _encabezado_tabla() -> FontFace:
    return FontFace(emphasis="BOLD", color=(255, 255, 255), fill_color=hex_a_rgb(TINTA))


def _tabla_ranking(pdf: _Reporte, y: float, ranking: list[dict]) -> None:
    pdf.set_xy(_MARGEN, y)
    pdf.set_font("Helvetica", size=8)
    pdf.set_text_color(*hex_a_rgb(TINTA))
    if not ranking:
        pdf.set_text_color(*hex_a_rgb(GRIS))
        pdf.cell(0, 6, "Sin resoluciones todavía.")
        return
    correos = _correos([r["id_usuario"] for r in ranking if r.get("id_usuario")])
    with pdf.table(
        col_widths=(16, 62, 72, 30),
        text_align=("CENTER", "LEFT", "LEFT", "RIGHT"),
        headings_style=_encabezado_tabla(),
        cell_fill_mode="ROWS",
        cell_fill_color=(244, 246, 250),
        line_height=6,
        width=_ANCHO,
    ) as t:
        cab = t.row()
        for c in ("Posición", "Participante", "Correo", "Puntaje"):
            cab.cell(c)
        for r in ranking:
            fila = t.row()
            fila.cell(str(r.get("posicion", "")))
            fila.cell(_recortar(pdf, r.get("nombre", ""), 58))
            fila.cell(_recortar(pdf, correos.get(r.get("id_usuario"), "-"), 68))
            fila.cell(str(r.get("puntaje", 0)))


def _tabla_categorias(pdf: _Reporte, y: float, categorias: list[dict]) -> None:
    pdf.set_xy(_MARGEN, y)
    pdf.set_font("Helvetica", size=8)
    pdf.set_text_color(*hex_a_rgb(TINTA))
    if not categorias:
        pdf.set_text_color(*hex_a_rgb(GRIS))
        pdf.cell(0, 6, "El evento no tiene retos asociados.")
        return
    total = sum(c.get("retos", 0) for c in categorias)
    negrita = FontFace(emphasis="BOLD")
    with pdf.table(
        col_widths=(130, 50),
        text_align=("LEFT", "CENTER"),
        headings_style=_encabezado_tabla(),
        cell_fill_mode="ROWS",
        cell_fill_color=(244, 246, 250),
        line_height=6,
        width=_ANCHO,
    ) as t:
        cab = t.row()
        for c in ("Categoría", "Retos"):
            cab.cell(c)
        for c in categorias:
            fila = t.row()
            fila.cell(_recortar(pdf, c.get("etiqueta", ""), 126))
            fila.cell(str(c.get("retos", 0)))
        fila = t.row(style=negrita)
        fila.cell("Total de retos")
        fila.cell(str(total))


# ------------------------------------------------------------------ entrada

def generar_reporte_evento(id_evento: int) -> tuple[bytes, str]:
    """Devuelve `(pdf_bytes, nombre_archivo)` del reporte del evento.

    Lanza `ValueError` si el evento no existe.
    """
    info = info_evento(id_evento)
    if not info.get("hay_evento"):
        raise ValueError("El evento no existe.")

    resumen = m.resumen_evento(id_evento)
    categorias = m.desglose_categoria(id_evento)
    ranking = ranking_y_evolucion(id_evento, None)[0][:TOP]
    evolucion = _series_evolucion(id_evento, ranking)
    actividad, etiquetas_act = _series_actividad(actividad_evento(id_evento))

    pdf = _Reporte(unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.set_margins(_MARGEN, _MARGEN, _MARGEN)
    pdf.set_title(_latin(f"Reporte - {info['titulo']}"))
    pdf.generado = datetime.now().strftime("%d/%m/%Y %H:%M")
    pdf.alias_nb_pages()

    # --- pagina 1
    pdf.add_page()
    _cabecera(pdf, info)
    y = _fila_kpis(pdf, pdf.get_y(), resumen)

    y += 7
    grafico_lineas(pdf, _MARGEN, y, _ANCHO, 80, evolucion,
                   titulo=f"Evolución de puntaje · top {TOP}",
                   titulo_x="Horas desde el inicio", leyenda=True)

    y = _titulo_seccion(pdf, y + 80 + 9, f"Ranking (top {TOP})")
    _tabla_ranking(pdf, y, ranking)

    # --- pagina 2
    pdf.add_page()
    y = _MARGEN
    grafico_lineas(pdf, _MARGEN, y, _ANCHO, 76, actividad,
                   titulo="Actividad durante el evento",
                   etiquetas_x=etiquetas_act, leyenda=True)

    y = _titulo_seccion(pdf, y + 76 + 9, "Retos por categoría")
    _tabla_categorias(pdf, y, categorias)

    datos = bytes(pdf.output())
    sello = datetime.now().strftime("%Y%m%d-%H%M")
    slug = nombre_seguro(info["titulo"])[:40].strip("_") or "evento"
    nombre = f"reporte_{slug}_{sello}.pdf"
    return datos, nombre
