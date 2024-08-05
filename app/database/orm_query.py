import datetime

from sqlalchemy import exists, select, update, delete, values
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Users, Games, Statistics

async def orm_add_user(session: AsyncSession, data: dict):
    obj = Users(nickname=data['nickname'], gender=data['gender'], club=data['club'])
    
    session.add(obj)
    await session.commit()

async def orm_get_all_users(session: AsyncSession):
    result = await session.execute(select(Users))

    return result.scalars().all()

async def orm_get_all_nicknames(session: AsyncSession):
    result = await session.execute(select(Users.nickname))

    return result.scalars().all()


async def orm_save_game(session: AsyncSession, data: dict):
    date_game = datetime.datetime.strptime(data['date_game'], '%Y-%m-%d').date()
    data['add_fol'] = list(map(lambda x: int(x), data['add_fol']))
    data['add_point'] = list(map(lambda x: float(x), data['add_point']))
    obj = Games(
        types_game=data['type_game'],
        date_game=date_game,
        gamers=data['add_players_in_game'],
        roles=data['add_role'],
        fols=data['add_fol'],
        points=data['add_point'],
        best_step=data['add_best_step'],
        first_dead=data['add_first_dead'],
        winner=data['add_winner'],
    )

    session.add(obj)
    await session.commit()