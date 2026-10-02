"""Caja blanca — auth/local_auth.verificar_credenciales  (V(G) = 5).

Análisis completo en tests/docs/caja_blanca_04_verificar_credenciales.md.
"""

from itdb_ctf.auth.local_auth import verificar_credenciales
from itdb_ctf.utils.security import hasher

from conftest import crear_usuario

EMAIL = "estudiante@itdonbosco.org"
CLAVE = "Clave_Segura_2026"


def test_C1_email_no_registrado():
    assert verificar_credenciales("nadie@itdonbosco.org", CLAVE) is None


def test_C1b_cuenta_google_no_entra_por_login_local():
    crear_usuario(EMAIL, metodo="google")
    assert verificar_credenciales(EMAIL, CLAVE) is None


def test_C2_cuenta_local_sin_contrasena():
    crear_usuario(EMAIL, metodo="local", password_hash=None)     # cuenta placeholder
    assert verificar_credenciales(EMAIL, CLAVE) is None


def test_C3_cuenta_inactiva():
    crear_usuario(EMAIL, password_hash=hasher.hashear(CLAVE), activo=False)
    assert verificar_credenciales(EMAIL, CLAVE) is None


def test_C4_contrasena_incorrecta():
    crear_usuario(EMAIL, password_hash=hasher.hashear(CLAVE))
    assert verificar_credenciales(EMAIL, "otra_clave") is None


def test_C5_credenciales_correctas():
    id_usuario = crear_usuario(EMAIL, password_hash=hasher.hashear(CLAVE))
    usuario = verificar_credenciales(EMAIL, CLAVE)
    assert usuario is not None
    assert usuario.id_usuario == id_usuario
