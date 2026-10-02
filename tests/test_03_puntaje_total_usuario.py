"""Caja blanca — core/puntaje_logic.puntaje_total_usuario  (V(G) = 10, 7 caminos factibles).

Análisis completo en tests/docs/caja_blanca_03_puntaje_total_usuario.md.
`corte` es el instante del freeze: solo cuenta lo ocurrido hasta ese momento.
"""

from datetime import timedelta

from sqlmodel import Session

from itdb_ctf.core.puntaje_logic import puntaje_total_usuario
from itdb_ctf.db import engine

from conftest import (ahora, asociar, comprar, crear_evento, crear_pista, crear_reto,
                      crear_usuario, inscribir, resolver)


def puntaje(id_usuario, id_evento, corte=None):
    with Session(engine) as s:
        return puntaje_total_usuario(s, id_usuario, id_evento, corte)


def base(modo="estatico"):
    admin = crear_usuario("admin@itdonbosco.org", rol="admin")
    est = crear_usuario()
    ev = crear_evento(admin, "activo", modo=modo)
    inscribir(est, ev)
    return admin, est, ev


def test_C1_evento_inexistente():
    _, est, _ = base()
    assert puntaje(est, 9999) == 0


def test_C2_estatico_en_vivo():
    admin, est, ev = base()
    reto = crear_reto(admin)
    asociar(reto, ev, puntaje=100)
    resolver(est, reto, ev, correcta=False)          # los intentos fallidos no suman
    resolver(est, reto, ev, correcta=True)
    comprar(est, reto, ev, crear_pista(reto, 30), 30)
    assert puntaje(est, ev) == 70                     # 100 − 30


def test_C3_estatico_congelado():
    admin, est, ev = base()
    corte = ahora() - timedelta(hours=1)
    reto_a, reto_b = crear_reto(admin), crear_reto(admin)
    asociar(reto_a, ev, puntaje=100)
    asociar(reto_b, ev, puntaje=100)
    resolver(est, reto_a, ev, fecha=corte - timedelta(hours=1))      # antes del corte
    resolver(est, reto_b, ev, fecha=corte + timedelta(minutes=30))   # después: no cuenta
    comprar(est, reto_b, ev, crear_pista(reto_b, 30), 30,
            fecha=corte + timedelta(minutes=10))                     # después: no cuenta
    assert puntaje(est, ev, corte) == 100
    assert puntaje(est, ev) == 170                    # en vivo sí cuenta todo


def test_C4_dinamico_en_vivo():
    admin, est, ev = base("dinamico")
    reto = crear_reto(admin)
    asociar(reto, ev, modo="dinamico", puntaje=500, minimo=100, actual=480)
    resolver(est, reto, ev)
    assert puntaje(est, ev) == 480                    # usa Contiene.puntaje_actual


def test_C5_dinamico_congelado_recalcula_decay():
    admin, est, ev = base("dinamico")
    otro1 = crear_usuario("otro1@itdonbosco.org")
    otro2 = crear_usuario("otro2@itdonbosco.org")
    corte = ahora() - timedelta(hours=1)
    reto = crear_reto(admin)
    asociar(reto, ev, modo="dinamico", puntaje=500, minimo=100, actual=300)
    resolver(est, reto, ev, fecha=corte - timedelta(hours=2))
    resolver(otro1, reto, ev, fecha=corte - timedelta(hours=1))
    resolver(otro2, reto, ev, fecha=corte + timedelta(minutes=30))   # después: no cuenta
    # 2 resoluciones hasta el corte → formula_dinamic(500, 100, 1) = 499
    assert puntaje(est, ev, corte) == 499


def test_C6_dinamico_congelado_sin_resoluciones():
    admin, est, ev = base("dinamico")
    corte = ahora() - timedelta(hours=1)
    reto = crear_reto(admin)
    asociar(reto, ev, modo="dinamico", puntaje=500, minimo=100)
    resolver(est, reto, ev, fecha=corte + timedelta(minutes=30))     # solo después del corte
    assert puntaje(est, ev, corte) == 0


def test_C7_piso_cero():
    admin, est, ev = base()
    reto = crear_reto(admin)
    asociar(reto, ev, puntaje=100)
    resolver(est, reto, ev)
    comprar(est, reto, ev, crear_pista(reto, 150), 150)
    assert puntaje(est, ev) == 0                      # 100 − 150 = −50 → 0
