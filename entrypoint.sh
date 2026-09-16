#!/usr/bin/env bash
set -e

echo "==> Alembic: migraciones"
alembic upgrade head

echo "==> Seed"
python -m scripts.seed

echo "==> Trigger auditoria"
python - <<'PY'
import os
import psycopg2

dns = os.environ["DATABASE_URL"].replace("+psycopg2", "")
con = psycopg2.connect(dns)
con.autocommit = True
with con.cursor() as cur:
    cur.execute(open("scripts/auditoria_up.sql").read())
con.close()
print("auditoria_fn y triggers aplicados")
PY

echo "==> Reflex (produccion)"
# --single-port: en prod el backend sirve API + frontend compilado juntos.
# --backend-port 8000: sin esto Reflex usa :3000 por defecto y Traefik (que
# apunta a :8000) devuelve Bad Gateway.
exec reflex run --env prod --single-port --backend-port 8000