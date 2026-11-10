# Prueba de caja blanca 06 — `permitir_flag` (rate limit de flags)

- **Módulo:** `itdb_ctf/core/rate_limit.py`
- **Función:** `permitir_flag(id_usuario, id_reto) -> (permitido: bool, segundos_restantes: int)`
- **Propósito:** frenar la fuerza bruta de flags: máximo **15 envíos por minuto**
  por cada par (usuario, reto). El contador vive en Redis; si Redis no está, se
  permite el envío (*fail-open*) para no bloquear la competencia.
- **Técnica:** camino básico (McCabe) + cobertura de ramas con `pytest-cov`.
- **Archivo de pruebas:** `tests/test_06_permitir_flag.py`

---

## 1. Código fuente con nodos numerados

```python
177  def permitir_flag(id_usuario, id_reto):
178      clave = _clave_flag(id_usuario, id_reto)        # 1
179      limite, ventana = FLAG                          # 1   (15, 60)
180      n = _redis_incr(clave, ventana)                 # 1   suma 1 y devuelve el total
181      if n is None:                                   # 2   ¿Redis no disponible?
182          return True, 0                              # 3   fail-open
183      if n > limite:                                  # 4   ¿superó 15?
184          r = _redis_peek(clave)                      # 5   consulta cuánto falta
185          return False, (r[1] if r else ventana)      # 6 → 7 (r[1]) / 8 (ventana)
186      return True, 0                                  # 9
                                                         # 10 (fin)
```

La línea 185 contiene un `if` en una sola línea (operador ternario); McCabe lo
cuenta como un nodo predicado más (6).

## 2. Grafo de flujo

```mermaid
graph TD
    n1((1)) --- n2((2))
    n2 --- n3((3))
    n3 --- n10((10))
    n2 --- n4((4))
    n4 --- n5((5))
    n5 --- n6((6))
    n4 --- n9((9))
    n9 --- n10
    n6 --- n7((7))
    n7 --- n10
    n6 --- n8((8))
    n8 --- n10
```

**Convención del grafo:** las aristas no llevan flecha ni etiqueta; el flujo va de arriba hacia abajo y converge en los nodos de unión y en el nodo final (10). De cada nodo predicado salen dos aristas: la de la **izquierda** corresponde a la condición verdadera (**sí**) y la de la **derecha** a la falsa (**no**).

## 3. Complejidad ciclomática V(G)

| Método | Cálculo | Resultado |
|---|---|---|
| Nodos predicado | P = 3 (nodos 2, 4, 6) → V(G) = P + 1 | **4** |
| Aristas y nodos | E = 12, N = 10 → V(G) = 12 − 10 + 2 | **4** |
| Regiones | 3 cerradas + 1 exterior | **4** |

## 4. Caminos independientes

| Camino | Recorrido | Descripción |
|---|---|---|
| C1 | 1 → 2(sí) → 3 → 10 | Redis caído → se permite (fail-open) |
| C2 | 1 → 2(no) → 4(no) → 9 → 10 | Dentro del límite → se permite |
| C3 | … → 4(sí) → 5 → 6(sí) → 7 → 10 | Superó el límite → bloquea con el tiempo restante real |
| C4 | … → 4(sí) → 5 → 6(no) → 8 → 10 | Superó el límite y Redis falla al consultar el tiempo → bloquea 60 s |

Todos los caminos son factibles. C4 ocurre si Redis se cae justo entre el
conteo y la consulta del tiempo; en la prueba se simula reemplazando
`_redis_peek` por una función que devuelve `None` (técnica de *stub*).

### 4.1 Grafo de cada camino

En cada grafo se resalta en naranja el recorrido del camino (nodos y
aristas); el resto del grafo queda en gris como referencia. Cada nodo
(círculo) es una sentencia o grupo de sentencias, numerado según el código
de la sección 1; el nodo 10 es el nodo final. Se usa la misma convención de la
sección 2 (izquierda = sí, derecha = no); en el recorrido escrito bajo cada
grafo, `(sí)`/`(no)` indica la salida que toma cada nodo predicado.

**C1 — Redis caído → se permite (fail-open)**

`1 → 2(sí) → 3 → 10`

```mermaid
graph TD
    n1((1)) --- n2((2))
    n2 --- n3((3))
    n3 --- n10((10))
    n2 --- n4((4))
    n4 --- n5((5))
    n5 --- n6((6))
    n4 --- n9((9))
    n9 --- n10
    n6 --- n7((7))
    n7 --- n10
    n6 --- n8((8))
    n8 --- n10
    classDef default fill:#f5f5f5,stroke:#9e9e9e,color:#757575
    classDef camino fill:#ffe082,stroke:#e65100,stroke-width:2px,color:#000
    class n1,n2,n3,n10 camino
    linkStyle default stroke:#bdbdbd,stroke-width:1px
    linkStyle 0,1,2 stroke:#e65100,stroke-width:3px
```

**C2 — Dentro del límite → se permite**

`1 → 2(no) → 4(no) → 9 → 10`

```mermaid
graph TD
    n1((1)) --- n2((2))
    n2 --- n3((3))
    n3 --- n10((10))
    n2 --- n4((4))
    n4 --- n5((5))
    n5 --- n6((6))
    n4 --- n9((9))
    n9 --- n10
    n6 --- n7((7))
    n7 --- n10
    n6 --- n8((8))
    n8 --- n10
    classDef default fill:#f5f5f5,stroke:#9e9e9e,color:#757575
    classDef camino fill:#ffe082,stroke:#e65100,stroke-width:2px,color:#000
    class n1,n2,n4,n9,n10 camino
    linkStyle default stroke:#bdbdbd,stroke-width:1px
    linkStyle 0,3,6,7 stroke:#e65100,stroke-width:3px
```

**C3 — Superó el límite → bloquea con el tiempo restante real**

`1 → 2(no) → 4(sí) → 5 → 6(sí) → 7 → 10`

```mermaid
graph TD
    n1((1)) --- n2((2))
    n2 --- n3((3))
    n3 --- n10((10))
    n2 --- n4((4))
    n4 --- n5((5))
    n5 --- n6((6))
    n4 --- n9((9))
    n9 --- n10
    n6 --- n7((7))
    n7 --- n10
    n6 --- n8((8))
    n8 --- n10
    classDef default fill:#f5f5f5,stroke:#9e9e9e,color:#757575
    classDef camino fill:#ffe082,stroke:#e65100,stroke-width:2px,color:#000
    class n1,n2,n4,n5,n6,n7,n10 camino
    linkStyle default stroke:#bdbdbd,stroke-width:1px
    linkStyle 0,3,4,5,8,9 stroke:#e65100,stroke-width:3px
```

**C4 — Superó el límite y falla la consulta del tiempo → bloquea 60 s**

`1 → 2(no) → 4(sí) → 5 → 6(no) → 8 → 10`

```mermaid
graph TD
    n1((1)) --- n2((2))
    n2 --- n3((3))
    n3 --- n10((10))
    n2 --- n4((4))
    n4 --- n5((5))
    n5 --- n6((6))
    n4 --- n9((9))
    n9 --- n10
    n6 --- n7((7))
    n7 --- n10
    n6 --- n8((8))
    n8 --- n10
    classDef default fill:#f5f5f5,stroke:#9e9e9e,color:#757575
    classDef camino fill:#ffe082,stroke:#e65100,stroke-width:2px,color:#000
    class n1,n2,n4,n5,n6,n8,n10 camino
    linkStyle default stroke:#bdbdbd,stroke-width:1px
    linkStyle 0,3,4,5,10,11 stroke:#e65100,stroke-width:3px
```

## 5. Casos de prueba

Redis es reemplazado por `fakeredis` (Redis en memoria), que se vacía antes de
cada caso. Para C1 se marca Redis como caído.

C2 aplica **valor límite**: el 1.er intento y el 15.º (el último permitido).
C3 prueba el 16.º (el primero bloqueado) y además que otro reto tiene su propio
contador.

| Caso | Test | Recorrido | Precondición | Entrada | Esperado | Obtenido |
|---|---|---|---|---|---|---|
| C1 | `test_C1_sin_redis_permite` | 1 → 2 → 3 → 10 | Redis caído | 20 intentos | todos `(True, 0)` | Aprobado |
| C2a | `test_C2_dentro_del_limite[primer_intento]` | 1 → 2 → 4 → 9 → 10 | Contador en 0 | intento 1 | `(True, 0)` | Aprobado |
| C2b | `test_C2_dentro_del_limite[intento_15_limite]` | 1 → 2 → 4 → 9 → 10 | 14 intentos previos | intento 15 | `(True, 0)` | Aprobado |
| C3 | `test_C3_supera_limite` | 1 → 2 → 4 → 5 → 6 → 7 → 10 | 15 intentos previos | intento 16 | `(False, t)` con 1 ≤ t ≤ 60; otro reto sigue `(True, 0)` | Aprobado |
| C4 | `test_C4_supera_limite_y_falla_la_consulta_del_ttl` | 1 → 2 → 4 → 5 → 6 → 8 → 10 | 15 intentos previos, `_redis_peek` devuelve `None` | intento 16 | `(False, 60)` | Aprobado |

## 6. Resultados y cobertura

Ejecución: `pytest tests/test_06_permitir_flag.py --cov=itdb_ctf.core.rate_limit --cov-branch --cov-report=term-missing`
(2026-10-02, Python 3.14.5, pytest 9.1.1).

**5 de 5 casos aprobados.**

| Función | Sentencias cubiertas | Ramas parciales | Cobertura |
|---|---|---|---|
| `permitir_flag` (líneas 177–186) | 10 / 10 | 0 | **100 %** |

El reporte de `pytest-cov` muestra el archivo completo al 45 %: el resto del
archivo es el rate limit del **login** (`login_bloqueado`, `registrar_fallo_login`,
respaldo en memoria…), que no forma parte de esta prueba.

## 7. Resumen de caminos

Un caso por camino independiente (V(G) = 4). Límite: 15 envíos por par (usuario, reto) en una ventana de 60 s.

| Camino | Precondición | Entrada | Resultado esperado |
|---|---|---|---|
| C1 | Redis no disponible | `id_usuario = 1`, `id_reto = 1` | `(True, 0)` |
| C2 | Contador del par (1, 1) en 0 | `id_usuario = 1`, `id_reto = 1` | `(True, 0)` |
| C3 | 15 intentos del par (1, 1) en los últimos 60 s | `id_usuario = 1`, `id_reto = 1` | `(False, t)` con 1 ≤ t ≤ 60 |
| C4 | 15 intentos del par (1, 1) en los últimos 60 s; la consulta del tiempo restante en Redis falla | `id_usuario = 1`, `id_reto = 1` | `(False, 60)` |

## 8. Recorrido de cada camino

Caminos independientes del conjunto base (V(G) = 4).

| Camino | Recorrido |
|---|---|
| C1 | 1 - 2 - 3 - 10 |
| C2 | 1 - 2 - 4 - 9 - 10 |
| C3 | 1 - 2 - 4 - 5 - 6 - 7 - 10 |
| C4 | 1 - 2 - 4 - 5 - 6 - 8 - 10 |

## 9. Código numerado por nodos

Renglones numerados de forma correlativa desde 1; el comentario indica el nodo del grafo de flujo que ocupa cada renglón (`# nodo # nodo` cuando hay más de uno). El último nodo `(fin)` no ocupa renglón: es la salida común de todos los `return`.

```python
1   def permitir_flag(id_usuario, id_reto):
2       clave = _clave_flag(id_usuario, id_reto)        # 1
3       limite, ventana = FLAG                          # 1
4       n = _redis_incr(clave, ventana)                 # 1
5       if n is None:                                   # 2
6           return True, 0                              # 3
7       if n > limite:                                  # 4
8           r = _redis_peek(clave)                      # 5
9           return False, (r[1] if r else ventana)      # 6 # 7 # 8
10      return True, 0                                  # 9
                                                        # 10 (fin)
```
