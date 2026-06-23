from sqlmodel import select,Session
from itdb_ctf.db import engine
from itdb_ctf.models import Resuelve,Contiene,Evento,Reto
from itdb_ctf.retos.puntaje_logic import calcular_puntaje
from itdb_ctf.utils.security import flag_hasher


def enviar_flag(id_usuario:int, id_reto:int, id_evento:int, flag_enviada:str, dir_ip:str |None=None )->dict:
    with Session(engine) as s :
        reto = s.get(Reto,id_reto)
        if not reto or not reto.activo:
            return{"ok": False, "msg":"Reto no disponible"}
        
        rel = s.exec(select(Contiene).where(Contiene.id_reto==id_reto,Contiene.id_evento==id_evento)).first()

        if not rel:
            return {"ok":False, "msg":"El reto no pertenece a este evento"}


        resuelto = s.exec(select(Resuelve).where(
            Resuelve.id_usuario==id_usuario,
            Resuelve.id_evento==id_evento,
            Resuelve.id_reto==id_reto,
            Resuelve.flag_correcta==True,
        )).first()

        if resuelto:
            return{"ok":False,"resuelto":True,"msg":"Ya resolviste el reto."}
        
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
            return{"ok":True, "puntos":puntos, "msg":"¡Flag correcta!"}
        return{"ok":False, "msg":"Flag incorrecta."}