from sqlmodel import select,Session
from itdb_ctf.db import engine
from itdb_ctf.models import Evento, Resuelve, Contiene, Reto, EstadoInscripcion, Participa
from itdb_ctf.core.puntaje_logic import refrescar_puntaje
from itdb_ctf.utils.security import flag_hasher
from itdb_ctf.asociar.asociar_logic import estado_evento

def enviar_flag(id_usuario:int, id_reto:int, id_evento:int, flag_enviada:str, dir_ip:str |None=None ) -> tuple[bool,str]:
    with Session(engine) as s :
        reto = s.get(Reto,id_reto)
        if not reto or not reto.activo:
            return False, "Reto no disponible."
        cont = s.exec(select(Contiene).where(Contiene.id_reto==id_reto,Contiene.id_evento==id_evento)).first()
        if not cont:
            return False, "El reto no pertenece a este evento."
        ev = s.get(Evento, id_evento)
        if not ev:
            return False, "Evento no disponible."
        est_evento = estado_evento(ev)
        if estado_evento == "futuro":
            return False, "El evento aún no ha iniciado."
        if estado_evento == "concluido":
            return False, "El evento ha finalizado."
        # --- El usuario debe estar INSCRITO en el evento
        est_inscrito = s.exec(select(EstadoInscripcion.id_estado_inscripcion).where(EstadoInscripcion.etiqueta=="inscrito")).first()
        inscrito = s.exec(select(Participa).where(
            Participa.id_usuario==id_usuario,
            Participa.id_evento==id_evento,
            Participa.id_estado_inscripcion==est_inscrito,
        )).first()
        if not inscrito:
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
        s.add(Resuelve(
            id_usuario=id_usuario,
            id_evento=id_evento,
            id_reto=id_reto,
            flag_correcta=correcta,
            dir_ip=dir_ip,
        )) 
        if correcta:
            s.flush()
            refrescar_puntaje(s, id_reto, id_evento)
            s.commit()
            return True, "¡Flag correcta!"
        s.commit()
        return False, "Flag incorrecta."