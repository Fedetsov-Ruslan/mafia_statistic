import datetime

from sqlalchemy import exists, select, update, delete, values
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import Users, Games, GameResults, BestStep

 #TODO  изменить все запросы в связи с изменением моделей таблиц

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
    points = [1 if (role == data['add_winner']) 
              or (role == 'Дон' and data['add_winner']=='Мафия') 
              or (role == 'Шериф' and data['add_winner']=='Мирный')
              else 0 for role in data['add_role']]
    obj = Games(
        types_game=data['type_game'],
        date_game=date_game,
        gamers=data['add_players_in_game'],
        roles=data['add_role'],
        fols=data['add_fol'],
        points=points,
        dop_points=data['add_point'],
        best_step=data['add_best_step'],
        first_dead=data['add_players_in_game'].index(data['add_first_dead']),
        winner=data['add_winner'],
    )
    session.add(obj)
    await session.commit()

async def orm_get_games(session: AsyncSession, data: dict):

    first_date = datetime.datetime.strptime(data['add_game_or_show_game'][0], '%Y-%m-%d').date()
    second_date = datetime.datetime.strptime(data['add_game_or_show_game'][1], '%Y-%m-%d').date()
    query = select(Games).where(Games.date_game>=first_date, Games.date_game<=second_date, Games.types_game==data['type_game'])
    result = await session.execute(query)
    return result.scalars().all()
