"""Configuración común de las pruebas de caja blanca.

1. Apunta la app a la BD de PRUEBAS (`ctf_itdb_test`) ANTES de importar `itdb_ctf`.
   `db.py` crea el engine al importarse leyendo `DATABASE_URL`, y `load_dotenv()`
   no pisa una variable que ya existe → todos los `*_logic` usan la BD de test.
2. Protección: si el nombre de la BD no termina en `_test`, se aborta todo.
3. Redis falso en memoria (`fakeredis`): no toca Memurai ni el Redis real.
4. Antes de CADA prueba se vacían las tablas y se cargan los catálogos mínimos.
"""

import os
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

import pytest
from dotenv import dotenv_values

# --- 1. BD de pruebas -------------------------------------------------------
_RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_url_dev = dotenv_values(os.path.join(_RAIZ, ".env")).get("DATABASE_URL", "")
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL") or _url_dev.rsplit("/", 1)[0] + "/ctf_itdb_test"

# --- 2. Protección ----------------------------------------------------------
if not urlparse(TEST_DATABASE_URL).path.lstrip("/").endswith("_test"):
    raise RuntimeError("Las pruebas solo corren sobre una BD cuyo nombre termine en '_test'.")

os.environ["DATABASE_URL"] = TEST_DATABASE_URL

# Recién ahora se importa la app
import fakeredis  # noqa: E402
from sqlalchemy import text  # noqa: E402
from sqlmodel import Session, SQLModel, select  # noqa: E402

from itdb_ctf import models  # noqa: E402,F401  (registra todas las tablas)
from itdb_ctf.db import engine  # noqa: E402
from itdb_ctf.models import (  # noqa: E402
    Categoria, Compra, Contiene, Dificultad, EstadoInscripcion, Evento, MetodoAuth,
    Modalidad, ModoPuntaje, Participa, Pista, Resuelve, Reto, Rol, Usuario,
)
from itdb_ctf.utils.security import flag_hasher  # noqa: E402
from itdb_ctf.websockets import redis_cliente  # noqa: E402

assert engine.url.database.endswith("_test"), "El engine no apunta a la BD de pruebas."


# --- Esquema: se crea una vez por corrida desde models.py --------------------
@pytest.fixture(scope="session", autouse=True)
def esquema():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    yield


# --- 3. Redis falso ---------------------------------------------------------
@pytest.fixture(autouse=True)
def redis_falso():
    falso = fakeredis.FakeRedis(decode_responses=True)
    redis_cliente._sync = falso
    redis_cliente._estado = True
    redis_cliente._ultimo_sondeo = time.monotonic() + 10**9   # nunca re-sondea
    yield falso
    falso.flushall()


# --- 4. Estado limpio antes de cada prueba ----------------------------------
ROLES = ["superadmin", "admin", "autor", "user"]
CATALOGOS = {
    ModoPuntaje: ["estatico", "dinamico"],
    Modalidad: ["abierto", "cerrado"],
    Dificultad: ["Fácil"],
    Categoria: ["Web"],
    EstadoInscripcion: ["inscrito", "descalificado"],
    MetodoAuth: ["google", "local"],
}


@pytest.fixture(autouse=True)
def bd_limpia():
    tablas = ", ".join(f'"{t.name}"' for t in SQLModel.metadata.sorted_tables)
    with Session(engine) as s:
        s.exec(text(f"TRUNCATE {tablas} RESTART IDENTITY CASCADE"))
        for codigo in ROLES:
            s.add(Rol(codigo=codigo, etiqueta=codigo))
        for modelo, etiquetas in CATALOGOS.items():
            for et in etiquetas:
                s.add(modelo(etiqueta=et))
        s.commit()
    yield


# --- Fábricas: arman el escenario de cada caso ------------------------------
def id_catalogo(modelo, etiqueta: str) -> int:
    pk = list(modelo.__table__.primary_key.columns)[0]
    with Session(engine) as s:
        return s.exec(select(pk).where(modelo.etiqueta == etiqueta)).one()


def ahora() -> datetime:
    return datetime.now(timezone.utc)


def crear_usuario(email="estudiante@itdonbosco.org", rol="user", metodo="local",
                  password_hash=None, activo=True) -> int:
    with Session(engine) as s:
        id_rol = s.exec(select(Rol.id_rol).where(Rol.codigo == rol)).one()
        u = Usuario(
            id_rol=id_rol,
            id_metodo_auth=id_catalogo(MetodoAuth, metodo),
            nombre="Prueba", paterno="Test",
            email_inst=email, password_hash=password_hash, activo=activo,
        )
        s.add(u)
        s.commit()
        return u.id_usuario


def crear_evento(id_creador: int, estado="activo", modo="estatico", activo=True) -> int:
    """estado: 'abierto' (sin fechas) | 'activo' | 'futuro' | 'concluido'."""
    fechas = {
        "abierto": (None, None),
        "activo": (ahora() - timedelta(days=1), ahora() + timedelta(days=1)),
        "futuro": (ahora() + timedelta(days=1), ahora() + timedelta(days=2)),
        "concluido": (ahora() - timedelta(days=2), ahora() - timedelta(days=1)),
    }[estado]
    with Session(engine) as s:
        ev = Evento(
            id_usuario=id_creador,
            id_modalidad=id_catalogo(Modalidad, "abierto" if estado == "abierto" else "cerrado"),
            id_modo_puntaje=id_catalogo(ModoPuntaje, modo),
            titulo=f"Evento {estado}",
            fec_inicio=fechas[0], fec_fin=fechas[1],
            activo=activo,
        )
        s.add(ev)
        s.commit()
        return ev.id_evento


def crear_reto(id_autor: int, flag="ITDB{flag_correcta}", activo=True, puntaje=100) -> int:
    with Session(engine) as s:
        r = Reto(
            id_usuario=id_autor,
            id_categoria=id_catalogo(Categoria, "Web"),
            id_dificultad=id_catalogo(Dificultad, "Fácil"),
            id_modo_puntaje=id_catalogo(ModoPuntaje, "estatico"),
            titulo="Reto de prueba",
            flag=flag_hasher.hashear(flag),
            puntaje_inicial=puntaje, activo=activo,
        )
        s.add(r)
        s.commit()
        return r.id_reto


def asociar(id_reto: int, id_evento: int, modo="estatico", puntaje=100, minimo=None, actual=None) -> int:
    with Session(engine) as s:
        c = Contiene(
            id_reto=id_reto, id_evento=id_evento,
            id_modo_puntaje=id_catalogo(ModoPuntaje, modo),
            puntaje_inicial=puntaje, puntaje_minimo=minimo,
            puntaje_actual=puntaje if actual is None else actual,
        )
        s.add(c)
        s.commit()
        return c.id_contiene


def inscribir(id_usuario: int, id_evento: int, estado="inscrito") -> None:
    with Session(engine) as s:
        s.add(Participa(
            id_usuario=id_usuario, id_evento=id_evento,
            id_estado_inscripcion=id_catalogo(EstadoInscripcion, estado),
            fec_ingreso=ahora(),
        ))
        s.commit()


def crear_pista(id_reto: int, costo: int) -> int:
    with Session(engine) as s:
        p = Pista(id_reto=id_reto, costo=costo, descripcion="Pista de prueba")
        s.add(p)
        s.commit()
        return p.id_pista


def resolver(id_usuario: int, id_reto: int, id_evento: int, correcta=True, fecha=None) -> None:
    """Inserta un envío en Resuelve (fecha opcional para probar el freeze)."""
    with Session(engine) as s:
        s.add(Resuelve(
            id_usuario=id_usuario, id_reto=id_reto, id_evento=id_evento,
            flag_correcta=correcta, fec_envio=fecha or ahora(),
        ))
        s.commit()


def comprar(id_usuario: int, id_reto: int, id_evento: int, id_pista: int, puntos: int, fecha=None) -> None:
    """Inserta una compra de pista directamente (fecha opcional para el freeze)."""
    with Session(engine) as s:
        s.add(Compra(
            id_usuario=id_usuario, id_reto=id_reto, id_evento=id_evento,
            id_pista=id_pista, puntos_usados=puntos, fec_compra=fecha or ahora(),
        ))
        s.commit()
