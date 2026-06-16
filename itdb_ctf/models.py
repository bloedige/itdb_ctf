
from __future__ import annotations
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, CHAR, Text, DateTime, func
from sqlalchemy.dialects.postgresql import INET

###          CATALOGOS

class Rol(SQLModel, table=True):
    __tablename__ = "rol"
    id_rol: Optional[int] = Field(default=None, primary_key=True)
    codigo: str = Field(max_length=15, unique=True)      # superadmin, admin, autor, user
    etiqueta: str = Field(max_length=25)   # super administrador, administrador, autor de retos, estudiante

class Categoria(SQLModel, table=True):
    __tablename__ = "categoria"
    id_categoria: Optional[int] = Field(default=None, primary_key=True)
    etiqueta: str = Field(max_length=30, unique=True)   #web, exploting......
    descripcion: Optional[str] = Field(default=None, sa_column=Column(Text))
    activo: bool = Field(default=True)

class Dificultad(SQLModel, table=True):
    __tablename__ = "dificultad"
    id_dificultad: Optional[int] = Field(default=None, primary_key=True)
    etiqueta: str = Field(max_length=15, unique=True)  #facil, dificil ......

class ModoPuntaje(SQLModel, table=True):
    __tablename__ = "modo_puntaje"
    id_modo_puntaje: Optional[int] = Field(default=None, primary_key=True)
    etiqueta: str = Field(max_length=15, unique=True)  # estatico, dinamico

class Modalidad(SQLModel, table=True):
    __tablename__ = "modalidad"
    id_modalidad: Optional[int] = Field(default=None, primary_key=True)
    etiqueta: str = Field(max_length=15, unique=True)     # abierto, cerrado

class EstadoWriteup(SQLModel, table=True):
    __tablename__ = "estado_writeup"
    id_estado_writeup: Optional[int]=Field(default=None, primary_key=True)
    etiqueta: str = Field(max_length=15, unique=True)  # borrador,pendiente, aprobado, rechazado

class EstadoInscripcion(SQLModel, table=True):
    __tablename__ = "estado_inscripcion"
    id_estado_inscripcion: Optional[int]=Field(default=None, primary_key=True)
    etiqueta: str = Field(max_length=15, unique=True)    #inscrito, invitado, aceptado, rechazado

class MetodoAuth(SQLModel, table=True):
    __tablename__ = "metodo_auth"
    id_metodo_auth: Optional[int]=Field(default=None, primary_key=True)
    etiqueta: str = Field(max_length=15, unique=True)   # google, local {github, microsotf........}
    activo: bool = Field(default=True)

###         ENTIDADES

class Usuario(SQLModel, table=True):
    __tablename__ = "usuario"
    id_usuario: Optional[int]= Field(default=None, primary_key=True)
    id_rol: int = Field(foreign_key="rol.id_rol")
    id_metodo_auth: int = Field(foreign_key="metodo_auth.id_metodo_auth")

    nombre: str = Field(max_length=50)
    paterno: str = Field(max_length=50)
    materno: Optional[str] = Field(default=None, max_length=50)
    alias: Optional[str] = Field(default=None, max_length=30)
    password_hash: Optional[str] = Field(default=None, sa_column=Column(CHAR(60)))
    email_inst: str = Field(max_length=150, unique=True, index=True)
    avatar: Optional[str] =  Field(default=None, max_length=255)
    fec_registro: datetime = Field(sa_column=Column(DateTime(timezone=True),server_default=func.now()))
    activo: bool = Field(default=True)

class Evento(SQLModel, table=True):
    __tablename__="evento"
    id_evento: Optional[int] = Field(default=None, primary_key=True)
    id_usuario: int = Field(foreign_key="usuario.id_usuario")
    id_modalidad: int = Field(foreign_key="modalidad.id_modalidad")
    id_modo_puntaje: int = Field(foreign_key="modo_puntaje.id_modo_puntaje")

    titulo: str=Field(max_length=100)
    descripcion: Optional[str] = Field(default=None, sa_column=Column(Text))
    fec_inicio: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    fec_fin: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    fec_creacion: datetime = Field(sa_column=Column(DateTime(timezone=True),server_default=func.now()))
    freeze: bool = Field(default=False)  #freeze de tabal de posisones
    auto_inscripcion: Optional[bool] = Field(default=None)
    activo: bool =Field(default = True)     #se desactiva una vez que su periodo finalice
    
class Reto(SQLModel, table=True):
    __tablename__="reto"
    id_reto: Optional[int] = Field(default=None, primary_key=True)
    id_usuario: int = Field(foreign_key="usuario.id_usuario")
    id_categoria: int = Field(foreign_key="categoria.id_categoria")
    id_dificultad: int = Field(foreign_key="dificultad.id_dificultad")
    id_modo_puntaje: int = Field(foreign_key="modo_puntaje.id_modo_puntaje")

    titulo: str = Field(max_length=100)
    descripcion: Optional[str] = Field(default=None, sa_column=Column(Text))
    flag: str =  Field(sa_column=Column(CHAR(64)))
    puntaje_inicial: int
    puntaje_minimo: Optional[int] = Field(default=None)
    archivo_original: Optional[str] =  Field(default=None, max_length=100)
    archivo_ruta: Optional[str] =    Field(default=None, max_length=255)
    fec_creacion: datetime = Field(sa_column=Column(DateTime(timezone=True),server_default=func.now()))
    activo: bool = Field(default=True)

class Pista(SQLModel, table=True):
    __tablename__="pista"
    id_pista: Optional[int] = Field(default=None,primary_key=True)
    id_reto: int = Field(foreign_key="reto.id_reto")

    costo: int = Field(default=0)
    descripcion: str = Field(sa_column=Column(Text))
    activo: bool = Field(default=True)

class Writeup(SQLModel, table=True):
    __tablename__="writeup"
    id_writeup: Optional[int] = Field(default=None, primary_key=True)
    id_usuario: int = Field(foreign_key="usuario.id_usuario")
    id_reto: int = Field(foreign_key="reto.id_reto")
    id_estado_writeup: int = Field(foreign_key="estado_writeup.id_estado_writeup")

    writeup_ruta: str = Field(max_length=255)
    fec_creacion: datetime = Field(sa_column=Column(DateTime(timezone=True),server_default=func.now())) 
    activo: bool = Field(default=True)


    ###     TABLAS ASOCIATIVAS

class Resuelve(SQLModel, table=True):
    __tablename__="resuelve"
    id_resuelve: Optional[int] = Field(default=None, primary_key=True)
    id_usuario: int = Field(foreign_key="usuario.id_usuario")
    id_reto: int = Field(foreign_key="reto.id_reto")
    id_evento: int = Field(foreign_key="evento.id_evento")
    flag_correcta: bool = Field(default=False)
    puntos: int = Field(default=0)
    dir_ip: Optional[str] = Field(default=None, sa_column=Column(INET))   
    fec_envio: datetime = Field(sa_column=Column(DateTime(timezone=True),server_default=func.now()))

class Participa(SQLModel, table=True):
    __tablename__="participa"
    id_participa: Optional[int] =  Field(default=None, primary_key=True)
    id_usuario: int = Field(foreign_key="usuario.id_usuario")
    id_evento: int = Field(foreign_key="evento.id_evento")
    id_estado_inscripcion: int = Field(foreign_key="estado_inscripcion.id_estado_inscripcion")
    fec_invitacion: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    fec_ingreso: Optional[datetime] =  Field(default=None, sa_column=Column(DateTime(timezone=True)))

class Compra(SQLModel, table=True):
    __tablename__="compra"
    id_compra: Optional[int] = Field(default=None, primary_key=True)
    id_usuario: int = Field(foreign_key="usuario.id_usuario")
    id_reto: int = Field(foreign_key="reto.id_reto")
    id_evento: int = Field(foreign_key="evento.id_evento")
    id_pista: int = Field(foreign_key="pista.id_pista")
    puntos_usados: int = Field(default=0)
    fec_compra: datetime = Field(sa_column=Column(DateTime(timezone=True),server_default=func.now()))

class Contiene(SQLModel, table=True):
    __tablename__="contiene"
    id_contiene: Optional[int] = Field(default=None, primary_key=True)
    id_reto: int = Field(foreign_key="reto.id_reto")
    id_evento: int = Field(foreign_key="evento.id_evento")
    puntaje_override: Optional[int] = Field(default=None)

