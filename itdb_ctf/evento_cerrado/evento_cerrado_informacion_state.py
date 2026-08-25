import reflex as rx
from datetime import datetime, timezone
from itdb_ctf.auth.auth_state import AuthState
from itdb_ctf.evento_cerrado.evento_cerrado_logic import info_evento_cerrado

class EventoCerradoInfromacionState(AuthState):
    id_cerrado:int = 0
    encontrado:bool = False
    titulo:str = ""
    desripcion:str = ""
    estado_evento:str = ""
    fi_str:str = ""
    ff_str:str = ""

    final:datetime | None=None

    @rx.event
    def cargar_info(self):
        guard = self.requiere_login()
        if guard: return guard
        self.id_cerrado = int(self.router.page.params.get("id_evento_cerrado", 0))
        info = info_evento_cerrado(self.id_cerrado)
        if not info:
            self.encontrado = False
            return 
        self.encontrado = True
        self.titulo = info['titulo']
        self.desripcion = info['descripcion']
        self.estado_evento = info['estado_evento']
        self.final = info['fec_fin']
        tz_local = datetime.now().astimezone().tzinfo
        fi, ff = info['fec_inicio'], info['fec_fin']
        self.fi_str = fi.astimezone(tz_local).strftime("%d-%m-%y %H:%M")if fi else ""
        self.ff_str = ff.astimezone(tz_local).strftime("%d-%m-%y %H:%M")if ff else ""


class EventoCerradoContadorRegresivoFinalState(AuthState):
    ahora:datetime = datetime.now(timezone.utc)
    #contador_regresivo:str = ""
    
    @rx.event
    def actualizar_tiempo(self):
        self.ahora = datetime.now(timezone.utc)
        #info = self.get_state(EventoCerradoInfromacionState)
        #final = info.final
        #if not final:
        #    return "00:00:00"
        #if isinstance(final, str):
        #    final = datetime.fromisoformat(final)
        #if final.tzinfo is None:
        #    final = final.replace(tzinfo=timezone.utc)
        #if self.ahora >= final:
        #    return "00:00:00"
        #else:
        #    rest = int((final - self.ahora).total_seconds())
        #    hrs, rest = divmod(rest, 3600)
        #    mins, seg = divmod(rest, 60)      
        #    self.contador_regresivo = f"{hrs:02d}:{mins:02d}:{seg:02d}"
    @rx.var
    async def contador_regresivo(self) -> str:
        info = await self.get_state(EventoCerradoInfromacionState)
        final = info.final
        if not final:
            return "00:00:00"
        if isinstance(final, str):
            final = datetime.fromisoformat(final)
        if final.tzinfo is None:
            final = final.replace(tzinfo=timezone.utc)
        if self.ahora >= final:
            return "00:00:00"
        rest = int((final - self.ahora).total_seconds())
        hrs, rest = divmod(rest, 3600)
        mins, seg = divmod(rest, 60)      
        return f"{hrs:02d}:{mins:02d}:{seg:02d}"

