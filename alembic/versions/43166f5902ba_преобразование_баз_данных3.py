"""Преобразование баз данных3

Revision ID: 43166f5902ba
Revises: 89f76b3a1030
Create Date: 2024-08-23 12:01:32.899728

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '43166f5902ba'
down_revision: Union[str, None] = '89f76b3a1030'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('best_step', 'seat_number',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=15),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('best_step', 'seat_number',
               existing_type=sa.String(length=15),
               type_=sa.INTEGER(),
               existing_nullable=False,
               postgresql_using='seat_number::integer')
    # ### end Alembic commands ###
