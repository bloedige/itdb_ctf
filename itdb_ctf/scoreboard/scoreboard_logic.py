from sqlmodel import Session, select
from itdb_ctf.db import engine
from itdb_ctf.models import Resuelve, Usuario, Contiene, Compra
from itdb_ctf.core.puntaje_logic import puntaje_total_usuario

def scoreboard(id_evento:int) -> list[dict]:
    with Session(engine) as s:
        filas = s.exec(select(Resuelve.id_usuario, Usuario.alias, Usuario.nombre)
                       .join(Usuario, Resuelve.id_usuario == Usuario.id_usuario)
                       .where(Resuelve.id_evento == id_evento, Resuelve.flag_correcta == True)).all()
        vistos = {}
        for id_u, ali, nom in filas:
            if not id_u in vistos:
                vistos[id_u]= ali if ali else nom
        ultimas = {}
        for id_u in vistos:
            ultimas[id_u] = s.exec(select(Resuelve.fec_envio).where(
                Resuelve.id_usuario == id_u,
                Resuelve.id_evento == id_evento,
                Resuelve.flag_correcta == True)
                .order_by(Resuelve.fec_envio.desc())).first()
        ranking = [
            {
                "id_usuario":id_usuario,
                "nombre":nombre,
                "puntaje":puntaje_total_usuario(s, id_usuario, id_evento),
                "ultima":ultimas[id_usuario],    
            }
            for id_usuario, nombre in vistos.items()
        ]
        ranking.sort(key=lambda x: (-x['puntaje'], x['ultima']))
        for i, fila in enumerate(ranking, start=1):
            fila['posicion'] = i
        return ranking

def scoreboard_graph(id_evento:int, top:int = 5) -> tuple[list[dict], list[dict]]:
    with Session(engine) as s:
        rank = scoreboard(id_evento)[:top]
        series = [{"key": str(r["id_usuario"]), "nombre": r["nombre"]} for r in rank]  # orden = posicion
        ids = {r["id_usuario"] for r in rank}
        if not ids:
            return [], series

        valor_reto = {
            c.id_reto: c.puntaje_actual
            for c in s.exec(select(Contiene).where(Contiene.id_evento == id_evento)).all()
        }

        resueltos = s.exec(select(
            Resuelve.id_usuario, Resuelve.id_reto, Resuelve.fec_envio).where(
                Resuelve.id_evento == id_evento,
                Resuelve.flag_correcta == True,
                Resuelve.id_usuario.in_(list(ids)))).all()

        compras = s.exec(select(
            Compra.id_usuario, Compra.puntos_usados, Compra.fec_compra).where(
                Compra.id_evento == id_evento,
                Compra.id_usuario.in_(list(ids)))).all()

        # linea de tiempo unificada: (fecha, id_usuario, delta)  suma(+) / resta(-)
        eventos = []
        for id_u, id_r, fec in resueltos:
            eventos.append((fec, id_u, valor_reto.get(id_r, 0)))
        for id_u, pts, fec in compras:
            eventos.append((fec, id_u, -pts))
        eventos.sort(key=lambda e: e[0])

        acum = {str(i): 0 for i in ids}
        data = []
        for i, (fec, id_u, delta) in enumerate(eventos):
            k = str(id_u)
            acum[k] += delta
            # solo el usuario que actuo -> el dot cae solo en su suma/resta
            data.append({
                "t": i,
                "fecha": fec.strftime("%d/%m/%y %H:%M") if fec else "",
                k: acum[k],
            })
        return data, series