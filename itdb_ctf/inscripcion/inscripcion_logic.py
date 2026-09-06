import csv, io
from datetime import datetime, timezone
from sqlmodel import select, Session
from itdb_ctf.db import engine
from itdb_ctf.models import Evento, Participa, Usuario, Rol, EstadoInscripcion, MetodoAuth
from itdb_ctf.auth.auth_logic import DominiNoPermitido, validar_dominio, separar_apellidos
from itdb_ctf.utils.validaciones import formato_email_valido
def estado_evento(ev) -> str:
    if not ev.fec_inicio:
        return "abierto"
    now = datetime.now(timezone.utc)
    fi = ev.fec_inicio if ev.fec_inicio.tzinfo else ev.fec_inicio.replace(tzinfo=timezone.utc)
    ff = None
    if ev.fec_fin:
        ff = ev.fec_fin if ev.fec_fin.tzinfo else ev.fec_fin.replace(tzinfo=timezone.utc)
    if now < fi:
        return "futuro"
    if ev.fec_fin and fi <= now <= ff:
        return "activo"
    return "concluido"

def id_estado(etiqueta:str) -> int | None:
    with Session(engine) as s:
        estado = s.exec(select(EstadoInscripcion).where(EstadoInscripcion.etiqueta == etiqueta)).first()
        return estado.id_estado_inscripcion if estado else None
    
def eventos_inscribibles() -> list[tuple[str, str]]:
    with Session(engine) as s:
        eventos = s.exec(select(Evento).where(Evento.activo == True)).all()
        return [
            (str(ev.id_evento), (f"{ev.titulo} ({estado_evento(ev)})"))
            for ev in eventos if estado_evento(ev) in ("futuro", "activo")            
        ]
    
def candidatos(id_evento:int, busqueda:str | None=None, id_metodo: int | None=None ):
    with Session(engine) as s:
        inscritos = set(s.exec(select(Participa.id_usuario).where(Participa.id_evento == id_evento)).all())
        stmt = (select(Usuario, MetodoAuth.etiqueta)
                .join(Rol , Usuario.id_rol == Rol.id_rol)
                .join(MetodoAuth, MetodoAuth.id_metodo_auth == Usuario.id_metodo_auth)
                .where(Rol.codigo == "user", Usuario.activo == True))
        if id_metodo:
            stmt = stmt.where(Usuario.id_metodo_auth == id_metodo)
        if busqueda:
            patron = f"%{busqueda}%"
            stmt = stmt.where(
                Usuario.email_inst.ilike(patron)
                |Usuario.nombre.ilike(patron)
                |Usuario.paterno.ilike(patron)
                |Usuario.alias.ilike(patron)
            )
        resultado = []
        for user, met in s.exec(stmt).all():
            if user.id_usuario in inscritos:
                continue
            resultado.append({
                "id_usuario":user.id_usuario,
                "alias":user.alias if user.alias else "---",
                "email_inst":user.email_inst,
                "nombre":f"{user.nombre} {user.paterno}",
                "metodo":met,
            })
        return resultado
    
def participantes(id_evento:int, busqueda:str | None=None, id_estado_filtro:int | None=None):
    with Session(engine) as s:
        ev = s.get(Evento, id_evento)
        futuro = estado_evento(ev) == "futuro" if ev else False
        stmt = (select(Usuario, EstadoInscripcion.etiqueta, Participa.fec_ingreso, Participa.id_participa)
                .join(Participa, Usuario.id_usuario == Participa.id_usuario)
                .join(EstadoInscripcion, Participa.id_estado_inscripcion == EstadoInscripcion.id_estado_inscripcion)
                .where(Participa.id_evento == id_evento)
                .order_by(Usuario.email_inst).order_by(EstadoInscripcion.id_estado_inscripcion.desc()))
        if id_estado_filtro:
            stmt = stmt.where(Participa.id_estado_inscripcion == id_estado_filtro)
        if busqueda:
            patron = f"%{busqueda}%" 
            stmt = stmt.where(
                Usuario.alias.ilike(patron)
                |Usuario.email_inst.ilike(patron)
                |Usuario.nombre.ilike(patron)
                |Usuario.paterno.ilike(patron)
                )   

        return [
            {
                "id_participa":id_p,
                "id_usuario":user.id_usuario,
                "alias":user.alias if user.alias else "---",
                "nombre":f"{user.nombre} {user.paterno}",
                "email_inst":user.email_inst,
                "estado":est,
                "quitar":futuro,
                "descalificado":est == "descalificado",
                "fec_ingreso":fec.strftime("%d/%m/%Y %H:%M") if fec else "---"
            } for user, est, fec, id_p in s.exec(stmt).all()
        ]    
        
def validar_incribir(id_usuario:int, id_evento:int) -> tuple[bool, str]:
    with Session(engine) as s:
        ev = s.get(Evento, id_evento)
        if not ev:
            return False , "Evento inexistente."
        est_ev = estado_evento(ev)
        if est_ev == "abierto":
            return False , "Evento abierto usa auto_incripción."
        if est_ev == "concluido":
            return False , "Evento concluido."
        u = s.get(Usuario, id_usuario)
        if not u:
            return False , "cuenta inexistente."
        if not u.activo:
            return False , "Cuenta desactivada."
        rol = s.get(Rol, u.id_rol)
        if not rol or rol.codigo != "user":
            return False , "Rol invalido para participación."
        part = s.exec(select(Participa).where(Participa.id_usuario == id_usuario, Participa.id_evento == id_evento)).first()
        if part:
            return False , "La cuenta ya ah sido inscrita." 
        return True, ""
    
def inscribir(id_susario:int, id_evento:int): 
    ok, msg = validar_incribir(id_susario,id_evento)
    if not ok:
        raise ValueError(msg)
    id_est = id_estado("inscrito")
    if not id_est:
        raise ValueError("Estado inscrito no configurado")
    with Session(engine) as s:
        s.add(Participa(
            id_estado_inscripcion=id_est,
            id_evento=id_evento,
            id_usuario=id_susario,
            fec_ingreso=datetime.now(timezone.utc)
        ))  
        s.commit()
        return True

def inscribir_lote(ids_usuario:list[int], id_evento:int) -> tuple[int, str]:
    ok = 0
    errors = []
    for id_u in ids_usuario:
        try:
            inscribir(id_u,id_evento)
            ok += 1
        except ValueError as e:
            errors.append(f"{id_u}: {e}")
    return ok, errors

def validar_quitar(id_participa:int) ->tuple[bool, str]:
    with Session(engine) as s:
        pr = s.get(Participa, id_participa)
        if not pr:
            return False, "Registro inexistente."
        ev = s.get(Evento, pr.id_evento)
        if not ev:
            return False, "Evento inexistente."
        if estado_evento(ev) != "futuro":
            return False, "Acción no valida use desacalificar." 
        return True, ""

def quitar_incripcion(id_participa:int):
    ok, msg = validar_quitar(id_participa)
    if not ok:
        raise ValueError(msg)
    with Session(engine) as s:
        p = s.get(Participa, id_participa)
        s.delete(p)
        s.commit()
        return True

def alternar_estado(id_participa:int):
    with Session(engine) as s:
        p = s.get(Participa, id_participa)
        if not p: 
            raise ValueError("Registro inexistente.")
        est_act = s.get(EstadoInscripcion, p.id_estado_inscripcion)
        est = "inscrito" if est_act.etiqueta == "descalificado" else "descalificado"
        id_est = id_estado(est)
        if not id_est: 
            raise ValueError(f"{est} no configurado.")
        p.id_estado_inscripcion = id_est
        s.add(p)
        s.commit()
        return est
      

def parsear_cvs(contenido:bytes) -> list[str]:
    texto = contenido.decode("utf-8-sig", errors="ignore")
    correos = []
    for fila in csv.reader(io.StringIO(texto)):
        if not fila:
            continue
        valor = fila[0].strip().lower()
        if valor and "@" in valor:
            correos.append(valor)
    return correos

def analizar_correos(correos:list[str], id_evento:int) -> dict:
    nuevos = []
    existentes = []
    omitidos= []
    vistos = set()
    with Session(engine) as s:
        inscritos = set(s.exec(select(Participa.id_usuario).where(Participa.id_evento == id_evento)).all())
        for correo in correos:
            if correo in vistos:
                omitidos.append({"email":correo, "motivo":"Correo duplicado en archivo."})
                continue
            vistos.add(correo)
            if not formato_email_valido(correo):
                omitidos.append({"email": correo, "motivo": "Formato de correo invalido"})
                continue
            try:
                validar_dominio(correo)
            except DominiNoPermitido:
                omitidos.append({"email":correo, "motivo":"Correo no institucional."})
                continue
            user = s.exec(select(Usuario).where(Usuario.email_inst == correo)).first()
            if user:
                if user.id_usuario in inscritos:
                    omitidos.append({"email":correo, "motivo":"Inscrito en evento."})
                elif not user.activo:
                    omitidos.append({"email":correo, "motivo":"Cuenta desactivada."})
                else:
                    existentes.append({"email":correo, "id_usuario":user.id_usuario})
            else:
                nuevos.append({"email":correo})
    omitidos.sort(key=lambda o: o['motivo'])
    return {"nuevos":nuevos, "existentes":existentes, "omitidos":omitidos}


def crear_placeholder(correo:str) -> int:
    with Session(engine) as s:
        rol = s.exec(select(Rol).where(Rol.codigo == "user")).one()
        met = s.exec(select(MetodoAuth).where(MetodoAuth.etiqueta == "google")).one()
        local = correo.split("@")[0]
        user = Usuario(
            id_rol=rol.id_rol,
            id_metodo_auth=met.id_metodo_auth,
            nombre=local,
            paterno="placeholder",
            materno="placeholder",
            email_inst=correo,
            alias=local[:30],
        )
        s.add(user)
        s.commit()
        s.refresh(user)
        return user.id_usuario
    
def confirmar_csv(nuevos:list[dict], existentes:list[dict], id_evento:int) -> tuple[int, list[str]]:
    ids = [e["id_usuario"] for e in existentes]
    for n in nuevos:
        try: 
            ids.append(crear_placeholder(n["email"]))
        except Exception as ex:
            pass
    return inscribir_lote(ids, id_evento)