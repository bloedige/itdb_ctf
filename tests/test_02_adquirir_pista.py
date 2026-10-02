"""Caja blanca — core/compra_logic.adquirir_pista  (V(G) = 4).

Análisis completo en tests/docs/caja_blanca_02_adquirir_pista.md.
"""

import pytest
from sqlmodel import Session, select

from itdb_ctf.core.compra_logic import adquirir_pista
from itdb_ctf.db import engine
from itdb_ctf.models import Compra

from conftest import (asociar, comprar, crear_evento, crear_pista, crear_reto,
                      crear_usuario, inscribir, resolver)


def compras(id_usuario, id_evento):
    with Session(engine) as s:
        return s.exec(select(Compra).where(
            Compra.id_usuario == id_usuario, Compra.id_evento == id_evento)).all()


@pytest.fixture
def escenario():
    """Estudiante con 100 pts (resolvió un reto de 100) y un segundo reto con pista."""
    admin = crear_usuario("admin@itdonbosco.org", rol="admin")
    est = crear_usuario()
    ev = crear_evento(admin, "activo")
    resuelto = crear_reto(admin)
    asociar(resuelto, ev, puntaje=100)
    reto = crear_reto(admin)
    asociar(reto, ev, puntaje=200)
    inscribir(est, ev)
    resolver(est, resuelto, ev)                     # saldo = 100
    return {"est": est, "ev": ev, "reto": reto}


def test_C1_pista_inexistente(escenario):
    e = escenario
    assert adquirir_pista(e["est"], e["ev"], e["reto"], 9999) == (False, "Pista inexistente")
    assert compras(e["est"], e["ev"]) == []


def test_C2_pista_ya_adquirida(escenario):
    e = escenario
    pista = crear_pista(e["reto"], costo=10)
    comprar(e["est"], e["reto"], e["ev"], pista, 10)
    assert adquirir_pista(e["est"], e["ev"], e["reto"], pista) == (False, "Pista adquirida")
    assert len(compras(e["est"], e["ev"])) == 1      # no se duplicó


def test_C3_puntos_insuficientes(escenario):
    e = escenario
    pista = crear_pista(e["reto"], costo=101)        # saldo 100 → falta 1 punto
    assert adquirir_pista(e["est"], e["ev"], e["reto"], pista) == (
        False, "Puntos insuficientes para adquirir la pista")
    assert compras(e["est"], e["ev"]) == []


@pytest.mark.parametrize("costo", [30, 100], ids=["costo_menor_al_saldo", "costo_igual_al_saldo"])
def test_C4_compra_exitosa(escenario, costo):
    e = escenario
    pista = crear_pista(e["reto"], costo=costo)
    assert adquirir_pista(e["est"], e["ev"], e["reto"], pista) == (True, "Pista adquirida.")
    filas = compras(e["est"], e["ev"])
    assert len(filas) == 1 and filas[0].puntos_usados == costo
