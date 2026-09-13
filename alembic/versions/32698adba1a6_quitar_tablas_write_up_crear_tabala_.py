"""quitar tablas write up crear tabala auditoria

Revision ID: 32698adba1a6
Revises: c3d5e7f9a1b2
Create Date: 2026-09-12 20:34:49.085126

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '32698adba1a6'
down_revision: Union[str, Sequence[str], None] = 'c3d5e7f9a1b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# catalogos que estrenan la columna `activo`
_CATALOGOS_ACTIVO = ("dificultad", "modo_puntaje", "modalidad", "estado_inscripcion")


def upgrade() -> None:
    """Upgrade schema."""
    # --- tabla de auditoria (los triggers van aparte: scripts/auditoria_up.sql) ---
    op.create_table(
        'auditoria',
        sa.Column('id_auditoria', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('tabla', sqlmodel.sql.sqltypes.AutoString(length=30), nullable=False),
        sa.Column('id_registro', sa.Integer(), nullable=True),
        sa.Column('operacion', sqlmodel.sql.sqltypes.AutoString(length=6), nullable=False),
        sa.Column('id_usuario', sa.Integer(), nullable=True),
        sa.Column('datos_antes', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('datos_despues', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('campos', postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column('fec_registro', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id_auditoria'),
    )
    op.create_index('ix_auditoria_fecha', 'auditoria', ['fec_registro'], unique=False)
    op.create_index('ix_auditoria_tabla_registro', 'auditoria', ['tabla', 'id_registro'], unique=False)
    op.create_index('ix_auditoria_usuario', 'auditoria', ['id_usuario'], unique=False)

    # --- writeup: feature descartada (hija primero por la FK) ---
    op.drop_table('writeup')
    op.drop_table('estado_writeup')

    # --- `activo` en los catalogos que faltaban ---
    # server_default temporal para poder poner NOT NULL sobre filas existentes;
    # se retira despues porque el default real vive en el modelo (Field(default=True)).
    for tabla in _CATALOGOS_ACTIVO:
        op.add_column(
            tabla,
            sa.Column('activo', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        )
        op.alter_column(tabla, 'activo', server_default=None)

    # --- columnas sin uso ---
    op.drop_column('categoria', 'descripcion')
    op.drop_column('resuelve', 'dir_ip')
    op.drop_column('usuario', 'avatar')


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column('usuario', sa.Column('avatar', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
    op.add_column('resuelve', sa.Column('dir_ip', postgresql.INET(), autoincrement=False, nullable=True))
    op.add_column('categoria', sa.Column('descripcion', sa.TEXT(), autoincrement=False, nullable=True))

    for tabla in _CATALOGOS_ACTIVO:
        op.drop_column(tabla, 'activo')

    op.create_table(
        'estado_writeup',
        sa.Column('id_estado_writeup', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('etiqueta', sa.VARCHAR(length=15), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint('id_estado_writeup', name=op.f('estado_writeup_pkey')),
        sa.UniqueConstraint('etiqueta', name=op.f('estado_writeup_etiqueta_key')),
    )
    op.create_table(
        'writeup',
        sa.Column('id_writeup', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('id_usuario', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('id_reto', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('id_estado_writeup', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('writeup_ruta', sa.VARCHAR(length=25), autoincrement=False, nullable=False),
        sa.Column('fec_creacion', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
        sa.Column('activo', sa.BOOLEAN(), autoincrement=False, nullable=False),
        sa.ForeignKeyConstraint(['id_estado_writeup'], ['estado_writeup.id_estado_writeup'], name=op.f('writeup_id_estado_writeup_fkey')),
        sa.ForeignKeyConstraint(['id_reto'], ['reto.id_reto'], name=op.f('writeup_id_reto_fkey')),
        sa.ForeignKeyConstraint(['id_usuario'], ['usuario.id_usuario'], name=op.f('writeup_id_usuario_fkey')),
        sa.PrimaryKeyConstraint('id_writeup', name=op.f('writeup_pkey')),
    )

    op.drop_index('ix_auditoria_usuario', table_name='auditoria')
    op.drop_index('ix_auditoria_tabla_registro', table_name='auditoria')
    op.drop_index('ix_auditoria_fecha', table_name='auditoria')
    op.drop_table('auditoria')
