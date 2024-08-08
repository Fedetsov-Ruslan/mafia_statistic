from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command, StateFilter, or_f
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram_calendar import  SimpleCalendar

from app.database.orm_query import orm_add_user, orm_get_all_nicknames, orm_get_all_users, orm_get_games, orm_save_game
from app.kbds.inline import get_add_don_kbds, get_add_mafia_kbds, get_add_point_kbds, get_add_sheriff_kbds, get_best_step_kbds, get_callback_btns, get_first_dead_kbds, get_paginator_keyboard, get_start_menu_kbds
from app.transformation_data.transformation_db_data import transformation_db_data


class ActionSelection(StatesGroup):
    choice_action = State()
    users = State()
    games = State()
    statistics = State()
    viewing_user = State()
    get_all_in_club = State()
    type_game = State()
    add_game_or_show_game = State()
    

class AddGame(StatesGroup):
    add_players_in_game = State()
    add_role = State()
    add_fol = State()
    add_point = State()
    add_first_dead = State()
    add_best_step = State()
    winner = State()
    date_game = State()
    review = State()


    

class AddUser(StatesGroup):

    nickname = State()
    gender = State()
    club = State()
    confirmation = State()
    add_complite = State()


user_private_router = Router()
    
@user_private_router.message(CommandStart())
async def start(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Статистика по мафии', reply_markup=get_start_menu_kbds())
    await state.clear()
    await state.set_state(ActionSelection.choice_action)

@user_private_router.callback_query(ActionSelection.choice_action, F.data.startswith('users'))
async def users(callback: CallbackQuery, state: FSMContext):
    await state.update_data(choice_action=callback.data)
    await callback.message.edit_text('Статистика по мафии', reply_markup=get_callback_btns(btns={
        'Добавить игрока': 'add_user',
        'Посмотреть всех в клубе': 'get_all_in_club',
        'назад': 'back',
    }, sizes=(2, 1)))
    await state.set_state(ActionSelection.users)

@user_private_router.callback_query(or_f(ActionSelection.users, AddUser.confirmation), F.data.startswith('add_user'))
async def add_nickname(callback:CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите никнейм')
    await state.set_state(AddUser.nickname)

@user_private_router.message(AddUser.nickname)
async def add_gender(message:types.Message, state: FSMContext):
    await state.update_data(nickname=message.text)
    await message.answer('Выберите пол', reply_markup=get_callback_btns(btns={
        'Мужской': 'Мужской',
        'Женский': 'Женский',
    }))
    await state.set_state(AddUser.gender)

@user_private_router.callback_query(AddUser.gender)
async def add_club(callback:CallbackQuery, state: FSMContext):
    await state.update_data(gender=callback.data)
    await callback.message.answer('Введите игровой клуб. Если нет, пропустите и идите дальше.')
    await state.set_state(AddUser.club)

@user_private_router.message(AddUser.club)
async def add_confirmation(message:types.Message, state: FSMContext):
    await state.update_data(club=message.text)
    data = await state.get_data()
    await message.answer(f"игровой ник - {data['nickname']}, \n" 
    f"пол - {data['gender']}, \n" 
    f"игровой клуб - {data['club']}, \n" 
    f"Все верно?", reply_markup=get_callback_btns(btns={
        'Да': 'yes',
        'Нет': 'add_user',
    }))
    await state.set_state(AddUser.confirmation)

@user_private_router.callback_query(AddUser.confirmation, F.data.startswith('yes'))
async def add_user(callback:CallbackQuery, session: AsyncSession, state: FSMContext):
    data = await state.get_data()
    await orm_add_user(session, data)
    await callback.message.answer(f"Игрок {data['nickname']} добавлен")
    await callback.message.answer('Статистика по мафии', reply_markup=get_start_menu_kbds())
    await state.clear()
    await state.set_state(ActionSelection.choice_action)

@user_private_router.callback_query(F.data.startswith('back'),  StateFilter('*'))
async def back(callback:CallbackQuery, state: FSMContext):
    curent_state = await state.get_state()
    if curent_state.split(':')[1] == 'type_game':
        await callback.message.edit_text('Статистика по мафии', reply_markup=get_start_menu_kbds())
        await state.clear()
        await state.set_state(ActionSelection.choice_action)
    elif curent_state.split(':')[1] == 'add_game_or_show_game':
        await callback.message.edit_text('Выберите вид игры', reply_markup=get_callback_btns(btns={
        'Рейтинг' : 'ranked',
        'Турнир' : 'tournament',
        'Назад' : 'back',
    }))
        await state.set_state(ActionSelection.type_game)
    elif curent_state.split(':')[1] == 'users':
        await callback.message.edit_text('Статистика по мафии', reply_markup=get_start_menu_kbds())
        await state.clear()
        await state.set_state(ActionSelection.choice_action)
    elif curent_state.split(':')[1] == 'choice_action':
        await callback.message.edit_text('Статистика по мафии', reply_markup=get_start_menu_kbds())
        await state.clear()
        await state.set_state(ActionSelection.choice_action)

@user_private_router.callback_query(ActionSelection.users, F.data.startswith('get_all_in_club'))
async def get_all_in_club(callback:CallbackQuery, session: AsyncSession, state:FSMContext):
    users = await orm_get_all_users(session)
    data_users = [f"Ник - {user.nickname}  *  Пол - {user.gender}  *   клуб - {user.club}" for user in users] 
    await callback.message.answer("\n".join(data_users))
    await callback.message.answer('Статистика по мафии', reply_markup=get_start_menu_kbds())
    await state.set_state(ActionSelection.choice_action)

@user_private_router.callback_query(ActionSelection.choice_action, F.data.startswith('games'))
async def games(callback: CallbackQuery, state: FSMContext):
    await state.update_data(choice_action=callback.data)
    await callback.message.edit_text('Выберите вид игры', reply_markup=get_callback_btns(btns={
        'Рейтинг' : 'ranked',
        'Турнир' : 'tournament',
        'Назад' : 'back',
    }))
    s = 'type_game'
    await state.set_state(ActionSelection.type_game)

@user_private_router.callback_query(ActionSelection.type_game) 
async def choice_type_game(callback: CallbackQuery, state: FSMContext):    
    await state.update_data(type_game=callback.data)
    await callback.message.edit_text('Что хотите сделать?', reply_markup=get_callback_btns(btns={
        'Добавить игру': 'add_game',
        'посмотреть игру': 'show_game',
        'Назад' : 'back',
    }))
    await state.set_state(ActionSelection.add_game_or_show_game)

@user_private_router.callback_query(ActionSelection.add_game_or_show_game, F.data.startswith('add_game'))
async def start_handler_for_add_nickname(callback: CallbackQuery, state:FSMContext, session:AsyncSession):
    all_nicknames = await orm_get_all_nicknames(session)
    await state.update_data(add_game_or_swow_game=all_nicknames)
    await callback.message.edit_text("Выберите игроков. Игроков добавленно: 0", reply_markup=get_paginator_keyboard(data=all_nicknames))
    await state.set_state(AddGame.add_players_in_game)

@user_private_router.callback_query(F.data.startswith("page_"), AddGame.add_players_in_game)
async def handle_pagination(callback: CallbackQuery, state: FSMContext):
    page = int(callback.data.split('_')[1])
    data = await state.get_data()
    nicknames = data.get("add_game_or_swow_game", [])
    await callback.message.edit_reply_markup(reply_markup=get_paginator_keyboard(page=page, data=nicknames))

@user_private_router.callback_query(AddGame.add_players_in_game, F.data.startswith('select_'))
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

@user_private_router.callback_query(AddGame.add_role,  F.data.startswith('add_game')) 
async def correct_users_in_game(callback: CallbackQuery, state: FSMContext, session:AsyncSession):
    data = await state.get_data()
    all_nicknames = await orm_get_all_nicknames(session)
    await state.update_data(add_game_or_swow_game=all_nicknames) 
    await state.update_data(add_players_in_game=[]) 
    await callback.message.edit_text("Выберите один из вариантов:", reply_markup=get_paginator_keyboard(data=all_nicknames))
    await state.set_state(AddGame.add_players_in_game)

@user_private_router.callback_query(AddGame.add_role, F.data.startswith('add_role'))
async def add_sherif(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    nicknames = data["add_players_in_game"]
    roles =['Мирный','Мирный','Мирный','Мирный','Мирный','Мирный','Мирный','Мирный','Мирный','Мирный']
    await state.update_data(add_role=roles)
    await callback.message.edit_text("Выберите шерифа игры:", reply_markup=get_add_sheriff_kbds(data=nicknames)) 

@user_private_router.callback_query(AddGame.add_role, F.data.startswith('sheriff_'))
async def add_don(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    nicknames = data["add_players_in_game"]
    nick = callback.data.split('_')[1]
    roles = data.get('add_role')
    roles[nicknames.index(nick)] = 'Шериф'
    await state.update_data(add_role=roles)
    await callback.message.edit_text("Выберите Дона игры:", reply_markup=get_add_don_kbds(data=nicknames)) 

@user_private_router.callback_query(AddGame.add_role, F.data.startswith('don_'))
async def add_fol(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    nicknames = data["add_players_in_game"]
    nick = callback.data.split('_')[1]
    roles = data.get('add_role')
    roles[nicknames.index(nick)] = 'Дон'
    await state.update_data(add_role=roles)
    await callback.message.edit_text("Выберите первую мафию:", reply_markup=get_add_mafia_kbds(data=nicknames))

@user_private_router.callback_query(AddGame.add_role, F.data.startswith('mafia_'))
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

@user_private_router.callback_query(AddGame.add_fol, F.data.startswith('add_role'))
async def correct_roles_in_game(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    nicknames = data["add_players_in_game"]
    roles =['Мирный','Мирный','Мирный','Мирный','Мирный','Мирный','Мирный','Мирный','Мирный','Мирный']
    await state.update_data(add_role=roles)
    await callback.message.edit_text("Выберите шерифа игры:", reply_markup=get_add_sheriff_kbds(data=nicknames)) 
    await state.set_state(AddGame.add_role)

@user_private_router.callback_query(AddGame.add_fol, F.data.startswith('add_fol'))
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

@user_private_router.callback_query(AddGame.add_fol, or_f(F.data.startswith('0'), F.data.startswith('1'), F.data.startswith('2'), F.data.startswith('3'), F.data.startswith('4')))
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

@user_private_router.callback_query(AddGame.add_point, F.data.startswith('add_fol'))
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
    
@user_private_router.callback_query(AddGame.add_point, F.data.startswith('add_point'))
async def start_handler_for_add_point(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    nicknames = data["add_players_in_game"]
    points = data.get('add_point', [])
    await callback.message.answer(f'Выберите количество доп балов для {nicknames[len(points)]}', reply_markup=get_add_point_kbds())

@user_private_router.callback_query(AddGame.add_point, or_f(F.data.startswith('-0.'), F.data.startswith('0'), F.data.startswith('1')))
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

@user_private_router.callback_query(AddGame.add_first_dead, F.data.startswith('add_point'))
async def correct_point_in_game(callback: CallbackQuery, state: FSMContext):
    await state.update_data(add_point=[])
    data = await state.get_data()
    nicknames = data["add_players_in_game"]
    points = data.get('add_point', [])    
    await callback.message.edit_text(f'Выберите количество доп балов для {nicknames[len(points)]}', reply_markup=get_add_point_kbds())
    await state.set_state(AddGame.add_point)

@user_private_router.callback_query(AddGame.add_first_dead, F.data.startswith('add_first_dead'))
async def add_first_dead(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    nicknames = data["add_players_in_game"]
    await callback.message.answer('Выберите ПУ игрока', reply_markup=get_first_dead_kbds(data=nicknames))  
    await state.set_state(AddGame.add_best_step)

@user_private_router.callback_query(AddGame.add_best_step, F.data.startswith('fd'))
async def start_handler_best_step(callback: CallbackQuery, state: FSMContext):
    await state.update_data(add_first_dead=callback.data.split('_')[1])
    data = await state.get_data()
    nicknames = data['add_players_in_game']
    best_steb =data.get('add_best_step', [])
    await callback.message.edit_text('Выберите лучший ход ПУ игрока', reply_markup=get_best_step_kbds(data=nicknames))

@user_private_router.callback_query(AddGame.add_best_step, F.data.startswith('bs'))
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

@user_private_router.callback_query(AddGame.winner, F.data.startswith('add_best_step'))
async def correct_best_step(callback: CallbackQuery, state: FSMContext):
    await state.update_data(add_best_step=[])
    data = await state.get_data()
    nicknames = data["add_players_in_game"]
    points = data.get('add_point', [])    
    await callback.message.edit_text(f'Выберите лучший ход ПУ игрока', reply_markup=get_best_step_kbds(data=nicknames))
    await state.set_state(AddGame.add_best_step)

@user_private_router.callback_query(AddGame.winner, F.data.startswith('winner'))
async def add_winner(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Выберите победителя', reply_markup=get_callback_btns(btns={
        'Мирные':'Мирный',
        'Мафия':'Мафия',
        'Ничья':'Ничья',
        }))
    await state.set_state(AddGame.date_game)

@user_private_router.callback_query(AddGame.date_game, or_f(F.data.startswith('Мирный'), F.data.startswith('Мафия'), F.data.startswith('Ничья')))
async def add_date_game(callback: CallbackQuery, state: FSMContext):
    await state.update_data(add_winner=callback.data)
    await callback.message.answer("Выберите дату:", reply_markup=await SimpleCalendar().start_calendar())

@user_private_router.callback_query(AddGame.date_game, F.data.startswith('simple_calendar'))
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
       
@user_private_router.callback_query(AddGame.review, F.data.startswith('save'))
async def save_game(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    await orm_save_game(session, data=data )
    await state.clear()

    await callback.message.edit_text('Игра сохранена')
    await callback.message.answer('Статистика по мафии', reply_markup=get_start_menu_kbds())
    await state.set_state(ActionSelection.choice_action)

@user_private_router.callback_query(AddGame.review, F.data.startswith('cancel'))
async def cancel_game(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer('Статистика по мафии', reply_markup=get_start_menu_kbds())
    await state.set_state(ActionSelection.choice_action)

@user_private_router.callback_query(ActionSelection.add_game_or_show_game, F.data.startswith('show_game'))
async def show_game(callback: CallbackQuery, state: FSMContext):

    await callback.message.answer("Выберите первую дату:", reply_markup=await SimpleCalendar().start_calendar())

@user_private_router.callback_query(ActionSelection.add_game_or_show_game, F.data.startswith('simple_calendar'))
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
            games = await orm_get_games(session, data=data)
            for game in games:
                list_game = await transformation_db_data(game)
                table_in_game = '\n'.join(list_game)
                await callback.message.answer(table_in_game)
            await callback.message.answer('Статистика по мафии', reply_markup=get_start_menu_kbds())
            await state.clear()
            await state.set_state(ActionSelection.choice_action)
        else:
            await callback.message.edit_text("Выберите вторую дату:", reply_markup=await SimpleCalendar().start_calendar())
    else:
        await callback.message.edit_text("Выберите дату или с помощью '<' и '>' выберите месяц:", reply_markup=await SimpleCalendar().start_calendar())

@user_private_router.callback_query(ActionSelection.choice_action, F.data.startswith('statistics'))
async def statistics(callback: CallbackQuery, state: FSMContext):
    await state.update_data(choice_action=callback.data)
    await callback.message.edit_text('Статистика по мафии для:', reply_markup=get_callback_btns(btns={
        'Cтаистика по всем игрокам':'all_statistic',
        'Cтатистика одного игрока':'one_statistic',
        'Cравнить двух игроков':'doble_statistic',
        'Назад':'back'
    }, sizes=(1,)))






















    

