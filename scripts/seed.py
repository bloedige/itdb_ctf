import os
from dotenv import load_dotenv
from sqlmodel import select, create_engine,Session
from itdb_ctf.models import (Rol,Categoria,Dificultad,Modalidad,ModoPuntaje,MetodoAuth,EstadoInscripcion,EstadoWriteup)

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

ROLES=[
    ("superadmin","super administrador"),
    ("admin","administrador"),
    ("autor","autor de retos"),
    ("user","estudiante")
    ]
MODOS_PUNTAJE = ["estatico", "dinamico"]
MODALIDADES = ["abierto", "cerrado"]
DIFICULTADES = ["Fácil", "Media", "Difícil"]
CATEGORIAS = ["Web", "Forensics", "Crypto", "Reversing", "Pwn", "OSINT", "Misc"]
ESTADOS_WRITEUP = ["borrador", "pendiente", "aprobado", "rechazado"]
ESTADOS_INSCR = ["inscrito", "invitado", "aceptado", "rechazado"]
METODOS_AUTH = ["google", "local"]

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

# ==========================================================================
#  ADMIN SEMILLA + EVENTO ABIERTO
## ==========================================================================
## Como resuelve.id_evento y compra.id_evento son OBLIGATORIOS, el evento abierto
## debe existir antes del primer envio. Y un evento necesita un creador (usuario),
## por eso primero creamos un admin semilla.
#
#ADMIN_SEED_EMAIL = "admin@donbosco.edu.bo"      # << CAMBIA esto al correo real
#
#EVENTO_ABIERTO_TITULO = "CTF Abierto Don Bosco"
#EVENTO_ABIERTO_DESC = (
#    "Evento de practica libre y permanente. Modalidad abierta, sin fecha de fin. "
#    "Todo miembro autenticado puede resolver retos aqui."
#)
#
#
#def sembrar_admin_y_evento(session):
#    """Crea el usuario admin semilla y el evento abierto permanente."""
#
#    # Buscamos el rol 'admin' y el metodo 'google' que ya sembramos arriba.
#    # .one() obliga a que exista exactamente uno (si no, lanza error: util para detectar problemas).
#    rol_admin = session.exec(select(Rol).where(Rol.codigo == "admin")).one()
#    metodo_google = session.exec(
#        select(MetodoAuth).where(MetodoAuth.etiqueta == "google")
#    ).one()
#
#    # Creamos (o recuperamos) el admin, identificado por su correo.
#    admin = get_or_create(
#        session, Usuario,
#        {"email_inst": ADMIN_SEED_EMAIL},        # filtro: si ya existe este correo, no duplica
#        {                                        # valores solo para cuando se crea:
#            "id_rol": rol_admin.id_rol,
#            "id_metodo_auth": metodo_google.id_metodo_auth,
#            "nombre": "Administrador",
#            "paterno": "Sistema",
#            "alias": "admin",
#        },
#    )
#
#    # Buscamos la modalidad 'abierto' y el modo de puntaje para el evento.
#    modalidad_abierto = session.exec(
#        select(Modalidad).where(Modalidad.etiqueta == "abierto")
#    ).one()
#    modo_estatico = session.exec(
#        select(ModoPuntaje).where(ModoPuntaje.etiqueta == "estatico")
#    ).one()
#
#    # Creamos (o recuperamos) el evento abierto, identificado por su titulo.
#    get_or_create(
#        session, Evento,
#        {"titulo": EVENTO_ABIERTO_TITULO},
#        {
#            "id_usuario": admin.id_usuario,              # el creador es el admin
#            "id_modalidad": modalidad_abierto.id_modalidad,
#            "id_modo_puntaje": modo_estatico.id_modo_puntaje,
#            "descripcion": EVENTO_ABIERTO_DESC,
#            "fec_inicio": datetime.now(timezone.utc),
#            "fec_fin": None,                             # None = permanente, sin fin
#        },
#    )
#
#
# ==========================================================================
#  EJECUCION
# ==========================================================================

def main():
    with Session(engine) as lm:
        sembrar_catalogos(lm)                   # 1. los 8 catalogos
        # sembrar_admin_y_evento(session)       # 2. admin + evento abierto
        lm.commit()                             # 3. guardar TODO de golpe
    print("seed catalogos implementados")
# Esto hace que main() se ejecute solo si corres el archivo directamente
# (python scripts/seed.py), pero no si alguien lo importa.
if __name__ == "__main__":
    main()