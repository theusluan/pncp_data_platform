"""add unique constraint compra numero ano

Revision ID: 0625d176f5c6
Revises: 20260228_1300
Create Date: 2026-03-12 00:06:47.542892
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0625d176f5c6"
down_revision: Union[str, Sequence[str], None] = "20260228_1300"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Aplica a alteração no banco:
    cria UNIQUE para evitar duplicidade de compras
    """
    op.create_unique_constraint(
        "uq_compra_numero_ano",
        "compra",
        ["numero_compra", "ano_compra"]
    )


def downgrade() -> None:
    """
    Reverte a alteração
    """
    op.drop_constraint(
        "uq_compra_numero_ano",
        "compra",
        type_="unique"
    )