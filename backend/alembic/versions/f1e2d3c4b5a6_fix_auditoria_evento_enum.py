"""fix auditoria evento enum - change to VARCHAR

Revision ID: f1e2d3c4b5a6
Revises: 144c3c3074f5
Create Date: 2026-05-25 00:00:00.000000

The DB ENUM for auditoria.evento only had the 7 original values from the
initial migration. The Python enum grew to 30+ values, causing any audit
insert with a newer value (CLIENTE_ATUALIZADO, OS_CRIADA, etc.) to fail
with a MySQL ENUM constraint error. Switching to VARCHAR(100) avoids
having to update this migration every time a new event type is added.
"""

from alembic import op

revision = 'f1e2d3c4b5a6'
down_revision = '144c3c3074f5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE auditoria MODIFY COLUMN evento VARCHAR(100) NOT NULL"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE auditoria MODIFY COLUMN evento ENUM("
        "'LOGIN_SUCESSO','LOGIN_FALHA','ACESSO_NEGADO','OS_ESTADO_ALTERADO',"
        "'STOCK_ENTRADA','STOCK_TRANSFERENCIA','FATURA_EMITIDA'"
        ") NOT NULL"
    )
