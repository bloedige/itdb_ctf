from sqlmodel import Session, select
from itdb_ctf.db import engine
from itdb_ctf.models import Usuario, MetodoAuth
from itdb_ctf.utils.security import hasher

def verificar_credenciales(email:str, password:str) -> Usuario |None:
    with Session(engine) as s:
        metodo_auth = s.exec(select(MetodoAuth).where(MetodoAuth.etiqueta=="local")).one()
        usuario = s.exec(select(Usuario).where(Usuario.email_inst==email, Usuario.id_metodo_auth == metodo_auth.id_metodo_auth)).first()

        if not usuario or not usuario.password_hash:
            return None
        if hasher.verificar(password, usuario.password_hash):
            return usuario
        return None