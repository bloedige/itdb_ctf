"""Estado de apoyo para las barras de navegación.

- `perfil_min`: alias / correo / iniciales del usuario en sesión para el botón de
  perfil (hace una consulta por lectura, igual que `AuthState.codigo_rol`).
- `menu_movil`: abre/cierra el drawer responsive de las tres barras.
"""

import reflex as rx
from sqlmodel import Session

from itdb_ctf.auth.auth_state import AuthState
from itdb_ctf.db import engine
from itdb_ctf.models import Usuario

_VACIO = {"alias": "", "email": "", "iniciales": "", "nombre": ""}


class NavState(AuthState):
    menu_movil: bool = False

    @rx.var
    def perfil_min(self) -> dict:
        if not self.autenticado:
            return _VACIO
        with Session(engine) as s:
            u = s.get(Usuario, self.id_usuario)
            if not u:
                return _VACIO
            alias = (u.alias or "").strip()
            nombre = f"{u.nombre} {u.paterno}".strip()
            if alias:
                iniciales = alias[:2].upper()
            else:
                iniciales = ((u.nombre[:1] or "") + (u.paterno[:1] or "")).upper()
            return {
                "alias": alias or nombre,
                "email": u.email_inst,
                "iniciales": iniciales or "?",
                "nombre": nombre or alias,
            }

    @rx.event
    def toggle_menu(self):
        self.menu_movil = not self.menu_movil

    @rx.event
    def cerrar_menu(self):
        self.menu_movil = False
