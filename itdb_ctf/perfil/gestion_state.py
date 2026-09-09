import reflex as rx

from itdb_ctf.auth.auth_state import AuthState
from itdb_ctf.components.form import toast_msg, success_msg
from itdb_ctf.perfil.perfil_state import PerfilGeneralState
from itdb_ctf.perfil.gestion_logic import datos_actuales, actualizar_perfil, ROLES_NOMBRE


class PerfilGestionState(AuthState):
    abierto: bool = False
    alias: str = ""
    nombre: str = ""
    paterno: str = ""
    materno: str = ""
    mensaje: str = ""

    @rx.var
    def edita_nombre(self) -> bool:
        return self.codigo_rol in ROLES_NOMBRE

    def set_alias(self, v: str):
        self.alias = v

    def set_nombre(self, v: str):
        self.nombre = v

    def set_paterno(self, v: str):
        self.paterno = v

    def set_materno(self, v: str):
        self.materno = v

    def set_abierto(self, v: bool):
        self.abierto = v
        if not v:
            self.mensaje = ""

    def _cargar_datos(self):
        d = datos_actuales(self.id_usuario)
        self.alias = d["alias"]
        self.nombre = d["nombre"]
        self.paterno = d["paterno"]
        self.materno = d["materno"]
        self.mensaje = ""

    @rx.event
    def abrir(self):
        guard = self.requiere_login()
        if guard:
            return guard
        self._cargar_datos()
        self.abierto = True

    @rx.event
    def cerrar(self):
        self.abierto = False
        self.mensaje = ""

    @rx.event
    def guardar(self):
        guard = self.requiere_login()
        if guard:
            return guard
        ok, msg = actualizar_perfil(
            self.id_usuario,
            self.codigo_rol,
            self.alias,
            self.nombre,
            self.paterno,
            self.materno,
        )
        if not ok:
            self.mensaje = msg
            return toast_msg(msg)
        self.mensaje = ""
        self.abierto = False
        # Refresca la tarjeta de perfil en el sitio (sin recargar la página, que
        # producía un "brinco" al cerrar el diálogo).
        return [success_msg("Datos actualizados."), PerfilGeneralState.cargar_perfil]
