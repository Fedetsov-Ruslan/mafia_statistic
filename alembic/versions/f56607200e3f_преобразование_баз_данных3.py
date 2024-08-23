"""Преобразование баз данных3

Revision ID: f56607200e3f
Revises: 43166f5902ba
Create Date: 2024-08-23 12:30:21.543964

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f56607200e3f'
down_revision: Union[str, None] = '43166f5902ba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('best_step', 'seat_number',
               existing_type=sa.VARCHAR(length=15),
               type_=sa.String(length=30),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('best_step', 'seat_number',
               existing_type=sa.String(length=30),
               type_=sa.VARCHAR(length=15),
               existing_nullable=False)
    # ### end Alembic commands ###
