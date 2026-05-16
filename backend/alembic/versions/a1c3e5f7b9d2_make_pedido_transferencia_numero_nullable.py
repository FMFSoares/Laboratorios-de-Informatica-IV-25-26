"""make pedido_transferencia numero nullable

Revision ID: a1c3e5f7b9d2
Revises: 4a8e8944f309
Create Date: 2026-05-16 12:55:00.000000

numero is generated from the auto-increment id (TRF-{year}-{id:04d}), which is
only available after the initial INSERT. Making the column nullable allows the
ORM to flush the row (getting the id), then set numero in the same transaction
before the final commit.
"""

from alembic import op
import sqlalchemy as sa

revision = 'a1c3e5f7b9d2'
down_revision = '4a8e8944f309'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        'pedidos_transferencia',
        'numero',
        existing_type=sa.String(50),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        'pedidos_transferencia',
        'numero',
        existing_type=sa.String(50),
        nullable=False,
    )
