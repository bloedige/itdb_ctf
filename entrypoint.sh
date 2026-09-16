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
exec reflex run --env prod