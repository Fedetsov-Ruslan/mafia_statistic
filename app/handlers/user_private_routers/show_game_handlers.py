import datetime
from aiogram import Router, F
from aiogram.types import  CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram_calendar import  SimpleCalendar

from app.handlers.fsm.states import ActionSelection
from app.database.orm_query import orm_get_games, orm_get_best_step
from app.transformation_data.transformation_db_data import transformation_db_data
from app.kbds.inline import get_start_menu_kbds

show_game_router = Router()


@show_game_router.callback_query(ActionSelection.add_game_or_show_game, F.data.startswith('show_game'))
async def show_game(callback: CallbackQuery, state: FSMContext):

    await callback.message.answer("Выберите первую дату:", reply_markup=await SimpleCalendar().start_calendar())


@show_game_router.callback_query(ActionSelection.add_game_or_show_game, F.data.startswith('simple_calendar'))
async def add_revie(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    if callback.data.split(':')[1] == 'PREV-MONTH':
        new_month = int(callback.data.split(':')[3]) - 1
        await callback.message.edit_text("Выберите дату:", reply_markup=await SimpleCalendar().start_calendar(month=new_month))
    elif callback.data.split(':')[1] == 'NEXT-MONTH':
        new_month = int(callback.data.split(':')[3]) + 1
        await callback.message.edit_text("Выберите дату:", reply_markup=await SimpleCalendar().start_calendar(month=new_month))
    elif callback.data.split(':')[1] == 'PREV-YEAR':
        new_year = int(callback.data.split(':')[2]) - 1
        await callback.message.edit_text("Выберите дату:", reply_markup=await SimpleCalendar().start_calendar(year=new_year))
    elif callback.data.split(':')[1] == 'NEXT-YEAR':
        new_year = int(callback.data.split(':')[2]) + 1
        await callback.message.edit_text("Выберите дату:", reply_markup=await SimpleCalendar().start_calendar(year=new_year))
    elif callback.data.split(':')[1] == 'DAY':
        data = await state.get_data()
        day = data.get('add_game_or_show_game', [])
        day.append(callback.data.split('DAY:')[1].replace(':', '-'))
        await state.update_data(add_game_or_show_game=day)
        if len(day) == 2:
            #запрос в базу на вывод игр по заданным датам
            first_date = datetime.datetime.strptime(data['add_game_or_show_game'][0], '%Y-%m-%d').date()
            second_date = datetime.datetime.strptime(data['add_game_or_show_game'][1], '%Y-%m-%d').date()
            games = await orm_get_games(session, first_date=first_date, second_date=second_date, data=data)
            best_step = await orm_get_best_step(session, first_date=first_date, second_date=second_date, data=data)
            bs_list=[]
            bs_in_game=[]
            for bs in best_step:
                bs_in_game.append(bs._asdict())  
                if len(bs_in_game) == 3:
                    bs_list.append(bs_in_game)
                    bs_in_game = []

            all_games = []
            players_in_game = []
            for game in games:
                players_in_game.append(game._asdict())
                if len(players_in_game) == 10:
                    all_games.append(players_in_game)
                    players_in_game = []
            
            all_games_list = await transformation_db_data(all_games, bs_list)
            for game_list in all_games_list:
                table_in_game = '\n'.join(game_list)
                await callback.message.answer(table_in_game)
               
            await callback.message.answer('Статистика по мафии', reply_markup=get_start_menu_kbds())
            await state.clear()
            await state.set_state(ActionSelection.choice_action)
        else:
            await callback.message.edit_text("Выберите вторую дату:", reply_markup=await SimpleCalendar().start_calendar())
    else:
        await callback.message.edit_text("Выберите дату или с помощью '<' и '>' выберите месяц:", reply_markup=await SimpleCalendar().start_calendar())