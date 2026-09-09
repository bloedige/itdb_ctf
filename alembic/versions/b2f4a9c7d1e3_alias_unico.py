"""alias unico case-insensitive

Revision ID: b2f4a9c7d1e3
Revises: 8ebefff773c4
Create Date: 2026-09-09

Antes de aplicar, verificar que no haya alias duplicados (ignorando mayúsculas):

    SELECT lower(alias) AS alias, count(*)
    FROM usuario
    WHERE alias IS NOT NULL
    GROUP BY lower(alias)
    HAVING count(*) > 1;

Si devuelve filas, corregir esos alias a mano antes de `alembic upgrade head`.
"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b2f4a9c7d1e3"
down_revision: Union[str, Sequence[str], None] = "8ebefff773c4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        "CREATE UNIQUE INDEX uq_usuario_alias_lower "
        "ON usuario (lower(alias)) WHERE alias IS NOT NULL"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP INDEX IF EXISTS uq_usuario_alias_lower")
