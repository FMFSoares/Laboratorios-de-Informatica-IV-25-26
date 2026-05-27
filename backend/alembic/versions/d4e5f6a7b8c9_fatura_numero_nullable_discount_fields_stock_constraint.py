"""fatura numero nullable, add discount fields to faturas, add unique constraint to stock_lojas

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-05-23 10:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = 'd4e5f6a7b8c9'
down_revision = 'c3d4e5f6a7b8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Fix 1: Make faturas.numero nullable (so we can flush to get ID before setting it)
    op.alter_column('faturas', 'numero',
        existing_type=sa.String(50),
        nullable=True
    )

    # Fix 2: Add discount fields to faturas
    op.add_column('faturas', sa.Column('desconto_tipo', sa.String(20), nullable=True))
    op.add_column('faturas', sa.Column('desconto_valor', sa.Float(), nullable=False, server_default='0.0'))
    op.add_column('faturas', sa.Column('valor_desconto', sa.Float(), nullable=False, server_default='0.0'))

    # Fix 5: Add unique constraint on stock_lojas(peca_id, loja_id)
    op.create_unique_constraint('uq_stock_peca_loja', 'stock_lojas', ['peca_id', 'loja_id'])


def downgrade() -> None:
    op.drop_constraint('uq_stock_peca_loja', 'stock_lojas', type_='unique')

    op.drop_column('faturas', 'valor_desconto')
    op.drop_column('faturas', 'desconto_valor')
    op.drop_column('faturas', 'desconto_tipo')

    op.alter_column('faturas', 'numero',
        existing_type=sa.String(50),
        nullable=False
    )
