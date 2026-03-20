"""add_amparo_legal_table_and_column

Revision ID: 20260228_1300
Revises: f4214871e326
Create Date: 2026-02-28 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260228_1300'
down_revision = 'f4214871e326'  # revision anterior, ajuste se necessário
branch_labels = None
depends_on = None


def upgrade():
    # ---- Criar tabela amparo_legal ----
    op.create_table(
        'amparo_legal',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('codigo', sa.Integer, nullable=False),
        sa.Column('nome', sa.String(255), nullable=False),
        sa.Column('descricao', sa.Text),
        sa.Column('data_inclusao', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
    )

    # ---- Adicionar coluna amparo_legal_id em compra ----
    op.add_column('compra', sa.Column('amparo_legal_id', postgresql.UUID(as_uuid=True), nullable=True))

    # ---- Criar ForeignKey ----
    op.create_foreign_key(
        'fk_compra_amparo_legal',
        source_table='compra',
        referent_table='amparo_legal',
        local_cols=['amparo_legal_id'],
        remote_cols=['id'],
        ondelete='SET NULL'
    )


def downgrade():
    # ---- Reverter alterações ----
    op.drop_constraint('fk_compra_amparo_legal', 'compra', type_='foreignkey')
    op.drop_column('compra', 'amparo_legal_id')
    op.drop_table('amparo_legal')