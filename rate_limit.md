## rate_limit.md — Rate limiting de la plataforma ITDB CTF

Manual del **tope de intentos por ventana de tiempo** en **login** y **envío de
flag**. Complementa a `CLAUDE.md` y a `reddis.md` (comparte la infraestructura
Redis de este último). Se construye sobre `itdb_ctf/core/rate_limit.py`.

**Estado:** ✅ implementado y verificado (Memurai + simulación de Redis caído).

---

## 0. Por qué

Sin un tope de intentos, dos acciones de la plataforma son abusables:

### Login

`verificar_credenciales` corre **bcrypt** (~100 ms por intento, lento **a
propósito** para resistir fuerza bruta). El backend de Reflex corre en **un solo
proceso** (state manager DISK, sin workers). Entonces:

- Un script que prueba `estudiante1@itdonbosco.org` con 10 000 contraseñas ocupa
  el proceso ~100 ms por intento.
- Mientras tanto **el resto de usuarios queda esperando** → la plataforma se
  siente colgada. Es un DoS de facto.
- Los correos institucionales son predecibles (`nombre.apellido@itdonbosco.org`),
  así que el atacante sabe a quién apuntar.

### Envío de flag

`enviar_flag` inserta una fila en la tabla **`Resuelve` en cada intento**. Sin
tope:

- Un script mete miles de filas basura → ensucia la BD, el feed de resoluciones
  del dashboard y las estadísticas.
- Si algún reto tiene una flag débil (`flag{admin}`, un PIN de 4 dígitos), se
  puede adivinar probando rápido. Defensa en profundidad.

*(El puntaje dinámico NO se ve afectado por intentos fallidos: el decay solo cuenta
`Resuelve` correctos.)*

---

## 1. Qué hace

| Punto | Clave Redis | Tope | Cuenta… |
|---|---|---|---|
| Login | `itdb:rl:login:acc:{email}` | **8 / 10 min** | solo intentos **fallidos** |
| Login | `itdb:rl:login:ip:{ip}` | **50 / 10 min** | solo intentos **fallidos** |
| Envío de flag | `itdb:rl:flag:{id_usuario}:{id_reto}` | **15 / min** | **todos** los intentos |

Al pasarse:
- **Login** → `rx.toast.error("Demasiados intentos fallidos. Reintentá en N s.")`
- **Flag** → `enviar_flag` devuelve `(False, "Demasiados intentos. Esperá N s.")`

Un usuario normal nunca se acerca a estos números. Solo frena scripts.

---

## 2. Cómo funciona

Contador de **ventana fija en Redis**, atómico (pipeline transaccional):

```python
pipe = cli.pipeline(transaction=True)
pipe.incr(clave)                       # +1, crea la clave si no existía
pipe.expire(clave, ventana, nx=True)   # fija el TTL SOLO la primera vez (NX)
n, _ = pipe.execute()
```

- **`INCR`** crea la clave en 0 y la sube a 1 en el primer intento; de ahí en más
  suma. Es atómico, no hay carrera entre dos requests.
- **`EXPIRE ... NX`** pone el "se borra en `ventana` segundos" **una sola vez**
  (`NX` = *only if it has no TTL*). Así el bloqueo **nunca dura más que la
  ventana** aunque el atacante siga insistiendo: no se renueva el TTL.
- El contador **se limpia solo** cuando expira. **No hay tabla, ni migración, ni
  cron.**

`ttl(clave)` da los segundos que faltan para que se libere → es el "Reintentá en
N s" del mensaje.

---

## 3. Login = **solo cuenta intentos fallidos**  ← lo importante

El contador de login **solo sube cuando la contraseña es incorrecta**. Un login
**exitoso** llama `limpiar_login(ip, email)` y **borra los dos contadores**.

### Por qué

Un límite por IP asume *"1 IP ≈ 1 persona"*. **Es falso en dos casos muy comunes:**

1. **Desarrollo:** el navegador, el backend y la BD corren en la misma PC → el
   servidor ve **siempre `127.0.0.1`**, sin importar la cuenta.
2. **NAT / proxy institucional:** los ~200 alumnos del ITDB salen a internet por
   **una sola IP pública**. Para el servidor, todos son la misma IP.

Si se contaran **todos** los logins (buenos incluidos), esa IP compartida
reventaría cualquier tope razonable en el primer recreo. Contando **solo fallos**:

- 200 alumnos entrando bien a las 9:00 AM → contador de IP = **0**. No molesta.
- Un script probando 50 contraseñas equivocadas desde algún lado → contador = 50 →
  **bloqueado 10 min**. Funciona.

El tope **realmente útil** es el **por cuenta** (8 fallos / 10 min): protege contra
fuerza bruta dirigida a una persona, y no le afecta la IP compartida. El tope por
IP (50) es solo una red de seguridad contra un script que barre muchas cuentas.

---

## 4. Sin Redis (degradación)

| | Comportamiento |
|---|---|
| **Login** | Respaldo **en memoria del proceso**: un `dict[str, deque]` de *timestamps* por clave. Como el backend es **mono-proceso**, ese diccionario ve *todos* los intentos → el rate limit **sigue aplicando**. Se pierde al reiniciar el backend (irrelevante para un ataque sostenido, que dura minutos/horas). Poda defensiva: si el dict pasa de 10 000 claves, se vacía. |
| **Envío de flag** | **Fail-open**: se permite el intento. Igual que el resto de features que dependen de Redis (scoreboard, freeze…). Que alguien mande flags de más un rato mientras Redis está caído no es un problema. |

La detección de "¿hay Redis?" es la misma de `websockets/redis_cliente.py`
(`get_sync()` devuelve `None` al instante si Redis está marcado como caído).

---

## 5. El módulo `itdb_ctf/core/rate_limit.py`

Función pura, sync, sin Reflex. Importa `get_sync` / `marcar_caido` de
`websockets/redis_cliente.py` (esa flecha `core → websockets` ya existía).

### Constantes (ajustar acá)

```python
LOGIN_CUENTA = (8, 600)    # (cantidad_de_FALLOS, ventana_seg)
LOGIN_IP     = (50, 600)
FLAG         = (15, 60)     # (intentos_totales, ventana_seg)
```

### API pública

| Función | Devuelve | Uso |
|---|---|---|
| `login_bloqueado(ip, email)` | `(bloqueado: bool, seg_restantes: int)` | **Solo lee.** Al inicio de `entrar_local`. |
| `registrar_fallo_login(ip, email)` | — | Suma 1 a IP y cuenta. Tras credenciales inválidas. |
| `limpiar_login(ip, email)` | — | Borra ambos contadores. Tras un login exitoso. |
| `permitir_flag(id_usuario, id_reto)` | `(permitido: bool, seg_restantes: int)` | Al inicio de `enviar_flag`. Incrementa siempre. |

### Estructura interna

- `_redis_incr(clave, ventana)` → `int | None` — el `INCR` + `EXPIRE NX`; `None` si no hay Redis.
- `_redis_peek(clave)` → `(conteo, ttl) | None` — lee sin incrementar.
- `_redis_del(*claves)` — borrado tolerante a fallo.
- `_memoria_peek` / `_memoria_incr` / `_memoria_del` — la capa de respaldo (deque de `time.monotonic()`).
- Todo `except Exception` llama `marcar_caido()` y degrada.

---

## 6. Integración

### `auth/local_auth_state.py :: entrar_local`

```python
def entrar_local(self):
    ip = self.router.session.client_ip or "desconocida"
    bloqueado, faltan = login_bloqueado(ip, self.email)     # 1. solo lee
    if bloqueado:
        return rx.toast.error(f"Demasiados intentos fallidos. Reintentá en {faltan} s.")
    usuario = verificar_credenciales(self.email, self.password)  # 2. bcrypt
    if not usuario:
        registrar_fallo_login(ip, self.email)              # 3. suma el fallo
        return rx.toast.error("Credenciales inválidas.")
    limpiar_login(ip, self.email)                          # 4. login OK -> limpia
    self.token = emitir_jwt(usuario)
    ...
```

- **IP**: `self.router.session.client_ip`. Reflex ya desenrolla `X-Forwarded-For`,
  así que detrás del reverse proxy del VPS devuelve la IP real del cliente.
- De paso se arregló un bug pre-existente: el mensaje de credenciales inválidas
  usaba `badge_msg("Credenciales invalidas.")` con **un argumento de menos**
  (`badge_msg(msg, color)` exige `color`) → `TypeError` en **cada** contraseña
  equivocada. Ahora es `rx.toast.error`.

### `core/envio_logic.py :: enviar_flag`

```python
def enviar_flag(id_usuario, id_reto, id_evento, flag_enviada, dir_ip=None):
    ok, faltan = permitir_flag(id_usuario, id_reto)
    if not ok:
        return False, f"Demasiados intentos. Esperá {faltan} s."
    with Session(engine) as s:
        ...
```

El chequeo va **dentro de la función `_logic`** (que ya recibe `id_usuario` e
`id_reto`), así cubre a **los dos callers** —
`catalogo/catalogo_states.py` y `evento_cerrado/evento_cerrado_reto_state.py` —
sin tocarlos.

### Lo que NO se tocó

**Sin** migración · **sin** cambios en `models.py`, `rxconfig.py` ni la BD.

---

## 7. Operación

### Inspeccionar los contadores

```
memurai-cli --scan --pattern 'itdb:rl:*'
memurai-cli GET  itdb:rl:login:acc:alguien@itdonbosco.org
memurai-cli TTL  itdb:rl:login:ip:200.58.x.x
```

### Desbloquear a mano (soporte / dev)

```
memurai-cli DEL itdb:rl:login:acc:alguien@itdonbosco.org
memurai-cli DEL itdb:rl:login:ip:200.58.x.x
```

El respaldo en memoria (cuando Redis está caído) se limpia **reiniciando el
backend** (`reflex run`).

### Cambiar los topes

Editar las constantes en `core/rate_limit.py` y reiniciar el backend. No hace
falta tocar Redis (las claves viejas expiran solas).

### Deploy en el VPS

- Requiere que el reverse proxy (nginx/caddy) mande `X-Forwarded-For` — es lo
  habitual; sin eso, todas las IPs se ven como la del proxy y el tope por-IP se
  comportaría como en dev (poco grave: el tope por-cuenta sigue siendo el que
  protege).
- El respaldo en memoria deja de ser fiable si algún día el backend corre con
  varios workers. Con Redis levantado no importa.

---

## 8. Incidente resuelto: "todas las cuentas aparecían bloqueadas en dev"

**Síntoma:** tras un rato probando el login, *ninguna* cuenta podía entrar; todas
mostraban el aviso de rate limit.

**Causa:** la primera versión tenía dos fallos de diseño:

1. Contaba **todos** los intentos de login, no solo los fallidos.
2. El tope por IP (entonces 15 / 5 min) asumía "1 IP = 1 persona". En dev **todas**
   las peticiones salen de `127.0.0.1`, así que había **un solo contador
   compartido** entre todas las cuentas. Al pasar de 15, **cualquier** login desde
   `127.0.0.1` quedaba rechazado — daba igual la cuenta.

Las claves en Redis al momento del diagnóstico lo confirmaron:

```
itdb:rl:login:ip:127.0.0.1     = 25   (límite 15)  ← bloqueaba a todos
itdb:rl:login:acc:admin@admin  = 22   (límite 6)   ← esa cuenta, genuinamente
```

**Arreglo:**
- Login pasa a contar **solo fallos**; un login OK borra los contadores.
- Tope por IP subido a 50 fallos / 10 min (red de seguridad, no límite principal).
- El límite que protege de verdad es el **por cuenta** (8 fallos / 10 min).
- Se limpiaron las claves atascadas.

**Lección:** un rate limit por IP es engañoso siempre que haya NAT o proxy entre
el usuario y el servidor — que es casi siempre (redes escolares, oficinas, dev
local). El límite por identidad (cuenta) es el que hay que afinar.

---

## 9. Verificación

- **Cuenta:** al 8º fallo → `(True, 600)`. Un login correcto después limpia →
  `(False, 0)`.
- **NAT:** 30 logins **exitosos** desde la misma IP → **no bloquea**.
- **Flag:** intento 16+ dentro del minuto → `(False, 60)`.
- **Redis caído** (`_estado = False` forzado): el tope de login sigue aplicando
  por la capa en memoria; `permitir_flag` devuelve siempre `(True, 0)` (fail-open).
- `import itdb_ctf.itdb_ctf` OK · `reflex export --frontend-only` compila.

---

## 10. No cubierto (a propósito)

- **Rate limit en el callback de Google OAuth** (`/auth/callback`, FastAPI). Google
  ya hace la autenticación; el callback solo hace un *upsert* de usuario. Prioridad
  baja. Si se quisiera: contar por `request.client.host` ahí también.
- **Rate limit en creación de cuentas / reset de password** (panel admin). Son
  acciones detrás de `requiere_admin`, el riesgo es bajo.
- **Bloqueo persistente / captcha / backoff exponencial.** Overkill para un CTF
  escolar; la ventana fija cumple.
