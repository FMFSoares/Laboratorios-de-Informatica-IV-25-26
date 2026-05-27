"""add mecanico_id to registos_tempo and create os_observacoes

Revision ID: c3d4e5f6a7b8
Revises: a1c3e5f7b9d2
Create Date: 2026-05-16 14:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = 'c3d4e5f6a7b8'
down_revision = 'a1c3e5f7b9d2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('registos_tempo',
        sa.Column('mecanico_id', sa.Integer(), sa.ForeignKey('utilizadores.id'), nullable=True)
    )

    op.create_table('os_observacoes',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('ordem_servico_id', sa.Integer(), sa.ForeignKey('ordens_servico.id'), nullable=False),
        sa.Column('autor_id', sa.Integer(), sa.ForeignKey('utilizadores.id'), nullable=False),
        sa.Column('texto', sa.String(1000), nullable=False),
        sa.Column('criado_em', sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('os_observacoes')
    op.drop_column('registos_tempo', 'mecanico_id')
