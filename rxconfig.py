import os
from dotenv import load_dotenv

import reflex as rx

load_dotenv()

config = rx.Config(
    app_name="itdb_ctf",
    # configuramos la url de la base de datos de la plataforma
    db_url=os.environ["DATABASE_URL"],
    # oculta el badge "Built with Reflex" (esquina inferior derecha)
    show_built_with_reflex=False,
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
        rx.plugins.RadixThemesPlugin(),
    ]
)