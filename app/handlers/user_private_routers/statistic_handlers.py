import datetime
from aiogram import Router, F
from aiogram.types import  CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram_calendar import  SimpleCalendar

from app.handlers.fsm.states import ActionSelection
from app.database.orm_query import orm_get_games
from app.kbds.inline import get_start_menu_kbds
from app.transformation_data.transformation_statistic import transformation_statistic

statistic_router = Router()

@statistic_router.callback_query(ActionSelection.choice_action, F.data.startswith('statistics'))
async def statistics(callback: CallbackQuery, state: FSMContext):
    await state.update_data(choice_action=callback.data)
    await callback.message.answer("Выберите дату:", reply_markup=await SimpleCalendar().start_calendar())
    await state.set_state(ActionSelection.statistics_date)


@statistic_router.callback_query(ActionSelection.statistics_date, F.data.startswith('simple_calendar'))
async def first_date_statistic(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
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
        day = data.get('statistics_date', [])
        day.append(callback.data.split('DAY:')[1].replace(':', '-'))
        await state.update_data(statistics_date=day)
        if len(day) == 2:
            first_date = datetime.datetime.strptime(data['statistics_date'][0], '%Y-%m-%d').date()
            second_date = datetime.datetime.strptime(data['statistics_date'][1], '%Y-%m-%d').date()
            data['type_game'] = 'ranked'
            games = await orm_get_games(session, first_date=first_date, second_date=second_date, data=data)
            players_in_game = []
            for game in games:
                players_in_game.append(game._asdict())               
            statistic = await transformation_statistic(players_in_game)
            await callback.message.answer_document(document=statistic, caption=' Статистика по мафии')               
            await callback.message.answer('Статистика по мафии', reply_markup=get_start_menu_kbds())
            await state.clear()
            await state.set_state(ActionSelection.choice_action)
        else:
            await callback.message.edit_text("Выберите вторую дату:", reply_markup=await SimpleCalendar().start_calendar())
    else:
        await callback.message.edit_text("Выберите дату или с помощью '<' и '>' выберите месяц:", reply_markup=await SimpleCalendar().start_calendar())