"""rename orders price to total_price

Revision ID: 94a2a1be888f
Revises: 0e47f58f4c3a
Create Date: 2026-10-15 09:58:46.729266

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision: str = '94a2a1be888f'
down_revision: Union[str, Sequence[str], None] = '0e47f58f4c3a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.alter_column('price', new_column_name='total_price')

def downgrade() -> None:
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.alter_column('total_price', new_column_name='price')

