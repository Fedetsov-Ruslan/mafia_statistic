from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command, StateFilter, or_f
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram_calendar import  SimpleCalendar

from app.database.orm_query import orm_add_user, orm_get_all_nicknames, orm_get_all_users
from app.kbds.inline import get_best_step_kbds, get_callback_btns, get_first_dead_kbds, get_paginator_keyboard


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
    revie = State()


class AddUser(StatesGroup):

    nickname = State()
    gender = State()
    club = State()
    confirmation = State()
    add_complite = State()


user_private_router = Router()
    
@user_private_router.message(CommandStart())
async def start(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Статистика по мафии', reply_markup=get_callback_btns(btns={
        'Игроки': 'users',
        'Игры': 'games',
        'Статистика': 'statistics',
    }, sizes=(3, )))
    await state.set_state(ActionSelection.choice_action)

@user_private_router.callback_query(ActionSelection.choice_action, F.data.startswith('users'))
async def users(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Статистика по мафии', reply_markup=get_callback_btns(btns={
        'Добавить игрока': 'add_user',
        'Посмотреть статистику по нику': 'viewing_user',
        'Посмотреть всех в клубе': 'get_all_in_club',
        'назад': 'back',
    }, sizes=(2, 2)))
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
    await callback.message.answer('Статистика по мафии', reply_markup=get_callback_btns(btns={
        'Игроки': 'users',
        'Игры': 'games',
        'Статистика': 'statistics',
    }, sizes=(3, )))
    await state.clear()
    await state.set_state(ActionSelection.choice_action)


@user_private_router.callback_query(ActionSelection.users, F.data.startswith('get_all_in_club'))
async def get_all_in_club(callback:CallbackQuery, session: AsyncSession, state:FSMContext):
    users = await orm_get_all_users(session)

    for user in users:
        await callback.message.answer(
            f"Игровой ник - {user.nickname}  *   " 
            f"Пол - {user.gender}   *   " 
            f"Игровой клуб - {user.club}")
    await callback.message.answer('Статистика по мафии', reply_markup=get_callback_btns(btns={
               'Игроки': 'users',
            'Игры': 'games',
            'Статистика': 'statistics',
            }, sizes=(3, )))
    await state.set_state(ActionSelection.choice_action)

@user_private_router.callback_query(ActionSelection.choice_action, F.data.startswith('games'))
async def games(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Выберите вид игры', reply_markup=get_callback_btns(btns={
        'Рейтинг' : 'ranked',
        'Турнир' : 'tournament',
        'Назад' : 'back',
    }))

    await state.set_state(ActionSelection.type_game)

@user_private_router.callback_query(ActionSelection.type_game, or_f(F.data.startswith('ranked'), F.data.startswith('tournament')))
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
    
    nicknames = await orm_get_all_nicknames(session)
    
    await state.update_data(add_game_or_swow_game=nicknames)
    
    await callback.message.edit_text("Выберите один из вариантов:", reply_markup=get_paginator_keyboard(data=nicknames))
    await state.set_state(AddGame.add_players_in_game)

@user_private_router.callback_query(F.data.startswith("page_"), AddGame.add_players_in_game)
async def handle_pagination(callback: CallbackQuery, state: FSMContext):
    page = int(callback.data.split('_')[1])
    data = await state.get_data()
    print(f'data{data}')
    nicknames = data.get("add_game_or_swow_game", [])
    await callback.message.edit_reply_markup(reply_markup=get_paginator_keyboard(page=page, data=nicknames))
    # await bot.answer_callback_query(callback_query.id)

@user_private_router.callback_query(AddGame.add_players_in_game, F.data.startswith('select_'))
async def add_nickname(callback: CallbackQuery, state: FSMContext, session:AsyncSession): 
    data = await state.get_data()
    
    type_game = data['type_game']
    all_nicknames = data['add_game_or_swow_game']
    nick = callback.data.split('_')[1]
    data = await state.get_data()
    
    nicknames = data.get("add_players_in_game", [])

    if nick not in nicknames:
        nicknames.append(nick)
        
        await state.update_data(add_players_in_game=nicknames)

        if len(nicknames) < 10:
            
            page = 0  
            await callback.message.edit_text(f'Вы добавили {nick}. Всего игроков добавлено: {len(nicknames)}',reply_markup=get_paginator_keyboard(page=page, data=all_nicknames))
            # await bot.answer_callback_query(callback.id)
        else:
            await callback.message.answer(f"Вы выбрали: {', '.join(nicknames)}", reply_markup=get_callback_btns(btns={
                'Ок': 'add_role'
            }))       
            await state.set_state(AddGame.add_role)
            # await bot.answer_callback_query(callback.id)
    else:
        page = 0  
        try:
            await callback.message.edit_text(f'Игрок {nick} уже был добавлен, выберите другого. \n Игроков добавлено: {len(nicknames)}',reply_markup=get_paginator_keyboard(page=page, data=all_nicknames))
        except:
            await callback.message.edit_text(f'ошибка при добавлении. Если ошибка повторится, обобратитесь к Математику', reply_markup=get_callback_btns(btns={
        'Игроки': 'users',
        'Игры': 'games',
        'Статистика': 'statistics',
    }, sizes=(3, )))
            await state.clear()
            await state.set_state(ActionSelection.choice_action)

@user_private_router.callback_query(AddGame.add_role, F.data.startswith('add_role'))
async def start_handler_for_add_role(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    nicknames = data["add_players_in_game"]
    roles = data.get('add_role', [])    
    await callback.message.answer(f'Выберите роль для {nicknames[len(roles)]}', reply_markup=get_callback_btns(btns={
            'Мирный': 'mir',
            'Мафия': 'mafia',
            'Шериф': 'Sheriff',
            'Дон': 'Don',
        }))
    
@user_private_router.callback_query(AddGame.add_role, or_f(F.data.startswith('mir'), F.data.startswith('mafia'), F.data.startswith('Sheriff'), F.data.startswith('Don')))
async def add_role(callback: CallbackQuery, state: FSMContext):
    role = callback.data
    data = await state.get_data()
    nicknames = data["add_players_in_game"]
    roles = data.get('add_role', [])
    roles.append(role)
    await state.update_data(add_role=roles)
    if len(roles) < 10:

        await callback.message.edit_text(f'Выберите роль для {nicknames[len(roles)]}', reply_markup=get_callback_btns(btns={
            'Мирный': 'mir',
            'Мафия': 'mafia',
            'Шериф': 'Sheriff',
            'Дон': 'Don',
        }))
    else:
        combined = [f'{nick} - {role}' for nick, role in zip(nicknames, roles)]
        await callback.message.edit_text(' ;'.join(combined), reply_markup=get_callback_btns(btns={
            'Ок': 'add_fol'
        }))
        await state.set_state(AddGame.add_fol)

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
            'Ок': 'add_point'
        }))
        await state.set_state(AddGame.add_point)
    
@user_private_router.callback_query(AddGame.add_point, F.data.startswith('add_point'))
async def start_handler_for_add_point(callback: CallbackQuery, state: FSMContext):

    data = await state.get_data()
    nicknames = data["add_players_in_game"]
    points = data.get('add_point', [])
    await callback.message.answer(f'Выберите количество очков для {nicknames[len(points)]}', reply_markup=get_callback_btns(btns={
        '-0.5': '-0.5',
        '0': '0',
        '0.1': '0.1',
        '0.2': '0.2',
        '0.3': '0.3',
        '0.4': '0.4',
        '0.5': '0.5',
        '0.6': '0.6',
        '0.7': '0.7',
        '0.8': '0.8',
        '0.9': '0.9',
        '1': '1',
        '1.1': '1.1',
        '1.2': '1.2',
        '1.3': '1.3',
        '1.4': '1.4',
        '1.5': '1.5',
    }, sizes=(5, 5, 5)))

@user_private_router.callback_query(AddGame.add_point, or_f(F.data.startswith('-0.5'), F.data.startswith('0'), F.data.startswith('1')))
async def add_point(callback: CallbackQuery, state: FSMContext):
    point = callback.data
    data = await state.get_data()
    nicknames = data["add_players_in_game"]
    points = data.get('add_point', [])
    points.append(point)
    await state.update_data(add_point=points)
    if len(points) < 10:
        await callback.message.edit_text(f'Выберите количество очков для {nicknames[len(points)]}', reply_markup=get_callback_btns(btns={
            '-0.5': '-0.5',
            '0': '0',
            '0.1': '0.1',
            '0.2': '0.2',
            '0.3': '0.3',
            '0.4': '0.4',
            '0.5': '0.5',
            '0.6': '0.6',
            '0.7': '0.7',
            '0.8': '0.8',
            '0.9': '0.9',
            '1': '1',
             '1.1': '1.1',
            '1.2': '1.2',
            '1.3': '1.3',
            '1.4': '1.4',
            '1.5': '1.5',
        }, sizes=(5, 5, 5)))
    else:
        combined = [f'{nick} - {point}' for nick, point in zip(nicknames, points)]
        await callback.message.edit_text(';    '.join(combined), reply_markup=get_callback_btns(btns={
            'Ок': 'add_first_dead'
        }))
        await state.set_state(AddGame.add_first_dead)

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
            'Ок': 'revie'
        }))
        await state.set_state(AddGame.winner)

@user_private_router.callback_query(AddGame.winner, F.data.startswith('revie'))
async def add_winner(callback: CallbackQuery, state: FSMContext):

    await callback.message.answer('Выберите победителя', reply_markup=get_callback_btns(btns={
        'Мирные':'mir',
        'Мафия':'mafia',
        'Ничья':'draw',
        }))
    await state.set_state(AddGame.date_game)

@user_private_router.callback_query(AddGame.date_game)
async def add_date_game(callback: CallbackQuery, state: FSMContext):
    await state.update_data(add_winner=callback.data)
    await callback.message.answer("Выберите дату:", reply_markup=await SimpleCalendar().start_calendar())

    await state.set_state(AddGame.revie)

@user_private_router.callback_query(AddGame.revie)
async def add_revie(callback: CallbackQuery, state: FSMContext):
    await state.update_data(add_date_game=callback.data.split('DAY:')[1].replace(':', '-'))
    data = await state.get_data()
    print(data)











    

