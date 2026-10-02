"""Caja blanca — core/rate_limit.permitir_flag  (V(G) = 4).

Análisis completo en tests/docs/caja_blanca_06_permitir_flag.md.
Límite: 15 envíos por (usuario, reto) en una ventana de 60 s.
"""

import time

import pytest

from itdb_ctf.core import rate_limit
from itdb_ctf.core.rate_limit import permitir_flag
from itdb_ctf.websockets import redis_cliente


def test_C1_sin_redis_permite():
    redis_cliente._estado = False                       # Redis marcado como caído
    redis_cliente._ultimo_sondeo = time.monotonic() + 10**9
    for _ in range(20):                                 # más que el límite
        assert permitir_flag(1, 1) == (True, 0)         # fail-open


@pytest.mark.parametrize("intentos", [1, 15], ids=["primer_intento", "intento_15_limite"])
def test_C2_dentro_del_limite(intentos):
    for _ in range(intentos - 1):
        permitir_flag(1, 1)
    assert permitir_flag(1, 1) == (True, 0)


def test_C3_supera_limite():
    for _ in range(15):
        permitir_flag(1, 1)
    ok, espera = permitir_flag(1, 1)                    # intento 16
    assert ok is False
    assert 1 <= espera <= 60
    assert permitir_flag(1, 2) == (True, 0)             # otro reto: contador aparte


def test_C4_supera_limite_y_falla_la_consulta_del_ttl(monkeypatch):
    for _ in range(15):
        permitir_flag(1, 1)
    monkeypatch.setattr(rate_limit, "_redis_peek", lambda clave: None)   # Redis cae justo aquí
    assert permitir_flag(1, 1) == (False, 60)           # usa la ventana completa
