"""Primitivas de gráficos para los reportes PDF (fpdf2).

fpdf2 no renderiza el `<text>` de un SVG (lo salta en silencio), así que los
gráficos se dibujan con las primitivas nativas (`line` / `rect` / `text`): salen
vectoriales y con las etiquetas en texto PDF real.

La composición imita la del dashboard de eventos cerrados: tarjeta con el título
en gris (`dashboard_componentes.panel`), rejilla punteada en los dos ejes,
línea solo en el eje X y leyenda con el icono de bandera
(`scoreboard_logic.FLAG_PATH`). Lo único que no se copia es el fondo oscuro:
sobre papel va en claro.

Este módulo no sabe nada del dominio: recibe series ya armadas y las pinta
dentro del rectángulo que se le indique. Todas las medidas en mm.
"""

import math

# La PALETA de `scoreboard_logic` es neón (fondo oscuro) y resulta ilegible
# impresa sobre blanco. Estos son los mismos 10 slots, en el mismo orden, para
# que el PDF conserve la correspondencia de colores con la pantalla.
PALETA_PDF = [
    "#00806a", "#c25400", "#5c8f00", "#5a00b0", "#b3004a",
    "#0077a8", "#a88900", "#c23b3b", "#6f4fc0", "#1d9e6c",
]

NARANJA_PDF = "#c25400"
VERDE_PDF = "#00806a"

TINTA = "#12233a"      # texto principal
GRIS = "#5a6b7f"       # etiquetas de ejes y título de la tarjeta
REJILLA = "#d8e0e8"    # `splitLine` punteado
MARCO = "#a9b7c6"      # `axisLine` del eje X
BORDE = "#d7dee6"      # borde de la tarjeta

_PAD_IZQ = 13.0        # hueco para las etiquetas del eje Y
_PAD_DER = 4.0
_PAD_ARR = 4.0
_PAD_ABA = 8.0         # hueco para las etiquetas del eje X
_ALTO_LEYENDA = 9.0
_RADIO_MARCA = 0.7     # equivale al `symbolSize: 6` de ECharts

_TARJETA_PAD = 4.0
_TARJETA_TITULO = 8.5

_BANDERA_K = 0.11      # escala del viewBox 24x24 de FLAG_PATH -> mm


def hex_a_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _paso_bonito(valor: float) -> float:
    """Redondea `valor` al siguiente 1/2/2.5/5 × 10^n — para ticks legibles."""
    if valor <= 0:
        return 1.0
    exp = math.floor(math.log10(valor))
    base = valor / (10 ** exp)
    for m in (1, 2, 2.5, 5):
        if base <= m:
            return m * (10 ** exp)
    return 10 ** (exp + 1)


def _fmt_num(v: float) -> str:
    return str(int(round(v))) if abs(v - round(v)) < 1e-9 else f"{v:g}"


def _tarjeta(pdf, x: float, y: float, w: float, h: float, titulo: str) -> tuple:
    """Dibuja la tarjeta con su título y devuelve el rectángulo interior libre.

    Es el `panel()` del dashboard: `rx.card` con el título arriba en gris.
    """
    pdf.set_draw_color(*hex_a_rgb(BORDE))
    pdf.set_fill_color(255, 255, 255)
    pdf.set_line_width(0.2)
    pdf.rect(x, y, w, h, style="DF", round_corners=True, corner_radius=1.6)

    pdf.set_font("Helvetica", size=9)
    pdf.set_text_color(*hex_a_rgb(GRIS))
    pdf.text(x + _TARJETA_PAD + 1, y + 6.2, titulo)

    return (x + _TARJETA_PAD,
            y + _TARJETA_TITULO,
            w - 2 * _TARJETA_PAD,
            h - _TARJETA_TITULO - _TARJETA_PAD)


def _sin_datos(pdf, x: float, y: float, w: float, h: float) -> None:
    pdf.set_font("Helvetica", size=8)
    pdf.set_text_color(*hex_a_rgb(GRIS))
    texto = "Sin datos todavía."
    pdf.text(x + (w - pdf.get_string_width(texto)) / 2, y + h / 2, texto)


def grafico_lineas(
    pdf,
    x: float,
    y: float,
    w: float,
    h: float,
    series: list[dict],
    *,
    titulo: str = "",
    etiquetas_x: list[str] | None = None,
    titulo_x: str = "",
    leyenda: bool = True,
    suave: bool = True,
) -> None:
    """Dibuja un gráfico de líneas dentro del rectángulo (x, y, w, h).

    `series`: `[{"nombre": str, "color": "#rrggbb", "puntos": [(xv, yv)],
    "marcas": [(xv, yv)]}]`. `marcas` es opcional: los puntos que llevan círculo
    (en la evolución, los instantes en que el puntaje cambió de verdad).
    `titulo`: si se pasa, el gráfico va dentro de una tarjeta como en el dashboard.
    `etiquetas_x`: si se pasa, el eje X es categórico y los `xv` son índices
    dentro de esa lista; si es `None`, el eje X es numérico.
    `suave`: traza curvas en vez de rectas, para que el PDF conserve la forma
    que tienen las mismas series en pantalla (ECharts y recharts las suavizan).
    """
    if titulo:
        x, y, w, h = _tarjeta(pdf, x, y, w, h, titulo)

    con_datos = [s for s in series if s.get("puntos")]
    if not con_datos:
        _sin_datos(pdf, x, y, w, h)
        _restaurar(pdf)
        return

    pad_aba = _PAD_ABA + (_ALTO_LEYENDA if leyenda else 0.0)
    px = x + _PAD_IZQ
    py = y + _PAD_ARR
    pw = max(w - _PAD_IZQ - _PAD_DER, 1.0)
    ph = max(h - _PAD_ARR - pad_aba, 1.0)

    todos_x = [p[0] for s in con_datos for p in s["puntos"]]
    todos_y = [p[1] for s in con_datos for p in s["puntos"]]
    x_min, x_max = min(todos_x), max(todos_x)
    if x_max <= x_min:
        x_max = x_min + 1
    y_max = max(todos_y)
    paso_y = _paso_bonito(y_max / 4 if y_max > 0 else 1)
    y_tope = max(paso_y * math.ceil(y_max / paso_y), paso_y) if y_max > 0 else paso_y

    def a_px(vx: float) -> float:
        return px + (vx - x_min) / (x_max - x_min) * pw

    def a_py(vy: float) -> float:
        return py + ph - (vy / y_tope) * ph

    base_y = py + ph

    # --- ticks del eje X (máx. 6, repartidos)
    if etiquetas_x:
        total = len(etiquetas_x)
        salto = max(1, math.ceil(total / 6))
        ticks_x = [(i, etiquetas_x[i]) for i in range(0, total, salto)]
    else:
        n = 5
        ticks_x = [
            (x_min + (x_max - x_min) * i / n,
             f"{_fmt_num(x_min + (x_max - x_min) * i / n)} h")
            for i in range(n + 1)
        ]

    # --- rejilla punteada en los dos ejes (`splitLine` de X y de Y)
    pdf.set_font("Helvetica", size=6)
    pdf.set_text_color(*hex_a_rgb(GRIS))
    pdf.set_draw_color(*hex_a_rgb(REJILLA))
    pdf.set_line_width(0.15)
    pdf.set_dash_pattern(dash=0.5, gap=0.8)
    v = 0.0
    while v <= y_tope + 1e-9:
        yy = a_py(v)
        pdf.line(px, yy, px + pw, yy)
        etq = _fmt_num(v)
        pdf.text(px - 1.5 - pdf.get_string_width(etq), yy + 1.0, etq)
        v += paso_y
    for vx, _ in ticks_x:
        xx = a_px(vx)
        pdf.line(xx, py, xx, base_y)
    pdf.set_dash_pattern()

    # --- etiquetas del eje X
    for vx, etq in ticks_x:
        xx = a_px(vx)
        ancho = pdf.get_string_width(etq)
        pdf.text(min(max(xx - ancho / 2, x + 0.5), x + w - ancho - 0.5), base_y + 3.5, etq)

    if titulo_x:
        pdf.text(px + (pw - pdf.get_string_width(titulo_x)) / 2, base_y + 7.0, titulo_x)

    # --- solo la línea del eje X: el eje de valores de ECharts no lleva `axisLine`
    pdf.set_draw_color(*hex_a_rgb(MARCO))
    pdf.set_line_width(0.25)
    pdf.line(px, base_y, px + pw, base_y)

    # --- series
    pdf.set_line_width(0.45)
    for s in con_datos:
        pdf.set_draw_color(*hex_a_rgb(s.get("color", TINTA)))
        pts = [(a_px(vx), a_py(min(vy, y_tope))) for vx, vy in s["puntos"]]
        if suave:
            for tramo in _tramos_suaves(pts):
                pdf.bezier(tramo)
        else:
            for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
                pdf.line(x1, y1, x2, y2)
        marcas = s.get("marcas") or ([] if len(pts) > 1 else [s["puntos"][0]])
        if marcas:
            pdf.set_fill_color(*hex_a_rgb(s.get("color", TINTA)))
            for vx, vy in marcas:
                # ojo: pese a lo que dice su docstring, `circle` recibe el CENTRO
                # (por dentro hace `ellipse(x - radius, y - radius, 2r, 2r)`)
                pdf.circle(a_px(vx), a_py(min(vy, y_tope)), _RADIO_MARCA, style="F")

    if leyenda:
        _leyenda(pdf, x + 2.0, base_y + 9.5, w - 4.0, con_datos)

    _restaurar(pdf)


def _bandera(pdf, x: float, y: float) -> float:
    """El icono de la leyenda del scoreboard: asta + banderín.

    Port de `scoreboard_logic.FLAG_PATH`
    (`M4 2 L6 2 L6 22 L4 22 Z  M6 3 L20 8 L6 13 Z`) sobre un viewBox de 24x24.
    Devuelve el ancho que ocupa.
    """
    k = _BANDERA_K
    pdf.rect(x, y, 2 * k, 20 * k, style="F")                      # asta
    pdf.polygon([(x + 2 * k, y + 1 * k),
                 (x + 16 * k, y + 6 * k),
                 (x + 2 * k, y + 11 * k)], style="F")             # banderín
    return 16 * k


def _leyenda(pdf, x: float, y: float, w: float, series: list[dict]) -> None:
    """Bandera del color de la serie + nombre, con salto de línea."""
    pdf.set_font("Helvetica", size=6)
    alto_icono = 20 * _BANDERA_K
    # centro óptico del texto: media altura de mayúsculas por encima de la base
    medio_texto = pdf.font_size * 0.36
    desplace = medio_texto + alto_icono / 2
    cx, cy = x, y
    for s in series:
        etq = s.get("nombre", "")
        ancho = alto_icono + 1.4 + pdf.get_string_width(etq) + 3.5
        if cx + ancho > x + w:
            cx, cy = x, cy + 4.0
        pdf.set_fill_color(*hex_a_rgb(s.get("color", TINTA)))
        w_icono = _bandera(pdf, cx, cy - desplace)
        pdf.set_text_color(*hex_a_rgb(GRIS))
        pdf.text(cx + w_icono + 1.4, cy, etq)
        cx += ancho


def _tramos_suaves(pts: list[tuple[float, float]]) -> list[list[tuple[float, float]]]:
    """Convierte la polilínea en tramos de Bézier cúbica (Catmull-Rom).

    Las tangentes se recortan al rectángulo de cada tramo: sin ese tope la curva
    sobrepasa en los saltos bruscos y dibujaría puntajes que nunca existieron
    (las series son acumuladas y tienen piso 0).
    """
    n = len(pts)
    if n < 2:
        return []
    tramos = []
    for i in range(n - 1):
        p1, p2 = pts[i], pts[i + 1]
        p0 = pts[i - 1] if i > 0 else p1
        p3 = pts[i + 2] if i + 2 < n else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        x_lo, x_hi = min(p1[0], p2[0]), max(p1[0], p2[0])
        y_lo, y_hi = min(p1[1], p2[1]), max(p1[1], p2[1])

        def tope(c):
            return (min(max(c[0], x_lo), x_hi), min(max(c[1], y_lo), y_hi))

        tramos.append([p1, tope(c1), tope(c2), p2])
    return tramos


def _restaurar(pdf) -> None:
    """Devuelve trazo y relleno a un neutro: si no, lo siguiente que se dibuje
    (las tablas) hereda el color de la ultima serie."""
    pdf.set_dash_pattern()
    pdf.set_draw_color(*hex_a_rgb(MARCO))
    pdf.set_fill_color(255, 255, 255)
    pdf.set_line_width(0.2)
