"""Moderación de textos que el usuario elige libremente (alias y, para staff,
nombre/paterno/materno).

Funciones puras, sin Reflex ni BD. La verificación es un filtro local best-effort:
formato + nombres reservados + lista negra de lenguaje ofensivo, con tolerancia a
trucos comunes (acentos, leetspeak `4dm1n`, repeticiones `puuta`). No pretende ser
infalible ("poco probable pero no imposible"); un admin siempre puede corregir un
alias desde `/admin/usuarios`.
"""

import re
import unicodedata

ALIAS_MIN = 3
ALIAS_MAX = 30          # == max_length de Usuario.alias
NOMBRE_MAX = 50         # == max_length de Usuario.nombre / paterno / materno

# Alias visible: letras (incl. acentos y ñ), dígitos, espacio y . _ -
_ALIAS_VISIBLE = re.compile(r"[A-Za-zÀ-ÿ0-9 ._-]+")
_SEPARADORES = " ._-"

# Nombre real: letras (con acentos y ñ), espacio, apóstrofo y guion.
_NOMBRE_VISIBLE = re.compile(r"[A-Za-zÀ-ÿ' -]+")

_LEET = str.maketrans({
    "0": "o", "1": "i", "3": "e", "4": "a", "5": "s",
    "7": "t", "8": "b", "@": "a", "$": "s", "!": "i",
})

# Palabras que nadie puede tomar como alias (suplantación de la plataforma / staff).
RESERVADAS = frozenset({
    "admin", "administrador", "administrator", "superadmin", "superadministrador",
    "superusuario", "root", "sysadmin", "moderador", "mod", "staff", "soporte",
    "support", "sistema", "system", "null", "none", "undefined",
    "itdb", "itdbctf", "itdonbosco", "donbosco", "bosco", "ctf",
    "anonimo", "anonymous", "usuario", "user", "invitado", "guest",
})

# Lista negra de lenguaje ofensivo (español + jerga boliviana + slurs frecuentes),
# ya en forma "plegada" (minúsculas, sin acentos, sin separadores). Editable.
PALABRAS_PROHIBIDAS = frozenset({
    # insultos / vulgaridades
    "puta", "puto", "putos", "putas", "putazo", "putamadre", "hijodeputa", "hdp",
    "mierda", "cagada", "cagon", "carajo", "coño", "cono", "verga", "vergon",
    "pendejo", "pendeja", "pelotudo", "boludo", "gil", "imbecil", "idiota",
    "estupido", "estupida", "tarado", "cojudo", "cojuda", "conchudo",
    "concha", "conchatumadre", "chucha", "chuchatumadre", "csm", "ctm",
    "culo", "culiao", "culero", "cabron", "cabrona", "maricon", "marica",
    "maraco", "joto", "trolo", "puñeta", "puneta", "pajero", "pajera",
    "follar", "coger", "cojer", "tirar", "garchar", "singar",
    "polla", "pija", "pito", "penetrar", "semen", "corrida",
    "teta", "tetas", "chichi", "pezon", "nalga", "nalgas",
    "orto", "poto", "trasero",
    "zorra", "perra", "golfa", "ramera", "prostituta", "prostituto",
    "cornudo", "malparido", "gonorrea", "chinga", "chingada", "chingar",
    "verguero", "kkk", "nazi", "hitler",
    # aimara / quechua vulgar de uso común
    "kaka", "jisqa", "qero", "supay",
    # sexual explícito / abuso
    "porno", "porn", "xxx", "sexo", "sexso", "violar", "violador", "pedofilo",
    "pedofilia", "zoofilia", "incesto", "nazi88",
    # slurs
    "negrata", "sudaca", "indio", "cholo", "cholito", "llama", "boliguayo",
    "retrasado", "mongolo", "mongol", "subnormal", "sidoso",
    "puton", "putona",
})


def _sin_acentos(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def _plegar(s: str) -> str:
    """Forma canónica para comparar contra listas: sin acentos, minúsculas,
    leet resuelto, solo [a-z0-9] y repeticiones colapsadas (`puuta` -> `puta`)."""
    s = _sin_acentos(s).lower().translate(_LEET)
    s = re.sub(r"[^a-z0-9]", "", s)
    s = re.sub(r"(.)\1+", r"\1", s)
    return s


def normalizar_alias(raw: str) -> str:
    """NFKC, sin caracteres de control/formato (incluye zero-width), espacios
    colapsados y recortados."""
    s = unicodedata.normalize("NFKC", raw or "")
    s = "".join(c for c in s if unicodedata.category(c)[0] != "C")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _tiene_ofensa(plegado: str) -> bool:
    if not plegado:
        return False
    if plegado in RESERVADAS:
        return True
    return any(mala in plegado for mala in PALABRAS_PROHIBIDAS)


def validar_alias(raw: str) -> tuple[bool, str]:
    """`(True, alias_normalizado)` o `(False, motivo)`."""
    alias = normalizar_alias(raw)
    if not alias:
        return False, "Escribe un alias."
    if not (ALIAS_MIN <= len(alias) <= ALIAS_MAX):
        return False, f"El alias debe tener entre {ALIAS_MIN} y {ALIAS_MAX} caracteres."
    if not _ALIAS_VISIBLE.fullmatch(alias):
        return False, "El alias solo admite letras, números, espacio y . _ -"
    if alias[0] in _SEPARADORES or alias[-1] in _SEPARADORES:
        return False, "El alias no puede empezar ni terminar con espacio, punto, guion o guion bajo."

    plegado = _plegar(alias)
    if not plegado:
        return False, "El alias debe contener al menos una letra o número."
    if plegado.isdigit():
        return False, "El alias no puede ser solo números."
    if plegado in RESERVADAS or any(r in plegado for r in RESERVADAS if len(r) >= 4):
        return False, "Ese alias está reservado."
    if any(mala in plegado for mala in PALABRAS_PROHIBIDAS):
        return False, "El alias contiene lenguaje ofensivo."
    return True, alias


def validar_nombre(raw: str, campo: str, *, obligatorio: bool) -> tuple[bool, str]:
    """Valida un componente del nombre real. Devuelve `(True, valor_limpio)` donde
    `valor_limpio` puede ser `""` si es opcional y vino vacío (el caller lo pasa a
    `None`)."""
    valor = re.sub(r"\s+", " ", (raw or "").strip())
    if not valor:
        if obligatorio:
            return False, f"El {campo} es obligatorio."
        return True, ""
    if len(valor) > NOMBRE_MAX:
        return False, f"El {campo} no puede superar los {NOMBRE_MAX} caracteres."
    if not _NOMBRE_VISIBLE.fullmatch(valor):
        return False, f"El {campo} solo admite letras, espacio, apóstrofo y guion."
    if _tiene_ofensa(_plegar(valor)):
        return False, f"El {campo} contiene lenguaje no permitido."
    return True, valor
