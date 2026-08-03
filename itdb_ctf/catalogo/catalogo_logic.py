from sqlmodel import select, Session
from itdb_ctf.db import engine
from itdb_ctf.models import Reto, Categoria, Dificultad, Usuario, Resuelve, EstadoInscripcion, Participa, Contiene

def inscrito(id_usuario:int, id_evento:int) -> bool:
    with Session(engine) as s:
        est = s.exec(select(EstadoInscripcion.id_estado_inscripcion)
                     .where(EstadoInscripcion.etiqueta == "inscrito")).first()
        if not est:
            return False
        part = s.exec(select(Participa).where(
            Participa.id_usuario == id_usuario,
            Participa.id_evento == id_evento,
            Participa.id_estado_inscripcion == est
        )).first()
        return part is not None

def cargar_catalogos() -> dict:
    with Session(engine) as s:
        return {
            "categorias": [("","Todos")] + [(str(c.id_categoria),c.etiqueta) for c in s.exec(select(Categoria)).all()],
            "dificultades": [("","Todos")] + [(str(d.id_dificultad),d.etiqueta) for d in s.exec(select(Dificultad)).all()]
        }
    
def listar_retos(id_usuario:int, id_evento:int, id_categoria:int | None = None, id_dificultad:int | None = None):
    with Session(engine) as s:
        resueltos = s.exec(select(Resuelve.id_reto).where(
            Resuelve.id_usuario == id_usuario,
            Resuelve.id_evento == id_evento,
            Resuelve.flag_correcta == True,
        )).all()

        stmt = (select(Reto, Contiene, Categoria.etiqueta, Dificultad.etiqueta, Usuario.alias, Usuario.nombre)
                .join(Categoria, Reto.id_categoria == Categoria.id_categoria)
                .join(Dificultad, Reto.id_dificultad == Dificultad.id_dificultad)
                .join(Usuario, Reto.id_usuario == Usuario.id_usuario)
                .join(Contiene, Reto.id_reto == Contiene.id_reto)
                .where(Reto.activo == True, Contiene.id_evento == id_evento)
                .order_by(Categoria.id_categoria))
        
        if id_categoria:
            stmt = stmt.where(Reto.id_categoria == id_categoria)
        if id_dificultad:
            stmt = stmt.where(Reto.id_dificultad == id_dificultad)

        return[
            {
                "id_reto":r.id_reto,
                "titulo":r.titulo,
                "descripcion":r.descripcion,
                "categoria":cat,
                "dificultad":dif,
                "creador":ali if ali else nom,
                "puntaje":c.puntaje_inicial,
                "original":r.archivo_original,
                "resuelto":r.id_reto in resueltos,
            }
            for r ,c, cat, dif, ali, nom in s.exec(stmt).all()
        ]
    
