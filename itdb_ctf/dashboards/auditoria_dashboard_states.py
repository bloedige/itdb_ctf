import reflex as rx

from itdb_ctf.auth.auth_state import AuthState
from itdb_ctf.dashboards.auditoria_dashboard_logic import (
    LIMITE_INICIAL,
    LIMITE_MAXIMO,
    RESUMEN_VACIO,
    SALUD_VACIA,
    auditoria_por_dia,
    bitacora,
    contar_bitacora,
    detalle_auditoria,
    listar_actores_opciones,
    listar_operaciones_opciones,
    listar_periodos_opciones,
    listar_tablas_opciones,
    resumen_auditoria,
    salud_plataforma,
)
from itdb_ctf.dashboards.retos_dashboard_logic import resumen_retos
from itdb_ctf.dashboards.usuarios_dashboard_logic import resumen_usuarios
from itdb_ctf.websockets import canales, suscriptor
from itdb_ctf.websockets.suscriptor import SuscriptorMixin


class AuditoriaDashboardState(SuscriptorMixin, AuthState):
    # cabecera
    salud: dict = dict(SALUD_VACIA)
    resumen: dict = dict(RESUMEN_VACIO)
    padron: dict = {}
    retos: dict = {}
    serie_cambios: list[dict] = []

    # bitácora
    filas: list[dict] = []
    total_filas: int = 0
    limite: int = LIMITE_INICIAL

    # filtros
    tablas_opciones: list[list[str]] = []
    operaciones_opciones: list[list[str]] = []
    actores_opciones: list[list[str]] = []
    periodos_opciones: list[list[str]] = []
    tabla_sel: str = "todas"
    operacion_sel: str = "todas"
    actor_sel: str = "todos"
    periodo_sel: str = "7"

    # diálogo de detalle
    detalle: dict = {}
    # los cambios van aparte y tipados: indexar un dict Var da Any y rx.foreach lo rechaza
    detalle_cambios: list[dict] = []
    detalle_abierto: bool = False

    # --- VARS DERIVADAS ---

    @rx.var
    def redis_ok(self) -> bool:
        return bool(self.salud.get("redis"))

    @rx.var
    def hay_filas(self) -> bool:
        return len(self.filas) > 0

    @rx.var
    def hay_mas(self) -> bool:
        return self.total_filas > len(self.filas) and self.limite < LIMITE_MAXIMO

    @rx.var
    def hay_congelados(self) -> bool:
        return self.salud.get("congelados", 0) > 0

    @rx.var
    def hay_detalle(self) -> bool:
        return len(self.detalle_cambios) > 0

    @rx.var
    def texto_eventos(self) -> str:
        s = self.salud
        return (
            f"{s.get('activos', 0)} activos · {s.get('futuros', 0)} futuros · "
            f"{s.get('concluidos', 0)} concluidos"
        )

    @staticmethod
    def _reparto(pares) -> list[dict]:
        """[(etiqueta, valor)] -> [{etiqueta, valor, pct}] con guardia de /0."""
        total = sum(v for _, v in pares)
        return [
            {
                "etiqueta": et,
                "valor": v,
                "pct": round(v / total * 100, 1) if total else 0.0,
            }
            for et, v in pares
        ]

    @rx.var
    def reparto_usuarios(self) -> list[dict]:
        p = self.padron
        return self._reparto(
            [("activos", p.get("activos", 0)), ("inactivos", p.get("inactivos", 0))]
        )

    @rx.var
    def reparto_retos(self) -> list[dict]:
        r = self.retos
        return self._reparto(
            [("activos", r.get("activos", 0)), ("inactivos", r.get("inactivos", 0))]
        )

    @rx.var
    def reparto_staff(self) -> list[dict]:
        p = self.padron
        return self._reparto([
            ("superadmin", p.get("superadmin", 0)),
            ("admin", p.get("admin", 0)),
            ("autor", p.get("autor", 0)),
        ])

    @rx.var
    def staff_total(self) -> int:
        p = self.padron
        return p.get("superadmin", 0) + p.get("admin", 0) + p.get("autor", 0)

    @rx.var
    def texto_conteo(self) -> str:
        return f"{len(self.filas)} de {self.total_filas} registros"

    # --- PRIVADAS ---

    def _args(self) -> dict:
        return {
            "tabla": None if self.tabla_sel == "todas" else self.tabla_sel,
            "operacion": None if self.operacion_sel == "todas" else self.operacion_sel,
            "actor": None if self.actor_sel == "todos" else self.actor_sel,
            "dias": int(self.periodo_sel) or None,
        }

    def _cargar_cabecera(self):
        self.salud = salud_plataforma()
        self.resumen = resumen_auditoria(30)
        self.serie_cambios = auditoria_por_dia(30)
        self.padron = resumen_usuarios()
        self.retos = resumen_retos()

    def _cargar_bitacora(self):
        a = self._args()
        self.filas = bitacora(**a, limite=self.limite)
        self.total_filas = contar_bitacora(**a)

    def _refrescar(self):
        """Lo que corre en cada aviso del canal de auditoría."""
        self._cargar_cabecera()
        self._cargar_bitacora()
        self.actores_opciones = listar_actores_opciones()

    # --- HANDLERS ---

    @rx.event
    def cargar_dashboard(self):
        guard = self.requiere_superadmin()
        if guard:
            return guard
        self.tablas_opciones = listar_tablas_opciones()
        self.operaciones_opciones = listar_operaciones_opciones()
        self.periodos_opciones = listar_periodos_opciones()
        self.limite = LIMITE_INICIAL
        self._refrescar()

    @rx.event(background=True)
    async def escuchar_auditoria(self):
        await suscriptor.escuchar(
            self,
            clave_getter=lambda s: "auditoria",
            canales_getter=lambda s: [canales.CH_AUDITORIA],
            recargar=lambda s: s._refrescar(),
            # el push de after_commit cubre toda escritura auditada; este fallback
            # solo cubre cambios hechos fuera de la app (psql directo)
            fallback_seg=60,
        )

    @rx.event
    def parar_auditoria(self):
        self.streaming = False

    @rx.event
    def set_tabla(self, v: str):
        guard = self.requiere_superadmin()
        if guard:
            return guard
        self.tabla_sel = v
        self.limite = LIMITE_INICIAL
        self._cargar_bitacora()

    @rx.event
    def set_operacion(self, v: str):
        guard = self.requiere_superadmin()
        if guard:
            return guard
        self.operacion_sel = v
        self.limite = LIMITE_INICIAL
        self._cargar_bitacora()

    @rx.event
    def set_actor(self, v: str):
        guard = self.requiere_superadmin()
        if guard:
            return guard
        self.actor_sel = v
        self.limite = LIMITE_INICIAL
        self._cargar_bitacora()

    @rx.event
    def set_periodo(self, v: str):
        guard = self.requiere_superadmin()
        if guard:
            return guard
        self.periodo_sel = v
        self.limite = LIMITE_INICIAL
        self._cargar_bitacora()

    @rx.event
    def ver_mas(self):
        guard = self.requiere_superadmin()
        if guard:
            return guard
        if self.limite >= LIMITE_MAXIMO:
            return
        self.limite += LIMITE_INICIAL
        self._cargar_bitacora()

    @rx.event
    def ver_detalle(self, id_auditoria: str):
        guard = self.requiere_superadmin()
        if guard:
            return guard
        d = detalle_auditoria(id_auditoria)
        self.detalle_cambios = d.pop("cambios", [])
        self.detalle = d
        self.detalle_abierto = True

    @rx.event
    def cerrar_detalle(self):
        self.detalle_abierto = False
        self.detalle = {}
        self.detalle_cambios = []
