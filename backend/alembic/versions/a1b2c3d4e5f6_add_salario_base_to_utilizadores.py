"""add salario_base to utilizadores

Revision ID: a1b2c3d4e5f6
Revises: f1e2d3c4b5a6
Create Date: 2026-05-27 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = 'a1b2c3d4e5f6'
down_revision = 'f1e2d3c4b5a6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('utilizadores', sa.Column('salario_base', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('utilizadores', 'salario_base')
