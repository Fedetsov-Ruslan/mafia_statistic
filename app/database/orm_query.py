import datetime

from sqlalchemy import distinct, select
from sqlalchemy.orm import Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import Users, Games, GameResults, BestStep

async def orm_add_user(session: AsyncSession, data: dict):
    obj = Users(nickname=data['nickname'], gender=data['gender'], club=data['club'])
    session.add(obj)
    await session.commit()

async def orm_get_all_users(session: AsyncSession, club: str):
    result = await session.execute(select(Users).where(Users.club == club))
    return result.scalars().all()

async def orm_get_all_nicknames(session: AsyncSession):
    result = await session.execute(select(Users.nickname))
    return result.scalars().all()

async def orm_get_clubs(session: AsyncSession):
    result = await session.execute(select(distinct(Users.club)))
    return result.scalars().all()

async def orm_save_game(session: AsyncSession, data: dict):
    date_on_game = datetime.datetime.strptime(data['date_game'], '%Y-%m-%d').date()
    data['add_fol'] = list(map(lambda x: int(x), data['add_fol']))
    data['add_point'] = list(map(lambda x: float(x), data['add_point']))
    point_sum = [1 if (role == data['add_winner']) 
              or (role == 'Дон' and data['add_winner']=='Мафия') 
              or (role == 'Шериф' and data['add_winner']=='Мирный')
              else 0 for role in data['add_role']]
    new_game = Games(
        type_games=data['type_game'],
        date_game=date_on_game,
        first_dead=str(data['add_players_in_game'].index(data['add_first_dead'])),
        winner=data['add_winner'],
    )
    session.add(new_game)
    session.flush()
    query = select(Users.nickname, Users.id).where(Users.nickname.in_(data['add_players_in_game']))
    result = await session.execute(query)
    all_playres = {nickname: id for nickname, id in result.all()}
    for i in range(len(data['add_role'])):
        new_game_results = GameResults(
            game_id=new_game.id,
            player_id=all_playres[data['add_players_in_game'][i]],
            seat_number=i+1,
            role=data['add_role'][i],
            fols=data['add_fol'][i],
            points=point_sum[i],
            dop_points=data['add_point'][i],
        )
        session.add(new_game_results)
    if data['add_first_dead'] != '':
        for seat in data['add_best_step']:
            new_best_step = BestStep(
                game_id=new_game.id,
                seat_number=all_playres[seat],
            )
            session.add(new_best_step)
    
    await session.commit()

async def orm_get_games(session: AsyncSession, first_date : datetime.date, second_date : datetime.date, data : dict):

    query = select(Games.id,Games.type_games, Games.date_game, 
                   Games.first_dead, Games.winner, GameResults.seat_number,
                   Users.nickname, GameResults.role, GameResults.fols, 
                   GameResults.points, GameResults.dop_points).join(GameResults, GameResults.game_id==Games.id).join(Users, Users.id==GameResults.player_id).where(Games.date_game>=first_date, Games.date_game<=second_date, Games.type_games==data['type_game'])
    result = await session.execute(query)
    
    return result

async def orm_get_best_step(session: AsyncSession, first_date : datetime.date, second_date : datetime.date, data : dict):
    query = (
        select(BestStep.game_id, Users.nickname)
        .join(Games, Games.id==BestStep.game_id)
        .join(Users, Users.id==BestStep.user_id)
        .where(Games.date_game>=first_date, Games.date_game<=second_date, Games.type_games==data['type_game']))
    result = await session.execute(query)

    return result

async def statistics_collection(session: AsyncSession, data: dict):
    first_date = datetime.datetime.strptime(data['add_game_or_show_game'][0], '%Y-%m-%d').date()
    second_date = datetime.datetime.strptime(data['add_game_or_show_game'][1], '%Y-%m-%d').date()

    games = await orm_add_user(session, data)
    players = select(GameResults.player_id, Users.nickname).join(Games, Games.id==GameResults.game_id). join(Users, Users.id==GameResults.player_id).where(Games.date_game>=first_date, Games.date_game<=second_date, Games.type_games==data['type_game'])
    for game in games:
        pass

    

