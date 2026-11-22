"""quitar compra.id_reto (se deriva de compra.id_pista -> pista.id_reto)

Revision ID: d4e6f8a0b2c4
Revises: 6a4dcf85d756
Create Date: 2026-11-19

`compra.id_reto` dependía transitivamente de `id_pista` (cada pista pertenece a
un único reto), lo que rompe la 3FN. El reto de una compra se obtiene con
`JOIN pista ON pista.id_pista = compra.id_pista`. No se pierde información:
el downgrade reconstruye la columna desde `pista`.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "d4e6f8a0b2c4"
down_revision: Union[str, Sequence[str], None] = "6a4dcf85d756"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Postgres elimina junto con la columna su FK compra_id_reto_fkey.
    op.drop_column("compra", "id_reto")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column("compra", sa.Column("id_reto", sa.Integer(), nullable=True))
    op.execute(
        "UPDATE compra c SET id_reto = p.id_reto FROM pista p WHERE p.id_pista = c.id_pista"
    )
    op.alter_column("compra", "id_reto", nullable=False)
    op.create_foreign_key(
        "compra_id_reto_fkey", "compra", "reto", ["id_reto"], ["id_reto"]
    )
