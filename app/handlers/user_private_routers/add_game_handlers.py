from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.filters import or_f
from aiogram_calendar import  SimpleCalendar

from app.handlers.fsm.states import ActionSelection, AddUser, AddGame
from app.database.orm_query import orm_get_all_nicknames, orm_save_game
from app.kbds.inline import (get_callback_btns, get_start_menu_kbds,
                             get_paginator_keyboard, get_add_sheriff_kbds,
                             get_add_don_kbds, get_add_mafia_kbds,
                             get_add_point_kbds, get_best_step_kbds,
                             get_first_dead_kbds)


add_game_router = Router()


@add_game_router.callback_query(ActionSelection.add_game_or_show_game, F.data.startswith('add_game'))
async def start_handler_for_add_nickname(callback: CallbackQuery, state:FSMContext, session:AsyncSession):
    all_nicknames = await orm_get_all_nicknames(session)
    await state.update_data(add_game_or_swow_game=all_nicknames)
    await callback.message.edit_text("Выберите игроков. Игроков добавленно: 0", reply_markup=get_paginator_keyboard(data=all_nicknames))
    await state.set_state(AddGame.add_players_in_game)


@add_game_router.callback_query(F.data.startswith("page_"), AddGame.add_players_in_game)
async def handle_pagination(callback: CallbackQuery, state: FSMContext):
    page = int(callback.data.split('_')[1])
    data = await state.get_data()
    nicknames = data.get("add_game_or_swow_game", [])
    await callback.message.edit_reply_markup(reply_markup=get_paginator_keyboard(page=page, data=nicknames))


@add_game_router.callback_query(AddGame.add_players_in_game, F.data.startswith('select_'))
async def add_nickname(callback: CallbackQuery, state: FSMContext, session:AsyncSession): 
    data = await state.get_data()    
    all_nicknames = data['add_game_or_swow_game']
    nick = callback.data.split('_')[1]
    data = await state.get_data()
    nicknames = data.get("add_players_in_game", [])
    if nick not in nicknames:
        nicknames.append(nick)
        all_nicknames.remove(nick)        
        await state.update_data(add_players_in_game=nicknames)
        if len(nicknames) < 10:
            page = 0  
            await callback.message.edit_text(f'Вы добавили {nick}. Всего игроков добавлено: {len(nicknames)}',reply_markup=get_paginator_keyboard(page=page, data=all_nicknames))
        else:
            formatted_nicknames = ",  ".join([f"{i+1}) {nickname}" for i, nickname in enumerate(nicknames)])
            await callback.message.edit_text(f"Вы выбрали: {formatted_nicknames}", reply_markup=get_callback_btns(btns={
                'Ок': 'add_role',
                'изменить': 'add_game',
            }))       
            await state.set_state(AddGame.add_role) 
    else:
        page = 0  
        try:
            await callback.message.edit_text(f'Игрок {nick} уже был добавлен, выберите другого. \n Игроков добавлено: {len(nicknames)}',reply_markup=get_paginator_keyboard(page=page, data=all_nicknames))
        except:
            await callback.message.edit_text(f'ошибка при добавлении. Если ошибка повторится, обобратитесь к Математику', reply_markup=get_start_menu_kbds())
            await state.clear()
            await state.set_state(ActionSelection.choice_action)


@add_game_router.callback_query(AddGame.add_role,  F.data.startswith('add_game')) 
async def correct_users_in_game(callback: CallbackQuery, state: FSMContext, session:AsyncSession):
    data = await state.get_data()
    all_nicknames = await orm_get_all_nicknames(session)
    await state.update_data(add_game_or_swow_game=all_nicknames) 
    await state.update_data(add_players_in_game=[]) 
    await callback.message.edit_text("Выберите один из вариантов:", reply_markup=get_paginator_keyboard(data=all_nicknames))
    await state.set_state(AddGame.add_players_in_game)


@add_game_router.callback_query(AddGame.add_role, F.data.startswith('add_role'))
async def add_sherif(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    nicknames = data["add_players_in_game"]
    roles =['Мирный','Мирный','Мирный','Мирный','Мирный','Мирный','Мирный','Мирный','Мирный','Мирный']
    await state.update_data(add_role=roles)
    await callback.message.edit_text("Выберите шерифа игры:", reply_markup=get_add_sheriff_kbds(data=nicknames)) 


@add_game_router.callback_query(AddGame.add_role, F.data.startswith('sheriff_'))
async def add_don(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    nicknames = data["add_players_in_game"]
    nick = callback.data.split('_')[1]
    roles = data.get('add_role')
    roles[nicknames.index(nick)] = 'Шериф'
    await state.update_data(add_role=roles)
    await callback.message.edit_text("Выберите Дона игры:", reply_markup=get_add_don_kbds(data=nicknames)) 


@add_game_router.callback_query(AddGame.add_role, F.data.startswith('don_'))
async def add_fol(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    nicknames = data["add_players_in_game"]
    nick = callback.data.split('_')[1]
    roles = data.get('add_role')
    roles[nicknames.index(nick)] = 'Дон'
    await state.update_data(add_role=roles)
    await callback.message.edit_text("Выберите первую мафию:", reply_markup=get_add_mafia_kbds(data=nicknames))


@add_game_router.callback_query(AddGame.add_role, F.data.startswith('mafia_'))
async def add_fol(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    nicknames = data["add_players_in_game"]
    nick = callback.data.split('_')[1]
    roles = data.get('add_role')
    roles[nicknames.index(nick)] = 'Мафия'
    await state.update_data(add_role=roles)
    if roles.count('Мафия') == 1:                
        await callback.message.edit_text("Выберите вторую мафию:", reply_markup=get_add_mafia_kbds(data=nicknames))
    else:
        combined = [f'{nick} - {role}' for nick, role in zip(nicknames, roles)]
        await callback.message.edit_text(' ;'.join(combined), reply_markup=get_callback_btns(btns={
            'Ок': 'add_fol',
            'Изменить':'add_role'
        }))
        await state.set_state(AddGame.add_fol)


@add_game_router.callback_query(AddGame.add_fol, F.data.startswith('add_role'))
async def correct_roles_in_game(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    nicknames = data["add_players_in_game"]
    roles =['Мирный','Мирный','Мирный','Мирный','Мирный','Мирный','Мирный','Мирный','Мирный','Мирный']
    await state.update_data(add_role=roles)
    await callback.message.edit_text("Выберите шерифа игры:", reply_markup=get_add_sheriff_kbds(data=nicknames)) 
    await state.set_state(AddGame.add_role)


@add_game_router.callback_query(AddGame.add_fol, F.data.startswith('add_fol'))
async def start_handler_for_add_fol(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    nicknames = data["add_players_in_game"]
    fols = data.get('add_fol', [])
    await callback.message.answer(f'Выберите количество фолов для {nicknames[len(fols)]}', reply_markup=get_callback_btns(btns={
        '0': '0',
        '1': '1',
        '2': '2',
        '3': '3',
        '4': '4',
    }))


@add_game_router.callback_query(AddGame.add_fol, or_f(F.data.startswith('0'), F.data.startswith('1'), F.data.startswith('2'), F.data.startswith('3'), F.data.startswith('4')))
async def add_fol(callback: CallbackQuery, state: FSMContext):
    fol = callback.data
    data = await state.get_data()
    nicknames = data["add_players_in_game"]
    fols = data.get('add_fol', [])
    fols.append(fol)
    await state.update_data(add_fol=fols)
    if len(fols) < 10:
        await callback.message.edit_text(f'Выберите количество фолов для {nicknames[len(fols)]}', reply_markup=get_callback_btns(btns={
            '0': '0',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
        }))
    else:
        combined = [f'{nick} - {fol}' for nick, fol in zip(nicknames, fols)]
        await callback.message.edit_text(';    '.join(combined), reply_markup=get_callback_btns(btns={
            'Ок': 'add_point',
            'Изменить':'add_fol'
        }))
        await state.set_state(AddGame.add_point)


@add_game_router.callback_query(AddGame.add_point, F.data.startswith('add_fol'))
async def correct_fol_in_game(callback: CallbackQuery, state: FSMContext):
    await state.update_data(add_fol=[])
    data = await state.get_data()
    nicknames = data["add_players_in_game"]
    fols = data.get('add_fol', [])    
    await callback.message.edit_text(f'Выберите количество фолов для {nicknames[len(fols)]}', reply_markup=get_callback_btns(btns={
            '0': '0',
            '1': '1',
            '2': '2',
            '3': '3',
            '4': '4',
        }))
    await state.set_state(AddGame.add_fol)
   
 
@add_game_router.callback_query(AddGame.add_point, F.data.startswith('add_point'))
async def start_handler_for_add_point(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    nicknames = data["add_players_in_game"]
    points = data.get('add_point', [])
    await callback.message.answer(f'Выберите количество доп балов для {nicknames[len(points)]}', reply_markup=get_add_point_kbds())


@add_game_router.callback_query(AddGame.add_point, or_f(F.data.startswith('-0.'), F.data.startswith('0'), F.data.startswith('1')))
async def add_point(callback: CallbackQuery, state: FSMContext):
    point = callback.data
    data = await state.get_data()
    nicknames = data["add_players_in_game"]
    points = data.get('add_point', [])
    points.append(point)
    await state.update_data(add_point=points)
    if len(points) < 10:
        await callback.message.edit_text(f'Выберите количество доп балов для {nicknames[len(points)]}', reply_markup=get_add_point_kbds())
    else:
        combined = [f'{nick} - {point}' for nick, point in zip(nicknames, points)]
        await callback.message.edit_text(';    '.join(combined), reply_markup=get_callback_btns(btns={
            'Ок': 'add_first_dead',
            'Изменить':'add_point'
        }))
        await state.set_state(AddGame.add_first_dead)


@add_game_router.callback_query(AddGame.add_first_dead, F.data.startswith('add_point'))
async def correct_point_in_game(callback: CallbackQuery, state: FSMContext):
    await state.update_data(add_point=[])
    data = await state.get_data()
    nicknames = data["add_players_in_game"]
    points = data.get('add_point', [])    
    await callback.message.edit_text(f'Выберите количество доп балов для {nicknames[len(points)]}', reply_markup=get_add_point_kbds())
    await state.set_state(AddGame.add_point)


@add_game_router.callback_query(AddGame.add_first_dead, F.data.startswith('add_first_dead'))
async def add_first_dead(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    nicknames = data["add_players_in_game"]
    await callback.message.answer('Выберите ПУ игрока', reply_markup=get_first_dead_kbds(data=nicknames))  
    await state.set_state(AddGame.add_best_step)


@add_game_router.callback_query(AddGame.add_best_step, F.data.startswith('fd'))
async def start_handler_best_step(callback: CallbackQuery, state: FSMContext):
    await state.update_data(add_first_dead=callback.data.split('_')[1])
    data = await state.get_data()
    nicknames = data['add_players_in_game']
    best_steb =data.get('add_best_step', [])
    await callback.message.edit_text('Выберите лучший ход ПУ игрока', reply_markup=get_best_step_kbds(data=nicknames))


@add_game_router.callback_query(AddGame.add_best_step, F.data.startswith('bs'))
async def add_best_step(callback: CallbackQuery, state: FSMContext):
    bs = callback.data.split('_')[1]
    data = await state.get_data()
    nicknames = data["add_players_in_game"]
    best_step = data.get('add_best_step', [])
    best_step.append(bs)
    await state.update_data(add_best_step=best_step)
    if len(best_step) < 3:
        await callback.message.edit_text(f'Выберите лучший ход ПУ игрока. Добавлены: {best_step}', reply_markup=get_best_step_kbds(data=nicknames))
    else:
        await callback.message.edit_text(f'ЛХ игрока {data["add_first_dead"]}: {best_step[0]} {best_step[1]} {best_step[2]}', reply_markup=get_callback_btns(btns={
            'Ок': 'winner',
            'Изменить':'add_best_step'
        }))
        await state.set_state(AddGame.winner)


@add_game_router.callback_query(AddGame.winner, F.data.startswith('add_best_step'))
async def correct_best_step(callback: CallbackQuery, state: FSMContext):
    await state.update_data(add_best_step=[])
    data = await state.get_data()
    nicknames = data["add_players_in_game"]
    points = data.get('add_point', [])    
    await callback.message.edit_text(f'Выберите лучший ход ПУ игрока', reply_markup=get_best_step_kbds(data=nicknames))
    await state.set_state(AddGame.add_best_step)


@add_game_router.callback_query(AddGame.winner, F.data.startswith('winner'))
async def add_winner(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Выберите победителя', reply_markup=get_callback_btns(btns={
        'Мирные':'Мирный',
        'Мафия':'Мафия',
        'Ничья':'Ничья',
        }))
    await state.set_state(AddGame.date_game)


@add_game_router.callback_query(AddGame.date_game, or_f(F.data.startswith('Мирный'), F.data.startswith('Мафия'), F.data.startswith('Ничья')))
async def add_date_game(callback: CallbackQuery, state: FSMContext):
    await state.update_data(add_winner=callback.data)
    await callback.message.answer("Выберите дату:", reply_markup=await SimpleCalendar().start_calendar())


@add_game_router.callback_query(AddGame.date_game, F.data.startswith('simple_calendar'))
async def add_revie(callback: CallbackQuery, state: FSMContext):
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
        day = callback.data.split('DAY:')[1].replace(':', '-')
        await state.update_data(date_game=day)
        data = await state.get_data()
        print(data)
        gamers = data["add_players_in_game"]
        roles = data["add_role"]
        points = data.get('add_point', [])
        best_step = data.get('add_best_step', [])
        winner = data.get('add_winner', [])
        date = data.get('date_game')
        data_game = [f'{gamer}:  {role} - {point}' for gamer, role, point in zip(gamers, roles, points)]
        await callback.message.edit_text(f'Игроки: {data_game}\nЛХ: {best_step}\nПобедитель: {winner}\nДата: {date}', reply_markup=get_callback_btns(btns={
            'Сохранить':'save',
            'Отменить':'cancel'
        }))
        await state.set_state(AddGame.review)
    else:
        await callback.message.edit_text("Выберите дату или с помощью '<' и '>' выберите месяц:", reply_markup=await SimpleCalendar().start_calendar())
  
       
@add_game_router.callback_query(AddGame.review, F.data.startswith('save'))
async def save_game(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    await orm_save_game(session, data=data )
    await state.clear()

    await callback.message.edit_text('Игра сохранена')
    await callback.message.answer('Статистика по мафии', reply_markup=get_start_menu_kbds())
    await state.set_state(ActionSelection.choice_action)