#!/usr/bin/env bash
set -e

alembic upgrade head

python -m scripts.seed

python - <<'PY'
import os, psycopg2
dns = os.environ["DATABASE_URL"].replace("+psycopg2", "")
con = psycopg2.connect(dns)
con.autocommit = True
con.cursor().execute(open("scripts/auditoria_up.sql").read())
con.close()
print("auditoria_fn y triggers aplicados")
PY

exec reflex run --env prod --backed-host 0.0.0.0