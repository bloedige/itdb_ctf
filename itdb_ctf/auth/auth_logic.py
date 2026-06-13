import os 
from sqlmodel import Session, select
from ..db import engine
from ..models import Usuario,Rol, MetodoAuth

DOMINIO=os.environ["ALLOWED_EMAIL_DOMAIN"]

class DominiNoPermitido(Exception):
    """El correo no pertenece al dominio institucional."""
def validar_dominio (email: str) -> None:
    if not email.lower().endswith("@"+DOMINIO.lower()):
        raise DominiNoPermitido(email)
    
def separar_apellidos(family_name: str | None) -> tuple[str, str|None]:
    if not family_name:
        return "",None
    partes = family_name.split()
    paterno = partes[0]
    materno = " ".join(partes[1:]) if len(partes) > 1 else None
    return paterno, materno
    
    
def obtener_crear_usuario(info: dict) -> Usuario:
    email = info["email"] #porque  es una lista 
    validar_dominio(email)

    with Session(engine) as s:
        usuario = s.exec(select(Usuario).where(Usuario.email_inst==email)).first()
        if usuario:
            return usuario
        rol = s.exec(select(Rol).where(Rol.codigo=="user")).one()
        metodo = s.exec(select(MetodoAuth).where(MetodoAuth.etiqueta=="google")).one()
        
        paterno, materno = separar_apellidos(info.get("family_name"))
            
        usuario = Usuario(
            id_rol=rol.id_rol,
            id_metodo_auth=metodo.id_metodo_auth,
            nombre=info.get("given_name", ""),
            paterno=paterno,
            materno=materno,
            alias=info.get("name",email.split("@")[0])[:30],
            email_inst=email,
        )

        s.add(usuario)
        s.commit()
        s.refresh(usuario)

        return usuario