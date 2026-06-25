import reflex as rx
from sqlmodel import select, Session
from itdb_ctf.db import engine
from itdb_ctf.models import Reto, Categoria, Dificultad, Usuario, Resuelve, EstadoInscripcion, Participa, Contiene
from itdb_ctf.auth.auth_state import AuthState
from itdb_ctf.retos.envio_logic import enviar_flag
from itdb_ctf.retos.evento_logic import id_evento_abierto

class CatalogoState(AuthState):
    retos:list[dict]=[]
    filtro_categoria:str=""
    filtro_dificultad:str=""
    # --- Opciones de filtro
    cat_opciones:list[tuple[str,str]]=[]
    dif_opciones:list[tuple[str,str]]=[]
    
    def set_filtro_categoria(self, v:str):
        self.filtro_categoria=v

    def set_filtro_dificultad(self, v:str):
        self.filtro_dificultad=v

    def cargar_retos(self):
        # --- Verificamos que el usuario este logueado
        guard = self.requiere_login()
        if guard:
            return guard
        
        id_evento=id_evento_abierto()

        with Session(engine) as s:

            est_aceptado = s.exec(select(EstadoInscripcion.id_estado_inscripcion).where(EstadoInscripcion.etiqueta=="aceptado")).first()
            aceptado = s.exec(select(Participa).where(
                Participa.id_usuario==self.id_usuario,
                Participa.id_evento==id_evento,
                Participa.id_estado_inscripcion==est_aceptado,
            )).first()

            if not aceptado:
                self.retos=[]
                self.cat_opciones=[]
                self.dif_opciones=[]
                return
            
            self.cat_opciones=[(str(c.id_categoria),c.etiqueta) for c in s.exec(select(Categoria)).all()] 
            self.dif_opciones=[(str(d.id_dificultad),d.etiqueta) for d in s.exec(select(Dificultad)).all()]

            resueltos = set(s.exec(select(Resuelve.id_reto).where(Resuelve.id_usuario==self.id_usuario,Resuelve.flag_correcta==True)).all())
            
            stmt=(
                select(Reto,Categoria.etiqueta,Dificultad.etiqueta,Usuario.alias,Usuario.nombre)
                .join(Categoria, Reto.id_categoria == Categoria.id_categoria)
                .join(Dificultad, Reto.id_dificultad == Dificultad.id_dificultad)
                .join(Usuario, Reto.id_usuario == Usuario.id_usuario)
                .join(Contiene, Reto.id_reto == Contiene.id_reto)
                .where(Reto.activo==True, Contiene.id_evento==id_evento)
            )
            if self.filtro_categoria:
                stmt=stmt.where(Reto.id_categoria==int(self.filtro_categoria))
            if self.filtro_dificultad:
                stmt=stmt.where(Reto.id_dificultad==int(self.filtro_dificultad))

            filas=s.exec(stmt).all()

            self.retos=[
                {
                    "id":r.id_reto,
                    "categoria":categoria,
                    "dificultad":dificultad,
                    "creador":alias or nombre,
                    "titulo":r.titulo,
                    "descripcion":r.descripcion,
                    "puntaje":r.puntaje_inicial,
                    "original":r.archivo_original,
                    "resuelto":r.id_reto in resueltos,
                    "resultado":""

                }       
                for r, categoria, dificultad, alias, nombre in filas             
            ]

    def filtrar_categoria(self, id_cat:str):
        self.filtro_categoria=id_cat
        return CatalogoState.cargar_retos
    
    def filtrar_dificultad(self, id_dif:str):
        self.filtro_dificultad=id_dif
        return CatalogoState.cargar_retos


class EnvioFlagState(AuthState):
    flag_input:dict[int,str]={}

    #resultado:dict[int,str]={}

    def set_flag(self, id_reto:int, cadena:str):
        self.flag_input[id_reto]=cadena 

    async def enviar(self, id_reto:int):
        #  --- Validamos login
        guard = self.requiere_login()
        if guard:
            return guard
        
        flag = self.flag_input.get(id_reto,"")

        cat =  await self.get_state(CatalogoState)

        if not flag:
            self.marcar(cat, id_reto, "Escrive una flag")
            return
        
        id_evento=id_evento_abierto()

        if not id_evento:
            self.marcar(cat, id_reto, "Evento no activo")
            return 
        
        r=enviar_flag(
            id_usuario=self.id_usuario,
            id_reto=id_reto,
            id_evento=id_evento,
            flag_enviada=flag,
        )

        self.marcar(cat,id_reto,r['msg'],r.get('ok',False))

        #self.resultado[id_reto]=r['msg']
        if r.get('ok'):
            self.flag_input[id_reto]=""


    def marcar(self,cat:"CatalogoState", id_reto:int,msg:str,resuelto:bool=False): 
        nuevos=[]
        for x in cat.retos:
            if x['id'] == id_reto:
                x={**x, "resultado":msg}
                if resuelto:
                    x["resuelto"]=True
            nuevos.append(x)
        cat.retos=nuevos

        

    


