import secrets
from sqlmodel import select, Session
from itdb_ctf.db import engine
from itdb_ctf.models import Rol, Usuario, MetodoAuth
from itdb_ctf.utils.security import hasher
from itdb_ctf.auth.auth_logic import auto_incripcion_evento_abierto

RANGO={"superadmin":3, "admin":2, "autor":1, "user":0}

def generar_password() -> str:
    return secrets.token_hex(8)

def id_rol_cod(id_rol:int) -> str:
    with Session(engine) as s:
        rol = s.get(Rol, id_rol)
        return rol.codigo if rol else ""
    
def id_rol_eti(id_rol:int) -> str:
    with Session(engine) as s:
        rol = s.get(Rol, id_rol)
        return rol.etiqueta if rol else ""

def existe_email(email:str, ex_id:int | None=None) -> bool:
    with Session(engine) as s:
        stmt = (select(Usuario).where(Usuario.email_inst == email))
        if ex_id:
            stmt= stmt.where(Usuario.id_usuario != ex_id)
        return s.exec(stmt).first() is not None
    
def obtener_usuario(id_usuario:int):
    with Session(engine) as s:
        return s.get(Usuario, id_usuario)
    
def roles_asignables(cod_rol:str) -> list[tuple[str,str]]:
    with Session(engine) as s:
        roles = []
        for r in s.exec(select(Rol)).all():
            if cod_rol == "superadmin" or RANGO.get(r.codigo,-1) < RANGO.get(cod_rol,-1):
                roles.append((str(r.id_rol), r.etiqueta))
        return roles


def puede_gestionar(id_target:int, id_actor:int, cod_actor:str, accion:str) -> tuple[bool, str]:
    #Regla unica. accion: 'datos' | 'reset' | 'estado'.
    #Sobre uno mismo: solo 'datos' (editar lo propio).
    #Sobre otros: solo si tu rango es ESTRICTAMENTE mayor (no semejantes).
     if id_target == id_actor:
        if accion == "datos":
            return True, ""
        return False, "Acción no valida"
     with Session(engine)  as s:
         target = s.get(Usuario, id_target)
         if not target:
             return False, "Usuario inexistente"
         cod_target = id_rol_cod(id_target)
         if RANGO.get(cod_actor, -1) > RANGO.get(cod_target, -1):
             return True, ""
         return False, "Acción no valida"

# ---------- CREAR ----------

def validar_crear_cuenta(email:str, id_rol:int, cod_rol:str) -> tuple[bool,str]:
    if existe_email(email):
        return False, "Ya existe una cuenta vinculada a este correo"
    codigo = id_rol_cod(id_rol)
    if not codigo:
        return False, "Rol no existente"
    

    if cod_rol != "superadmin" and RANGO.get(codigo) >= RANGO.get(cod_rol, -1):
        return False, f"Creacion invalida para {codigo}"
    return True, ""

def crear_cuenta(nombre:str, paterno:str, materno:str, alias:str, email:str, id_rol:int, cod_rol:str) -> str:
    ok, msg = validar_crear_cuenta(email, id_rol, cod_rol)
    if not ok:
        raise ValueError(msg)
    with Session(engine) as s:
        metodo = s.exec(select(MetodoAuth).where(MetodoAuth.etiqueta == "local")).first()
        if not metodo:
            raise ValueError("metodo de autenticacio no configuarado")
        password = generar_password()
        user = Usuario(
            id_rol=id_rol,
            id_metodo_auth=metodo.id_metodo_auth,
            nombre=nombre,
            paterno=paterno,
            materno=materno or None,
            alias=alias or None,
            email_inst=email,
            password_hash=hasher.hashear(password)
        )
        s.add(user)
        s.flush()
        auto_incripcion_evento_abierto(s, user.id_usuario)
        s.commit()
        return password
    
# ---------- EDITAR ----------
    
def validar_editar_usuario(id_usuario:int, email:str, id_actor:int, cod_actor:str ) -> tuple[bool,str]:
    ok, msg = puede_gestionar(id_usuario, id_actor, cod_actor, "datos")
    if not ok:
        return False, msg
    with Session(engine) as s:
        user = s.get(Usuario, id_usuario)
        if not user:
            return False, "Usuario inexistente"
        metodo = s.get(MetodoAuth, user.id_metodo_auth)
        if not metodo or metodo.etiqueta != "local":
            return False, "Solo se puede editar cunetas locales"
        if existe_email(email, id_usuario):
            return False , "Correo vinculado a otra cuenta"
        return True, ""
    
def editar_usuario(id_usuario:int, values:dict, id_actor:int, cod_actor:int):
    ok, msg = validar_editar_usuario(id_usuario, values.get("email_inst",""), id_actor, cod_actor)
    if not ok:
        raise ValueError(msg)
    with Session(engine) as s:
        user = s.get(Usuario, id_usuario)
        if not user:
            return False
        for campo,  valor in values.items():
            setattr(user, campo, valor)
        s.add(user)
        s.commit()
        return True

# ---------- LISTAR ---------- 
def listar_usuarios(busqueda:str | None=None, id_rol:int | None= None, id_metodo:int | None=None, activo:bool | None=None, id_actor:int |None= None, cod_actor:str=""):
    with Session(engine) as s:
        stmt = (select(Usuario, Rol.etiqueta, Rol.codigo, MetodoAuth.etiqueta)
        .join(Rol, Usuario.id_rol == Rol.id_rol)
        .join(MetodoAuth, Usuario.id_metodo_auth == MetodoAuth.id_metodo_auth)
        .order_by(Rol.id_rol)
        .order_by(MetodoAuth.id_metodo_auth.desc()))

        if id_rol:
            stmt = stmt.where(Usuario.id_rol == id_rol)
        if id_metodo:
            stmt = stmt.where(Usuario.id_metodo_auth == id_metodo)
        if activo is not None:
            stmt = stmt.where(Usuario.activo == activo)
        if busqueda:
            patron = f"%{busqueda}%"
            stmt = stmt.where(Usuario.email_inst.ilike(patron) | Usuario.alias.ilike(patron)
                            | Usuario.nombre.ilike(patron) | Usuario.paterno.ilike(patron))
        filas = s.exec(stmt).all()
    
    rango_actor = RANGO.get(cod_actor, -1)
    resultado=[]
    
    for u, eti, cod, met in filas:
        rango_target = RANGO.get(cod,-1)
        if rango_target > rango_actor:
            continue
        gest = rango_actor > rango_target
        mismo = u.id_usuario == id_actor
        local = met == "local"
        resultado.append({
            "id_usuario":u.id_usuario,
            "nombre": f"{u.nombre} {u.paterno}",
            "alias":u.alias if u.alias else "---",
            "email_inst":u.email_inst,
            "id_rol":u.id_rol,
            "rol":eti,
            "codigo":cod,
            "metodo":met,
            "activo":u.activo,
            "mismo":mismo,
            "edit":local and (gest or mismo),
            "reset":local and gest,
            "estado":gest,
        })
    return resultado

# ---------- ESTADO ----------
    
def validar_activar_desactivar(id_usuario:int, id_actor:int, cod_actor:str) -> tuple[bool,str]:
    return puede_gestionar(id_usuario,id_actor,cod_actor, "estado")

def activar_desactivar(id_usuario:int, id_actor:int, cod_actor:str):
    ok, msg = validar_activar_desactivar(id_usuario,id_actor , cod_actor)
    if not ok:
        raise ValueError(msg)
    with Session(engine) as s:
        user = s.get(Usuario, id_usuario)
        if not user:
            return False
        user.activo = not user.activo
        s.add(user)
        s.commit()
        return True
    
# ---------- PASSWORD ----------

def validar_reset_password(id_usuario:int, id_actor:int, cod_actor:str) -> tuple[bool, str]:
    ok, msg = puede_gestionar(id_usuario,id_actor,cod_actor,"reset")
    if not ok:
        raise ValueError(msg)
    
    with Session(engine) as s:
        user = s.get(Usuario, id_usuario)
        if not user:
            return False, "Usuario inexistente"
        metodo = s.get(MetodoAuth, user.id_metodo_auth)
        if not metodo or metodo.etiqueta != "local":
            return False, "Solo se restablece contraseñas de cuentas locales"
        return True , ""
    
def reset_password(id_usuario:int, id_actor:int, cod_actor:str) -> str:
    ok, msg = validar_reset_password(id_usuario,id_actor,cod_actor)
    if not ok:
        raise ValueError(msg)
    with Session(engine) as s:
        user = s.get(Usuario, id_usuario)
        password = generar_password()
        user.password_hash = hasher.hashear(password)
        s.add(user)
        s.commit()
        return password