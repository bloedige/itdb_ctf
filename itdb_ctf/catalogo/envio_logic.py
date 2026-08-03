from sqlmodel import select,Session
from itdb_ctf.db import engine
from itdb_ctf.models import Resuelve,Contiene,Reto,EstadoInscripcion,Participa
from itdb_ctf.catalogo.puntaje_logic import calcular_puntaje
from itdb_ctf.utils.security import flag_hasher

def enviar_flag(id_usuario:int, id_reto:int, id_evento:int, flag_enviada:str, dir_ip:str |None=None ) -> tuple[bool,str]:
    with Session(engine) as s :
        reto = s.get(Reto,id_reto)
        if not reto or not reto.activo:
            return False, "Reto no disponible"
        cont = s.exec(select(Contiene).where(Contiene.id_reto==id_reto,Contiene.id_evento==id_evento)).first()
        if not cont:
            return False, "El reto no pertenece a este evento"
        # --- El usuario debe estar ACEPTADO en el evento
        est_aceptado = s.exec(select(EstadoInscripcion.id_estado_inscripcion).where(EstadoInscripcion.etiqueta=="inscrito")).first()
        aceptado = s.exec(select(Participa).where(
            Participa.id_usuario==id_usuario,
            Participa.id_evento==id_evento,
            Participa.id_estado_inscripcion==est_aceptado,
        )).first()
        if not aceptado:
            return False, "No estás inscrito en este evento."
        # --- Anti-resubmit
        resuelto = s.exec(select(Resuelve).where(
            Resuelve.id_usuario==id_usuario,
            Resuelve.id_evento==id_evento,
            Resuelve.id_reto==id_reto,
            Resuelve.flag_correcta==True,
        )).first()
        if resuelto:
            return False, "El reto ah sido resuelto."
        correcta=flag_hasher.verificar(flag_enviada,reto.flag)
        puntos = calcular_puntaje(s,id_reto,id_evento) if correcta else 0
        s.add(Resuelve(
            id_usuario=id_usuario,
            id_evento=id_evento,
            id_reto=id_reto,
            flag_correcta=correcta,
            puntos=puntos,
            dir_ip=dir_ip,
        )) 
        s.commit()
        if correcta:
            return True, "¡Flag correcta!"
        return False, "Flag incorrecta."