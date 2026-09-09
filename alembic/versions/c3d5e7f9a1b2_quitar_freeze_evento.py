"""quitar evento.freeze (el freeze del scoreboard pasa a Redis)

Revision ID: c3d5e7f9a1b2
Revises: b2f4a9c7d1e3
Create Date: 2026-09-09

El estado de freeze del scoreboard deja de vivir en la BD y pasa a Redis
(claves `itdb:frz:flag:{id}` / `itdb:frz:fecha:{id}`). Ver `reddis.md`.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "c3d5e7f9a1b2"
down_revision: Union[str, Sequence[str], None] = "b2f4a9c7d1e3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_column("evento", "freeze")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "evento",
        sa.Column("freeze", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column("evento", "freeze", server_default=None)
