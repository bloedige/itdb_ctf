import base64
import logging

import reflex as rx

from itdb_ctf.auth.auth_state import AuthState
from itdb_ctf.scoreboard.scoreboard_logic import ranking_y_evolucion
from itdb_ctf.dashboards import dashboard_metricas_logic as m
from itdb_ctf.dashboards.eventos_cerrados_dashboard_logic import (
    listar_eventos_cerrados,
    info_evento,
    actividad_evento,
    feed_resoluciones,
)
from itdb_ctf.dashboards.reporte_evento_logic import generar_reporte_evento
from itdb_ctf.websockets import freeze_logic, canales, suscriptor

_log = logging.getLogger(__name__)


class EventosCerradosDashboardState(AuthState):
    eventos: list[list[str]] = []
    id_sel: str = ""
    info: dict = {}
    resumen: dict = {}
    categoria: list[dict] = []
    dificultad: list[dict] = []
    actividad: list[dict] = []
    ranking: list[dict] = []
    evol_opcion: dict = {}
    feed: list[dict] = []
    streaming: bool = False
    tick_token: int = 0

    # preview del reporte (diálogo)
    reporte_abierto: bool = False
    reporte_uri: str = ""        # data:application/pdf;base64,... que consume react-pdf
    reporte_nombre: str = ""
    reporte_paginas: int = 1
    reporte_pagina: int = 1

    @rx.var
    def hay_eventos(self) -> bool:
        return len(self.eventos) > 0

    @rx.var
    def hay_seleccion(self) -> bool:
        return bool(self.info.get("hay_evento"))

    @rx.var
    def evento_activo(self) -> bool:
        return self.info.get("estado") == "activo"

    @rx.var
    def esta_congelado(self) -> bool:
        return bool(self.info.get("freeze"))

    @rx.var
    def hay_ranking(self) -> bool:
        return len(self.ranking) > 0

    @rx.var
    def hay_feed(self) -> bool:
        return len(self.feed) > 0

    @rx.var
    def texto_paginas(self) -> str:
        return f"{self.reporte_pagina} / {self.reporte_paginas}"

    def _recargar(self):
        if not self.id_sel:
            self.info = {}
            self.resumen = {}
            self.categoria = self.dificultad = self.actividad = []
            self.ranking = self.feed = []
            self.evol_opcion = {}
            return
        id_ev = int(self.id_sel)
        self.info = info_evento(id_ev)
        self.resumen = m.resumen_evento(id_ev)
        self.categoria = m.desglose_categoria(id_ev)
        self.dificultad = m.desglose_dificultad(id_ev)
        self.actividad = actividad_evento(id_ev)
        self.feed = feed_resoluciones(id_ev)
        r, o = ranking_y_evolucion(id_ev, None)   # admin -> siempre en vivo (cacheado)
        self.ranking = r[:10]
        self.evol_opcion = o

    def _refrescar_vivo(self):
        """Refresco liviano para el suscriptor: lo que cambia con aciertos / freeze."""
        if not self.id_sel:
            return
        id_ev = int(self.id_sel)
        self.info = info_evento(id_ev)            # badge / botón freeze
        r, o = ranking_y_evolucion(id_ev, None)   # cacheado
        self.ranking = r[:10]
        self.evol_opcion = o
        self.feed = feed_resoluciones(id_ev)

    @rx.event(background=True)
    async def escuchar(self):
        """Suscripción Redis: el badge de freeze y el ranking se actualizan solos
        para todos los admin que estén mirando el mismo evento."""
        await suscriptor.escuchar(
            self,
            clave_getter=lambda s: int(s.id_sel) if s.id_sel else None,
            canales_getter=lambda s: (
                [canales.ch_scoreboard(int(s.id_sel)), canales.ch_freeze(int(s.id_sel))]
                if s.id_sel else []
            ),
            recargar=lambda s: s._refrescar_vivo(),
        )

    @rx.event
    def parar(self):
        self.streaming = False

    @rx.event
    def cargar_todo(self):
        guard = self.requiere_admin()
        if guard:
            return guard
        self.eventos = [list(t) for t in listar_eventos_cerrados()]
        ids = {e[0] for e in self.eventos}
        if self.id_sel not in ids:
            self.id_sel = self.eventos[0][0] if self.eventos else ""
        self._recargar()

    @rx.event
    def set_evento(self, v: str):
        self.id_sel = v
        self._recargar()

    @rx.event
    def actualizar(self):
        return EventosCerradosDashboardState.cargar_todo

    @rx.event
    def abrir_reporte(self):
        """Genera el PDF del evento y abre el diálogo de previsualización.

        Corte en vivo (`corte=None`): el reporte es del admin, así que muestra los
        datos reales aunque el scoreboard público esté congelado.

        El PDF se guarda como data URI porque es lo que consume `react-pdf`; de paso
        sirve para la descarga, que así no vuelve a generarlo.
        """
        guard = self.requiere_admin()
        if guard:
            return guard
        if not self.id_sel:
            return
        try:
            datos, nombre = generar_reporte_evento(int(self.id_sel))
        except Exception:
            _log.exception("fallo al generar el reporte del evento %s", self.id_sel)
            return rx.toast.error("No se pudo generar el reporte.")
        self.reporte_uri = "data:application/pdf;base64," + base64.b64encode(datos).decode()
        self.reporte_nombre = nombre
        self.reporte_paginas = 1
        self.reporte_pagina = 1
        self.reporte_abierto = True

    @rx.event
    def cerrar_reporte(self):
        # vaciar el data URI: no tiene sentido cargar el State con el PDF entero
        self.reporte_abierto = False
        self.reporte_uri = ""
        self.reporte_nombre = ""

    @rx.event
    def reporte_cargado(self, info: dict):
        """`on_load_success` de react-pdf: trae `numPages`."""
        self.reporte_paginas = max(int(info.get("numPages", 1) or 1), 1)
        if self.reporte_pagina > self.reporte_paginas:
            self.reporte_pagina = self.reporte_paginas

    @rx.event
    def pagina_anterior(self):
        if self.reporte_pagina > 1:
            self.reporte_pagina -= 1

    @rx.event
    def pagina_siguiente(self):
        if self.reporte_pagina < self.reporte_paginas:
            self.reporte_pagina += 1

    @rx.event
    def descargar_reporte(self):
        """Entrega el PDF ya generado por `abrir_reporte`, sin recalcularlo."""
        guard = self.requiere_admin()
        if guard:
            return guard
        if not self.reporte_uri:
            return
        datos = base64.b64decode(self.reporte_uri.split(",", 1)[1])
        return rx.download(data=datos, filename=self.reporte_nombre,
                           mime_type="application/pdf")

    @rx.event
    def congelar(self):
        """Alterna el freeze del scoreboard del evento seleccionado (en Redis)."""
        guard = self.requiere_admin()
        if guard:
            return guard
        if not self.id_sel:
            return
        id_ev = int(self.id_sel)
        if freeze_logic.esta_congelado(id_ev):
            freeze_logic.descongelar(id_ev)
            msg = "Scoreboard descongelado."
        else:
            fecha = freeze_logic.congelar(id_ev)
            msg = "Scoreboard congelado." if fecha else "No se pudo congelar (Redis no disponible)."
        self._recargar()
        return rx.toast.success(msg)
