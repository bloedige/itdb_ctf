import reflex as rx
from datetime import datetime, timezone
from itdb_ctf.auth.auth_state import AuthState
from itdb_ctf.utils.fechas import a_local
from itdb_ctf.auto_inscripcion.auto_inscripcion_evento_logic import auto_inscripcion, eventos
from itdb_ctf.websockets import canales, suscriptor
from itdb_ctf.websockets.suscriptor import SuscriptorMixin

class AutoInscripcionState(SuscriptorMixin, AuthState):
    eventos:list[dict] = []
    ahora:datetime = datetime.now(timezone.utc)

    @rx.event
    def actualizar_tiempo(self):
        self.ahora = datetime.now(timezone.utc)

    @rx.event(background=True)
    async def escuchar_eventos(self):
        await suscriptor.escuchar(
            self,
            clave_getter=lambda s: "eventos",
            canales_getter=lambda s: [canales.CH_EVENTOS],
            recargar=lambda s: s.cargar_eventos(),
        )

    @rx.event
    def parar_eventos(self):
        self.streaming = False
        
    @rx.event
    def cargar_eventos(self):
        guard = self.requiere_login()
        if guard: return guard
        self.eventos = eventos(self.id_usuario)


    @rx.event
    def cofirmar_inscrito(self, id_evento:int):
        guard = self.requiere_login()
        if guard: return guard
        if self.codigo_rol != "user":
            return rx.toast.error("Solo estudiantes pueden participar en los eventos.")
        ok, msg = auto_inscripcion(id_evento, self.id_usuario)
        if not ok:
            return rx.toast.error(msg)
        self.cargar_eventos()
        return rx.toast.success(msg)
    
    @rx.var
    def eventos_procesados(self) -> list[dict]:
        resultado = []
        for ev in self.eventos:
            item = dict(ev)
            if ev['estado_evento'] != "abierto":   
                fi = ev["fec_inicio"]
                ff = ev["fec_fin"]
                if isinstance(fi, str):
                    fi = datetime.fromisoformat(fi)
                if isinstance(ff, str):
                    ff = datetime.fromisoformat(ff)
                item["fi_str"] = a_local(fi).strftime("%d-%m-%y %H:%M")if fi else "" 
                item["ff_str"] = a_local(ff).strftime("%d-%m-%y %H:%M")if ff else "" 
                hh, rt = divmod(int((ff - fi).total_seconds()), 3600)
                item["duracion"] = f"{hh} Hrs."
                if self.ahora < fi:
                    rest = int((fi - self.ahora).total_seconds())
                    dias, rest = divmod(rest, 86400)
                    if dias > 0:
                        item["contador_inicio"] = (f"{dias} día{'s' if dias != 1 else ''}")
                    else:
                        hrs, rest = divmod(rest, 3600)
                        mins, seg = divmod(rest, 60)
                        item["contador_inicio"] = f"{hrs:02d}:{mins:02d}:{seg:02d}"
                elif fi <= self.ahora < ff:
                    rest = int((ff - self.ahora).total_seconds())
                    hrs, rest = divmod(rest, 3600)
                    mins, seg = divmod(rest, 60)
                    item["contador_fin"] = f"{hrs:02d}:{mins:02d}:{seg:02d}"

            resultado.append(item)

        activos = [e for e in resultado if e["estado_evento"] == "activo"]
        futuros = [e for e in resultado if e["estado_evento"] == "futuro"]
        pasados = [e for e in resultado if e["estado_evento"] == "concluido"]
        
        futuros.sort(key=lambda e: e["fec_inicio"])
        pasados.sort(key=lambda e: e["fec_fin"], reverse=True)

        return activos + futuros + pasados