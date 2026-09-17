import os
from dotenv import load_dotenv

import reflex as rx

load_dotenv()

# Variables opcionales: si no estan definidas se usa el valor de desarrollo.
# (os.environ[...] reventaba con KeyError en vez de tomar un valor por defecto.)
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "Falta DATABASE_URL: definila en .env o en las variables de entorno."
    )

# URL publica del backend. En dev el backend vive en :8000; en prod (single-port)
# es el dominio del sitio, p. ej. https://itdbctf.duckdns.org
API_URL = os.environ.get("API_URL") or "http://localhost:8000"

config = rx.Config(
    app_name="itdb_ctf",
    # configuramos la url de la base de datos de la plataforma
    db_url=DATABASE_URL,
    # oculta el badge "Built with Reflex" (esquina inferior derecha)
    api_url=API_URL,
    show_built_with_reflex=False,
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
        rx.plugins.RadixThemesPlugin(),
    ]
)