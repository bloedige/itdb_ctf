import os
from dotenv import load_dotenv
from sqlmodel import select, create_engine,Session
from itdb_ctf.models import (Rol,Categoria,Dificultad,Modalidad,ModoPuntaje,MetodoAuth,EstadoInscripcion,EstadoWriteup,Usuario,)
from itdb_ctf.utils.security import hasher

load_dotenv()
DATABASE_URL=os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL)

def get_or_create(session,modelo,filtro:dict,valores:dict | None=None):
    # Construir la consulta de búsqueda
    stmt=select(modelo)
    for campo , valor in filtro.items():
        stmt = stmt.where(getattr(modelo,campo)==valor)
    # Buscar si ya existe
    existente=session.exec(stmt).first()
    if not existente:
    # Crear el registro porque no existe
        obj = modelo(**filtro,**(valores or {}))
        session.add(obj)
        session.flush()
        return obj
    return existente


#---Catalogo---

ROLES= [("superadmin","super administrador"),
        ("admin","administrador"),
        ("autor","autor de retos"),
        ("user","estudiante")]
        
METODOS_AUTH = ["google", "local"]
MODOS_PUNTAJE = ["estatico", "dinamico"]
MODALIDADES = ["abierto", "cerrado"]
DIFICULTADES = ["Fácil", "Media", "Difícil"]
CATEGORIAS = ["Web", "Forensics", "Crypto", "Reversing", "Pwn", "OSINT", "Misc"]
ESTADOS_WRITEUP = ["borrador", "pendiente", "aprobado", "rechazado"]
ESTADOS_INSCR = ["inscrito", "invitado", "aceptado", "rechazado"]


def sembrar_catalogos(session):
    catalogos=[
        (ModoPuntaje,MODOS_PUNTAJE),
        (Modalidad,MODALIDADES),
        (Dificultad,DIFICULTADES),
        (Categoria,CATEGORIAS),
        (EstadoWriteup,ESTADOS_WRITEUP),
        (EstadoInscripcion,ESTADOS_INSCR),
        (MetodoAuth,METODOS_AUTH),
    ]

    for codigo, etiqueta in ROLES:
        get_or_create(session,Rol,{"codigo":codigo},{"etiqueta":etiqueta})

    for modelo, datos in catalogos:
        for et in datos:
            get_or_create(session,modelo,{"etiqueta":et})

#---Creacion superadmin---

EMAIL_SEED = os.environ["SUPERADMIN_ITDB"]
ALIAS_SEED= os.environ["SUPERADMIN_ITDB_ALIAS"]
PW_SEED= os.environ["SUPERADMIN_ITDB_PASS"]     

def sembrar_superadmin(session):
   
    rol = session.exec(select(Rol).where(Rol.codigo == "superadmin")).one()
    metodo_auth = session.exec(select(MetodoAuth).where(MetodoAuth.etiqueta == "local")).one()

    # Creamos (o recuperamos), identificando por su correo.
    admin = get_or_create(
        session,Usuario,
        {"email_inst": EMAIL_SEED},        # filtro: si ya existe este correo, no duplica
        {                                        # valores solo para cuando se crea:
            "id_rol": rol.id_rol,
            "id_metodo_auth": metodo_auth.id_metodo_auth,
            "nombre": "ITDB",
            "paterno": "Sistema",
            "password_hash": hasher.hashear(PW_SEED),
            "alias": ALIAS_SEED,
        },
    )

#####-----    # Buscamos la modalidad 'abierto' y el modo de puntaje para el evento.
#####-----    modalidad_abierto = session.exec(        select(Modalidad).where(Modalidad.etiqueta == "abierto")).one()
#####-----    modo_estatico = session.exec(select(ModoPuntaje).where(ModoPuntaje.etiqueta == "estatico")).one()
#####-----
#####-----    # Creamos (o recuperamos) el evento abierto, identificado por su titulo.
#####-----    get_or_create(
#####-----        session, Evento,
#####-----        {"titulo": EVENTO_ABIERTO_TITULO},
#####-----        {
#####-----            "id_usuario": admin.id_usuario,              # el creador es el admin
#####-----            "id_modalidad": modalidad_abierto.id_modalidad,
#####-----            "id_modo_puntaje": modo_estatico.id_modo_puntaje,
#####-----            "descripcion": EVENTO_ABIERTO_DESC,
#####-----            "fec_inicio": datetime.now(timezone.utc),
#####-----            "fec_fin": None,                             # None = permanente, sin fin
#####-----        },
#####-----    )
#####-----

 #==========================================================================
 # EJECUCION
 #==========================================================================

def main():
    with Session(engine) as lm:
        sembrar_catalogos(lm)  
        sembrar_superadmin(lm)                 
        # sembrar_admin_y_evento(session)       
        lm.commit()                             
    print("seed catalogos implementados")
# Esto hace que main() se ejecute solo si corres el archivo directamente
# (python scripts/seed.py), pero no si alguien lo importa.
if __name__ == "__main__":
    main()