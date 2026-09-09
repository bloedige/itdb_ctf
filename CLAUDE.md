# CLAUDE.md — ITDB CTF

Plataforma **Capture The Flag** institucional del Instituto Tecnológico Don Bosco
(El Alto – La Paz, Bolivia). Proyecto de grado. Toda la UI y el dominio están en
español; escribe código, nombres y mensajes en español para mantener consistencia.

Dos experiencias de jugador:
- **Evento abierto**: existe uno solo, sin fechas, práctica libre permanente.
  Inscripción automática. Puntaje siempre estático.
- **Eventos cerrados**: competencias con ventana `fec_inicio`/`fec_fin`. Inscripción
  por admin o auto-servicio. Pueden usar puntaje dinámico (curva tipo CTFd).

---

## Stack y entorno

- **Reflex 0.9.4** (framework full-stack en Python; frontend React compilado + backend
  FastAPI/Starlette), **SQLModel 0.0.38**, **PostgreSQL** (`psycopg2-binary`),
  **Alembic 1.18.4**, **PyJWT**, **bcrypt**, **google-auth-oauthlib** (OAuth2 Google),
  **FastAPI** montado dentro de Reflex, plugin **TailwindV4**.
- **Python 3.14**, virtualenv en `iTDB_CTF/.venv/`.
- `requirements.txt` solo fija `reflex==0.9.4`; el resto de dependencias vive en el
  venv. Si algún día se toca el deploy, conviene fijarlas — no hace falta ahora.
- Secretos y config en `iTDB_CTF/.env` (git-ignored): `DATABASE_URL`, credenciales
  del superadmin seed, Google OAuth (`GOOGLE_CLIENT_ID/SECRET/REDIRECT_URI`,
  `ALLOWED_EMAIL_DOMAIN=itdonbosco.org`), `JWT_SECRET_KEY` / `JWT_ALGORITHM` /
  `JWT_EXPIRE_MINUTES`, y rutas de archivos `RUTA_ARCHIVOS_RETO` /
  `RUTA_ARCHIVOS_AVATAR` (apuntan a `../FILES_ITDB_CTF/`).

---

## Layout del repo (¡ojo con la anidación!)

```
E:\proyecto de grado ITDB-CTF\
├── FILES_ITDB_CTF\            # almacenamiento físico de archivos de retos/avatares
├── *.md                       # docs de diseño / backlog (backlog_final.md, etc.)
└── iTDB_CTF\                  # RAÍZ del proyecto Reflex (aquí vive .git)
    ├── .env  rxconfig.py  alembic.ini  requirements.txt  settings.py
    ├── alembic\versions\      # migraciones
    ├── scripts\seed.py        # seed idempotente
    ├── assets\                # logos, favicon, isotipo.svg, fondo.png
    └── ITDB_CTF\              # == el paquete Python `itdb_ctf`
        ├── itdb_ctf.py        # ensamblado: importa states+pages, registra rutas
        ├── api.py             # sub-app FastAPI + `app = rx.App(api_transformer=...)`
        ├── db.py              # engine SQLModel único compartido
        ├── models.py          # 19 tablas SQLModel
        ├── auth\              # jwt_utils, oauth, local_auth, auth_logic,
        │                      #   auth_state (BASE de todos los states),
        │                      #   local_auth_state, local_auth_view
        ├── core\              # envio_logic, puntaje_logic, compra_logic
        ├── components\        # navbar (3 variantes), form (inputs/toasts), filtros
        ├── pages\             # componentes de ruta (delgados: navbar + un _view)
        ├── utils\             # security (hashers), validaciones (regex email)
        └── <feature>\         # informacion, catalogo, scoreboard, evento,
                               #   reto, asociar, usuario, inscripcion,
                               #   auto_inscripcion, evento_cerrado
```

- La carpeta `ITDB_CTF` se importa como `itdb_ctf` (case-insensitive en Windows);
  `app_name="itdb_ctf"` en `rxconfig.py`.
- `working directory` habitual de Claude Code: `iTDB_CTF\ITDB_CTF\`. Los comandos de
  abajo se corren desde `iTDB_CTF\` (donde está `rxconfig.py`).

---

## Comandos

Desde `E:\proyecto de grado ITDB-CTF\iTDB_CTF\` (activar `.venv` primero):

- **Correr la app**: `reflex run` — frontend en `:3000`, backend en `:8000`.
- **Migraciones**: `alembic upgrade head` · `alembic revision --autogenerate -m "..."`
  (`alembic/env.py` usa `SQLModel.metadata` + el engine de `itdb_ctf.db`).
- **Seed inicial**: `python scripts/seed.py` — idempotente (`get_or_create`); crea
  catálogos, el superadmin local (desde `.env`) y el evento abierto permanente.
- **No hay** tests ni linter configurados.

---

## Patrón de código — SEGUIR SIEMPRE

Cada feature se parte en 3 archivos:

| Archivo | Rol | Reglas |
|---|---|---|
| `*_logic.py` | Funciones puras de BD/negocio | Abren su propio `with Session(engine) as s:` y hacen `s.commit()` explícito. **Sin Reflex.** Devuelven `tuple[bool, str]` o dicts/listas de dicts para la UI. |
| `*_state(s).py` | Clases `State` de Reflex | Heredan de `AuthState`. Guardan estado de UI, llaman a `_logic`. Guard al inicio de cada handler: `guard = self.requiere_staff(); if guard: return guard`. |
| `*_view.py` | Componentes Reflex | Reutilizar helpers de `components/form.py` (`input_box`, `select_catalog`, `text_area`, `button`, `toast_msg`, `success_msg`, `card_text`, ...). |

- Rutas se registran **solo** en `itdb_ctf.py` vía `app.add_page(fn, route=..., on_load=...)`.
  Los guards de acceso viven en los handlers de `on_load`.
- `models.py` **no** usa `Relationship()`; todos los joins son explícitos en las queries.
- Feedback al usuario: `rx.toast` / `toast_msg` / `success_msg`.
- Catálogos para `rx.select` se pasan como `list[tuple[str_value, str_label]]`, con
  frecuencia prefijados con `("", "Todos")`.

---

## Modelo de datos (`models.py`)

**Catálogos**: `Rol` (códigos `superadmin` > `admin` > `autor` > `user`),
`Categoria`, `Dificultad`, `ModoPuntaje` (`estatico`/`dinamico`),
`Modalidad` (`abierto`/`cerrado`), `EstadoInscripcion` (`inscrito`/`descalificado`),
`EstadoWriteup`, `MetodoAuth` (`google`/`local`).

**Entidades**:
- `Usuario` — `id_rol`, `id_metodo_auth`, nombre/paterno/materno, `alias`,
  `password_hash` CHAR(60) bcrypt (NULL para cuentas Google), `email_inst` único,
  `activo`.
- `Evento` — `id_modalidad`, `id_modo_puntaje`, `titulo`, `fec_inicio`/`fec_fin`
  (**ambas NULL ⇒ es el evento abierto singleton**), `freeze` (congelar scoreboard),
  `auto_inscripcion`, `activo`.
- `Reto` — `id_categoria`, `id_dificultad`, `id_modo_puntaje`, `flag` CHAR(64)
  (**hash SHA-256 hex**, nunca texto plano), `puntaje_inicial`, `puntaje_minimo`,
  `archivo_original` (nombre amigable) / `archivo_ruta` (nombre físico en disco).
- `Pista` — `id_reto`, `costo`, `descripcion`, `activo`.
- `Writeup` — `id_reto`, `id_usuario`, `id_estado_writeup` (feature poco desarrollada).

**Asociativas — el corazón del dominio**:
- **`Contiene`** — un `Reto` colocado dentro de un `Evento`, con su **propio**
  `id_modo_puntaje`, `puntaje_inicial`, `puntaje_minimo`, `puntaje_actual`.
  Un reto es reutilizable entre eventos; **el puntaje efectivo siempre vive aquí**,
  no en `Reto`.
- **`Resuelve`** — envío de flag, alcance `(id_usuario, id_reto, id_evento)`,
  `flag_correcta`, `dir_ip` (INET), `fec_envio`. Se inserta fila **en cada intento**.
- **`Participa`** — inscripción a evento: `id_estado_inscripcion`, `fec_ingreso`.
- **`Compra`** — compra de pista `(id_usuario, id_reto, id_evento, id_pista)`,
  `puntos_usados`.

`models.py` divergió de la migración inicial (`puntaje_override`, `puntos` ya no
existen; `flag` pasó de CHAR(60) a CHAR(64)). Revisar siempre el diff al autogenerar.

---

## Auth y autorización

Dos flujos de login, ambos terminan en un **JWT en cookie `token`** (`max_age=3600`,
HS256, payload `{sub, rol, iat, exp}`):

- **Local**: form en `/login` → `LocalAuthState.entrar_local` →
  `verificar_credenciales` (bcrypt, solo cuentas `metodo_auth="local"` y `activo`) →
  `emitir_jwt`. `user` → `/informacion`; staff → `/admin/retos`.
- **Google OAuth2**: botón → `GET /auth/login` (FastAPI, setea cookie `oauth_state`) →
  Google → `GET /auth/callback` (verifica CSRF `oauth_state`) → `canjear_codigo` →
  `obtener_crear_usuario` (valida dominio `@itdonbosco.org`; crea cuenta rol `user`
  o rellena una cuenta *placeholder*; auto-inscribe al evento abierto) → `emitir_jwt`.
  PKCE está desactivado a propósito en `oauth.py`.

**`AuthState`** (`auth/auth_state.py`) es la **clase base de todos los states**.
`@rx.var` de solo lectura: `payload`, `autenticado`, `id_usuario`, `codigo_rol`
(hace consulta a BD en cada lectura → cambios de rol/baja surten efecto inmediato),
`es_staff` (`{superadmin, admin, autor}`), `es_admin` (`{superadmin, admin}`).
Handlers-guard que devuelven `rx.redirect`: `requiere_login`, `requiere_staff`,
`requiere_admin`, más `logout`. **No hay middleware global**: el guard se repite en
cada `on_load` y en cada event handler que lo necesite.

- `/admin/retos` → `requiere_staff` (autor incluido; el autor solo ve/edita sus retos
  vía `puede_editar`).
- `/admin/eventos`, `/admin/asociar`, `/admin/usuarios`, `/admin/inscribir` →
  `requiere_admin`.
- Eventos cerrados: `evento_cerrado_logic.acceso_evento_cerrado` (evento `activo` +
  modalidad `cerrado` + dentro de ventana + `Participa` inscrito + no `descalificado`).
- Gestión de usuarios: `RANGO = {superadmin:3, admin:2, autor:1, user:0}` en
  `usuario_logic.py`; `puede_gestionar` exige rango **estrictamente mayor** para tocar
  a otros; solo se gestionan cuentas `local`. `roles_asignables` impide crear/asignar
  un rol ≥ al propio (superadmin exento).

---

## Flujos clave

- **Ciclo de un reto**: crear en `/admin/retos` (`crear_reto` hashea la flag y crea
  el 1er `Contiene` + pistas + archivo opcional) → reutilizar en más eventos vía
  `/admin/asociar` (`asociar_reto` crea `Contiene` con modo/puntaje por evento) →
  editar/quitar de un evento **solo si ese evento está `futuro`**; en el evento
  abierto los retos son permanentes.
- **Envío de flag** (`core/envio_logic.enviar_flag`): reto activo → pertenece al
  evento (`Contiene`) → evento en ventana → usuario con `Participa` estado `inscrito`
  → sin `Resuelve` correcto previo (anti-resubmit) → compara SHA-256 → inserta
  `Resuelve` → si correcta, `refrescar_puntaje` recalcula `Contiene.puntaje_actual`.
- **Puntaje** (`core/puntaje_logic`): `puntaje_total_usuario` = Σ
  `Contiene.puntaje_actual` de retos resueltos − Σ `Compra.puntos_usados`, con piso 0.
  Dinámico = `formula_dinamic` (decay tipo CTFd, `decay=20`) **solo si el evento Y el
  `Contiene` son `dinamico`**; si cualquiera es `estatico`, puntaje fijo.
- **Compra de pista** (`core/compra_logic.adquirir_pista`): rechaza si ya comprada o
  si `costo > saldo`; inserta `Compra` con `puntos_usados = pista.costo`.
- **Scoreboard**: `ScoreboardState` sirve **tanto** `/scoreboard` como
  `/evento/{id}/scoreboard` (lee el param de ruta si existe, si no
  `id_evento_abierto()`). Auto-refresh en background cada 5 s.
- **Inscripción**: evento abierto = automática al crear cuenta / primer login
  (`auth_logic.auto_incripcion_evento_abierto`). Evento cerrado = auto-servicio en
  `/eventos` (si `Evento.auto_inscripcion`) o admin en `/admin/inscribir` (carrito
  individual, o CSV → valida dominio institucional → crea cuentas placeholder →
  `inscribir_lote`). `descalificado` bloquea acceso sin borrar la fila; el borrado
  duro de `Participa` solo se permite si el evento está `futuro`.

---

## Gotchas conocidos (documentados, no arreglados)

- **`core/envio_logic.py`**: los checks de ventana comparan la función
  `estado_evento` en vez de la variable `est_evento` → las ramas "futuro"/"concluido"
  nunca disparan. (Bug real.)
- **`auth/jwt_utils.py`**: lee `JWT_EXPIRE_MINUTE` pero `.env` define
  `JWT_EXPIRE_MINUTES` → siempre usa el default de 60 min.
- **`settings.py`**: typos `os.enviorn` y `GOOGLE_CLIENT_SECRTET`; el módulo parece no
  usarse (los módulos de auth leen `os.environ` directamente).
- **`auth/local_auth_view.py`**: el input de contraseña liga su `value` a
  `LocalAuthState.email`.
- **Cookie `token`**: sin `HttpOnly` / `Secure` / `SameSite` (hay `TODO` en `api.py`).
- **URLs hardcodeadas** `localhost:3000` / `localhost:8000` en `api.py` y
  `local_auth_view.py`.
- **`estado_evento` duplicada** en `evento_logic.py`, `asociar_logic.py` e
  `inscripcion_logic.py`, con etiquetas ligeramente inconsistentes (`activo` vs
  `abierto`). Al tocar lógica de estado de evento, unificar con cuidado.
- `pages/retos.py` existe pero no se registra; `/perfil` se enlaza en el navbar pero
  no hay página; `EventoCerradoPerfilState.caragar_perfil` es un stub.
- Creación de cuenta / reset de password devuelven la contraseña en texto plano a la
  UI del admin (`secrets.token_hex(8)`).

---

## Gotchas de Reflex

- El paquete se importa `itdb_ctf` aunque la carpeta sea `ITDB_CTF`.
- Reflex tiene su propio `db_url` en `rxconfig.py`, pero la app **no** usa
  `rx.Model` / `rx.session`: usa SQLModel crudo con el engine de `db.py`.
- `on_load` acepta un handler o una lista de handlers.
- Salidas de build git-ignored: `.web/`, `.states/`, `reflex.lock/`, `.env`,
  `__pycache__/`, `assets/external/`.

---

## Convenciones de commits

Mensajes de commit en español, cortos, estilo de los existentes
(`autoinscripcion + ventanas evento cerrado`, `fix scoreboard`, `compra de pistas`).
Rama principal: `main`. Solo commitear/pushear cuando el usuario lo pida.
