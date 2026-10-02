"""Caja blanca — core/envio_logic.enviar_flag  (V(G) = 11).

Un test por camino independiente. Análisis completo en
tests/docs/caja_blanca_01_enviar_flag.md. El camino C5 (evento inexistente)
no es factible: lo impide la clave foránea Contiene.id_evento → evento.
"""

import pytest
from sqlmodel import Session, select

from itdb_ctf.core.envio_logic import enviar_flag
from itdb_ctf.db import engine
from itdb_ctf.models import Resuelve

from conftest import asociar, crear_evento, crear_reto, crear_usuario, inscribir

FLAG_OK = "ITDB{flag_correcta}"


def envios(id_usuario, id_reto, id_evento):
    with Session(engine) as s:
        return s.exec(select(Resuelve).where(
            Resuelve.id_usuario == id_usuario,
            Resuelve.id_reto == id_reto,
            Resuelve.id_evento == id_evento,
        )).all()


@pytest.fixture
def escenario():
    """Escenario base válido: evento activo, reto asociado, estudiante inscrito."""
    admin = crear_usuario("admin@itdonbosco.org", rol="admin")
    est = crear_usuario()
    ev = crear_evento(admin, "activo")
    reto = crear_reto(admin, FLAG_OK)
    asociar(reto, ev)
    inscribir(est, ev)
    return {"admin": admin, "est": est, "ev": ev, "reto": reto}


def test_C1_supera_rate_limit(escenario):
    e = escenario
    for _ in range(15):                       # 15 permitidos por minuto
        enviar_flag(e["est"], e["reto"], e["ev"], "ITDB{mala}")
    ok, msg = enviar_flag(e["est"], e["reto"], e["ev"], FLAG_OK)
    assert ok is False
    assert msg.startswith("Demasiados intentos")
    assert len(envios(e["est"], e["reto"], e["ev"])) == 15   # el 16º no se registró


def test_C2_reto_inexistente(escenario):
    e = escenario
    assert enviar_flag(e["est"], 9999, e["ev"], FLAG_OK) == (False, "Reto no disponible.")


def test_C3_reto_inactivo(escenario):
    e = escenario
    reto = crear_reto(e["admin"], FLAG_OK, activo=False)
    asociar(reto, e["ev"])
    assert enviar_flag(e["est"], reto, e["ev"], FLAG_OK) == (False, "Reto no disponible.")


def test_C4_reto_no_pertenece_al_evento(escenario):
    e = escenario
    reto = crear_reto(e["admin"], FLAG_OK)                      # sin asociar
    assert enviar_flag(e["est"], reto, e["ev"], FLAG_OK) == (False, "El reto no pertenece a este evento.")


def test_C6_evento_futuro(escenario):
    e = escenario
    ev = crear_evento(e["admin"], "futuro")
    asociar(e["reto"], ev)
    inscribir(e["est"], ev)
    assert enviar_flag(e["est"], e["reto"], ev, FLAG_OK) == (False, "El evento aún no ha iniciado.")


def test_C7_evento_concluido(escenario):
    e = escenario
    ev = crear_evento(e["admin"], "concluido")
    asociar(e["reto"], ev)
    inscribir(e["est"], ev)
    assert enviar_flag(e["est"], e["reto"], ev, FLAG_OK) == (False, "El evento ha finalizado.")


@pytest.mark.parametrize("estado", [None, "descalificado"], ids=["sin_inscripcion", "descalificado"])
def test_C8_usuario_no_inscrito(escenario, estado):
    e = escenario
    otro = crear_usuario("otro@itdonbosco.org")
    if estado:
        inscribir(otro, e["ev"], estado)
    assert enviar_flag(otro, e["reto"], e["ev"], FLAG_OK) == (False, "No estás inscrito en este evento.")


def test_C9_reto_ya_resuelto(escenario):
    e = escenario
    assert enviar_flag(e["est"], e["reto"], e["ev"], FLAG_OK)[0] is True
    assert enviar_flag(e["est"], e["reto"], e["ev"], FLAG_OK) == (False, "El reto ah sido resuelto.")
    assert len(envios(e["est"], e["reto"], e["ev"])) == 1      # no se duplicó


def test_C10_flag_correcta(escenario):
    e = escenario
    assert enviar_flag(e["est"], e["reto"], e["ev"], FLAG_OK) == (True, "¡Flag correcta!")
    filas = envios(e["est"], e["reto"], e["ev"])
    assert len(filas) == 1 and filas[0].flag_correcta is True


def test_C11_flag_incorrecta(escenario):
    e = escenario
    assert enviar_flag(e["est"], e["reto"], e["ev"], "ITDB{mala}") == (False, "Flag incorrecta.")
    filas = envios(e["est"], e["reto"], e["ev"])
    assert len(filas) == 1 and filas[0].flag_correcta is False
