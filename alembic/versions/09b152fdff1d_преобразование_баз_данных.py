"""Преобразование баз данных

Revision ID: 09b152fdff1d
Revises: e03c798ca046
Create Date: 2024-08-23 11:14:33.230213

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '09b152fdff1d'
down_revision: Union[str, None] = 'e03c798ca046'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('new_games',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('type_games', sa.String(length=15), nullable=False),
    sa.Column('date_game', sa.Date(), nullable=False),
    sa.Column('first_dead', sa.String(length=150), nullable=True),
    sa.Column('winner', sa.String(length=15), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('old_games',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('types_game', sa.String(length=15), nullable=False),
    sa.Column('date_game', sa.Date(), nullable=False),
    sa.Column('gamers', sa.ARRAY(sa.String()), nullable=False),
    sa.Column('roles', sa.ARRAY(sa.String()), nullable=False),
    sa.Column('fols', sa.ARRAY(sa.Integer()), nullable=False),
    sa.Column('points', sa.ARRAY(sa.Float()), nullable=False),
    sa.Column('dop_points', sa.ARRAY(sa.Float()), nullable=True),
    sa.Column('best_step', sa.ARRAY(sa.String()), nullable=True),
    sa.Column('first_dead', sa.String(length=150), nullable=True),
    sa.Column('winner', sa.String(length=15), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('best_step',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('game_id', sa.Integer(), nullable=False),
    sa.Column('seat_number', sa.Integer(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['game_id'], ['new_games.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('game_results',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('game_id', sa.Integer(), nullable=False),
    sa.Column('playr_id', sa.Integer(), nullable=False),
    sa.Column('seat_number', sa.Integer(), nullable=False),
    sa.Column('role', sa.String(length=15), nullable=False),
    sa.Column('fols', sa.Integer(), nullable=False),
    sa.Column('points', sa.Float(), nullable=False),
    sa.Column('dop_points', sa.Float(), nullable=True),
    sa.Column('created', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['game_id'], ['new_games.id'], ),
    sa.ForeignKeyConstraint(['playr_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('games')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('games',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('types_game', sa.VARCHAR(length=15), autoincrement=False, nullable=False),
    sa.Column('date_game', sa.DATE(), autoincrement=False, nullable=False),
    sa.Column('gamers', postgresql.ARRAY(sa.VARCHAR()), autoincrement=False, nullable=False),
    sa.Column('roles', postgresql.ARRAY(sa.VARCHAR()), autoincrement=False, nullable=False),
    sa.Column('fols', postgresql.ARRAY(sa.INTEGER()), autoincrement=False, nullable=False),
    sa.Column('points', postgresql.ARRAY(sa.DOUBLE_PRECISION(precision=53)), autoincrement=False, nullable=False),
    sa.Column('dop_points', postgresql.ARRAY(sa.DOUBLE_PRECISION(precision=53)), autoincrement=False, nullable=True),
    sa.Column('best_step', postgresql.ARRAY(sa.VARCHAR()), autoincrement=False, nullable=True),
    sa.Column('first_dead', sa.VARCHAR(length=150), autoincrement=False, nullable=True),
    sa.Column('winner', sa.VARCHAR(length=15), autoincrement=False, nullable=True),
    sa.Column('created', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('updated', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='games_pkey')
    )
    op.drop_table('game_results')
    op.drop_table('best_step')
    op.drop_table('old_games')
    op.drop_table('new_games')
    # ### end Alembic commands ###
