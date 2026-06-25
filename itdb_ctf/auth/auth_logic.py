import os 
from sqlmodel import Session, select
from ..db import engine
from ..models import Usuario,Rol, MetodoAuth,Evento,Modalidad,EstadoInscripcion,Participa

DOMINIO=os.environ["ALLOWED_EMAIL_DOMAIN"]
titulo=os.environ.get("EVENTO_ABIERTO_TITULO", "Plataforma ITDB - Práctica Libre CTF")

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
    
def auto_incripcion_evento_abierto(session,id_usuario:int):
    etiqueta =session.exec(select(Modalidad).where(Modalidad.etiqueta=="abierto")).one()
    evento = session.exec(select(Evento).where(Evento.titulo==titulo)).first() or session.exec(select(Evento).where(Evento.id_evento==1 and Evento.id_modalidad==etiqueta.id_modalidad)).first()
    if not evento:
        return
    estado = session.exec(select(EstadoInscripcion).where(EstadoInscripcion.etiqueta=="aceptado")).first()
    if not estado:
        return
    participa = session.exec(select(Participa).where(
        Participa.id_usuario==id_usuario,
        Participa.id_evento==evento.id_evento,  
    )).first()
    if not participa:
        session.add(Participa(
            id_usuario=id_usuario,
            id_evento=evento.id_evento,
            id_estado_inscripcion=estado.id_estado_inscripcion,
        ))

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
        s.flush()
        auto_incripcion_evento_abierto(s,usuario.id_usuario)
        s.commit()
        s.refresh(usuario)

        return usuario