"""flag modification

Revision ID: 6a4dcf85d756
Revises: 32698adba1a6
Create Date: 2026-09-16 17:22:34.258182

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '6a4dcf85d756'
down_revision: Union[str, Sequence[str], None] = '32698adba1a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """reto.flag: CHAR(60) -> CHAR(64).

    La flag se guarda como SHA-256 en hexadecimal = 64 caracteres exactos. El
    esquema inicial dejo la columna en CHAR(60) (largo heredado de bcrypt), asi
    que en una base creada por migraciones (produccion) crear un reto falla con
    "value too long for type character(60)". models.py ya declara CHAR(64); el
    autogenerate salio vacio porque la base de desarrollo ya estaba alterada a
    mano.
    """
    op.alter_column(
        "reto",
        "flag",
        existing_type=sa.CHAR(length=60),
        type_=sa.CHAR(length=64),
        existing_nullable=True,
    )


def downgrade() -> None:
    """Vuelve a CHAR(60) (falla si ya hay hashes de 64 caracteres)."""
    op.alter_column(
        "reto",
        "flag",
        existing_type=sa.CHAR(length=64),
        type_=sa.CHAR(length=60),
        existing_nullable=True,
    )
