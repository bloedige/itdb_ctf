"""Componente React para las curvas de evolución de puntaje (Apache ECharts).

Lo comparten el scoreboard, los dashboards y el perfil del jugador. `rx.recharts`
no permite tooltip por-serie ni ubicar la leyenda libremente; este wrapper envuelve
`echarts-for-react`. El `option` se arma entero en Python
(`scoreboard.scoreboard_logic.opcion_evolucion*`) y el formatter del tooltip (que
tiene que ser una función JS, no serializable) se inyecta acá.
"""

import reflex as rx

# Formatter del tooltip + wrapper. El archivo compilado es .jsx: se puede usar JSX.
_CUSTOM_JS = r"""
const _fmtEvolucion = (p) => {
  const arr = Array.isArray(p.value) ? p.value : [p.value];
  const x = arr[0];
  const y = arr[1];
  let cuando = "";
  if (typeof x === "number" && x > 1e12) {
    cuando = new Date(x).toLocaleString("es-BO", {
      day: "2-digit", month: "2-digit", hour: "2-digit", minute: "2-digit",
    });
  } else if (typeof x === "number") {
    const h = Math.floor(x);
    const m = Math.round((x - h) * 60);
    cuando = h >= 24
      ? Math.floor(h / 24) + "d " + (h % 24) + "h"
      : h + "h " + (m < 10 ? "0" : "") + m + "m";
  }
  return "<b>" + p.seriesName + "</b><br/>" + y + " pts"
    + (cuando ? "<br/><span style='opacity:.6'>" + cuando + "</span>" : "");
};

function EvolucionChart({ option, altura }) {
  const h = altura || "360px";
  const vacio = typeof window === "undefined" || !option || !option.series || !option.series.length;
  if (vacio) {
    return (
      <div style={{ height: h, width: "100%", display: "flex",
                    alignItems: "center", justifyContent: "center",
                    color: "#9fb3c8", fontSize: "0.85rem", fontWeight: 300 }}>
        Sin datos de evolución todavía.
      </div>
    );
  }
  const opt = {
    ...option,
    tooltip: { ...(option.tooltip || {}), formatter: _fmtEvolucion },
  };
  return (
    <ReactECharts
      option={opt}
      notMerge={true}
      lazyUpdate={true}
      style={{ height: h, width: "100%" }}
    />
  );
}
"""


class EvolucionChart(rx.Component):
    """`<EvolucionChart option={...} altura="280px" />` — definido en custom code."""

    tag = "EvolucionChart"
    lib_dependencies = ["echarts@5.5.1"]

    option: rx.Var[dict]
    altura: rx.Var[str]

    def add_imports(self):
        return {
            "echarts-for-react@3.0.2": [rx.ImportVar(tag="ReactECharts", is_default=True)],
        }

    def add_custom_code(self):
        return [_CUSTOM_JS]


evolucion_chart = EvolucionChart.create
