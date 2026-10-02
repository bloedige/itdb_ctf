"""Caja blanca — evento_cerrado/evento_cerrado_logic.acceso_evento_cerrado  (V(G) = 6).

Análisis completo en tests/docs/caja_blanca_05_acceso_evento_cerrado.md.
El camino C6 termina en `estado_inscripcion`, que tiene 3 salidas → 3 variantes.
"""

import pytest

from itdb_ctf.evento_cerrado.evento_cerrado_logic import acceso_evento_cerrado

from conftest import crear_evento, crear_usuario, inscribir


@pytest.fixture
def usuarios():
    return crear_usuario("admin@itdonbosco.org", rol="admin"), crear_usuario()


def test_C1_evento_inexistente(usuarios):
    _, est = usuarios
    assert acceso_evento_cerrado(9999, est) == (False, "Evento no encontrado.")


def test_C2_evento_desactivado(usuarios):
    admin, est = usuarios
    ev = crear_evento(admin, "activo", activo=False)
    inscribir(est, ev)
    assert acceso_evento_cerrado(ev, est) == (False, "Evento no encontrado.")


def test_C3_evento_abierto_no_es_cerrado(usuarios):
    admin, est = usuarios
    ev = crear_evento(admin, "abierto")
    inscribir(est, ev)
    assert acceso_evento_cerrado(ev, est) == (False, "Evento no encontrado.")


def test_C4_evento_concluido(usuarios):
    admin, est = usuarios
    ev = crear_evento(admin, "concluido")
    inscribir(est, ev)
    assert acceso_evento_cerrado(ev, est) == (False, "Evento culminado.")


def test_C5_evento_futuro(usuarios):
    admin, est = usuarios
    ev = crear_evento(admin, "futuro")
    inscribir(est, ev)
    assert acceso_evento_cerrado(ev, est) == (False, "El evento aún no inicia.")


@pytest.mark.parametrize("estado, esperado", [
    ("inscrito", (True, "")),
    (None, (False, "No estas inscrito en este evento.")),
    ("descalificado", (False, "Has sido desacalificado de el evento.")),
], ids=["inscrito", "sin_inscripcion", "descalificado"])
def test_C6_evento_activo_segun_inscripcion(usuarios, estado, esperado):
    admin, est = usuarios
    ev = crear_evento(admin, "activo")
    if estado:
        inscribir(est, ev, estado)
    assert acceso_evento_cerrado(ev, est) == esperado
