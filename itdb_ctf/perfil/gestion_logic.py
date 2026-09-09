"""Autogestión del perfil: el usuario edita sus propios datos.

- `user` (estudiante), `admin`, `superadmin`: solo `alias`.
- `autor`: además `nombre` / `paterno` / `materno` (admin/superadmin gestionan sus
  datos desde `/admin/usuarios`).

A diferencia de `usuario.usuario_logic` (gestión de admin, solo cuentas locales),
esto no restringe por método de autenticación: un usuario Google también cambia su
alias/nombre. El alias es único case-insensitive (ver índice `uq_usuario_alias_lower`).
"""

from sqlmodel import Session, select
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from itdb_ctf.db import engine
from itdb_ctf.models import Usuario
from itdb_ctf.perfil.moderacion_logic import validar_alias, validar_nombre

# Solo el autor edita su nombre real desde aquí.
ROLES_NOMBRE = {"autor"}


def datos_actuales(id_usuario: int | None) -> dict:
    """Valores actuales para poblar el formulario (strings, nunca None)."""
    if not id_usuario:
        return {"alias": "", "nombre": "", "paterno": "", "materno": ""}
    with Session(engine) as s:
        u = s.get(Usuario, id_usuario)
        if not u:
            return {"alias": "", "nombre": "", "paterno": "", "materno": ""}
        return {
            "alias": u.alias or "",
            "nombre": u.nombre or "",
            "paterno": u.paterno or "",
            "materno": u.materno or "",
        }


def alias_en_uso(alias: str, id_usuario: int) -> bool:
    with Session(engine) as s:
        fila = s.exec(
            select(Usuario.id_usuario).where(
                func.lower(Usuario.alias) == alias.lower(),
                Usuario.id_usuario != id_usuario,
            )
        ).first()
    return fila is not None


def actualizar_perfil(
    id_usuario: int | None,
    codigo_rol: str,
    alias: str,
    nombre: str = "",
    paterno: str = "",
    materno: str = "",
) -> tuple[bool, str]:
    if not id_usuario:
        return False, "Sesión no válida."

    ok, val_alias = validar_alias(alias)
    if not ok:
        return False, val_alias
    if alias_en_uso(val_alias, id_usuario):
        return False, "Ese alias ya está en uso."

    campos_nombre: dict[str, str | None] = {}
    if codigo_rol in ROLES_NOMBRE:
        ok, val_nombre = validar_nombre(nombre, "nombre", obligatorio=True)
        if not ok:
            return False, val_nombre
        ok, val_paterno = validar_nombre(paterno, "apellido paterno", obligatorio=True)
        if not ok:
            return False, val_paterno
        ok, val_materno = validar_nombre(materno, "apellido materno", obligatorio=False)
        if not ok:
            return False, val_materno
        campos_nombre = {
            "nombre": val_nombre,
            "paterno": val_paterno,
            "materno": val_materno or None,
        }

    with Session(engine) as s:
        u = s.get(Usuario, id_usuario)
        if not u:
            return False, "Usuario inexistente."
        u.alias = val_alias
        for campo, valor in campos_nombre.items():
            setattr(u, campo, valor)
        s.add(u)
        try:
            s.commit()
        except IntegrityError:
            s.rollback()
            return False, "Ese alias ya está en uso."
    return True, "Datos actualizados."
