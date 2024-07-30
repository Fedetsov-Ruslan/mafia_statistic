from aiogram import Router, F, types
from aiogram.types import Message
from aiogram.filters import CommandStart, Command, StateFilter, or_f
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession


from app.database.orm_query import orm_add_user, orm_get_all_nicknames, orm_get_all_users
from app.kbds.inline import get_callback_btns, get_paginator_keyboard


class ActionSelection(StatesGroup):
    choice_action = State()
    users = State()
    games = State()
    statistics = State()
    viewing_user = State()
    get_all_in_club = State()
    type_game = State()
    add_game_or_show_game = State()
    add_players_in_game = State()
    add_role = State()



class AddUser(StatesGroup):

    nickname = State()
    gender = State()
    club = State()
    confirmation = State()
    add_complite = State()

user_private_router = Router()

    
@user_private_router.message(CommandStart())
async def start(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer('Статистика по мафии', reply_markup=get_callback_btns(btns={
        'Игроки': 'users',
        'Игры': 'games',
        'Статистика': 'statistics',
    }, sizes=(3, )))
    await state.set_state(ActionSelection.choice_action)

@user_private_router.callback_query(ActionSelection.choice_action, F.data.startswith('users'))
async def users(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Статистика по мафии', reply_markup=get_callback_btns(btns={
        'Добавить игрока': 'add_user',
        'Посмотреть статистику по нику': 'viewing_user',
        'Посмотреть всех в клубе': 'get_all_in_club',
        'назад': 'back',
    }, sizes=(2, 2)))
    await state.set_state(ActionSelection.users)

@user_private_router.callback_query(or_f(ActionSelection.users, AddUser.confirmation), F.data.startswith('add_user'))
async def add_nickname(callback:types.CallbackQuery, state: FSMContext):
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
async def add_club(callback:types.CallbackQuery, state: FSMContext):
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
async def add_user(callback:types.CallbackQuery, session: AsyncSession, state: FSMContext):
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
async def get_all_in_club(callback:types.CallbackQuery, session: AsyncSession, state:FSMContext):
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
async def games(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Выберите вид игры', reply_markup=get_callback_btns(btns={
        'Рейтинг' : 'ranked',
        'Турнир' : 'tournament',
        'Назад' : 'back',
    }))

    await state.set_state(ActionSelection.type_game)

@user_private_router.callback_query(ActionSelection.type_game, or_f(F.data.startswith('ranked'), F.data.startswith('tournament')))
async def choice_type_game(callback: types.CallbackQuery, state: FSMContext):    
    await state.update_data(type_game=callback.data)

    await callback.message.edit_text('Что хотите сделать?', reply_markup=get_callback_btns(btns={
        'Добавить игру': 'add_game',
        'посмотреть игру': 'show_game',
        'Назад' : 'back',
    }))

    await state.set_state(ActionSelection.add_game_or_show_game)

@user_private_router.callback_query(ActionSelection.add_game_or_show_game, F.data.startswith('add_game'))
async def start_handler(callback: types.CallbackQuery, state:FSMContext, session:AsyncSession):
    
    nicknames = await orm_get_all_nicknames(session)
    
    await state.update_data(add_game_or_swow_game=nicknames)
    print(nicknames)
    await callback.message.edit_text("Выберите один из вариантов:", reply_markup=get_paginator_keyboard(data=nicknames))
    await state.set_state(ActionSelection.add_players_in_game)

@user_private_router.callback_query(F.data.startswith("page_"), ActionSelection.add_players_in_game)
async def handle_pagination(callback_query: types.CallbackQuery, state: FSMContext):
    page = int(callback_query.data.split('_')[1])
    data = await state.get_data()
    print(f'data{data}')
    nicknames = data.get("add_game_or_swow_game", [])
    await callback_query.message.edit_reply_markup(reply_markup=get_paginator_keyboard(page=page, data=nicknames))
    # await bot.answer_callback_query(callback_query.id)

@user_private_router.callback_query(ActionSelection.add_players_in_game, F.data.startswith('select_'))
async def add_game(callback: types.CallbackQuery, state: FSMContext, session:AsyncSession): 
    data = await state.get_data()
    print(f'data2{data}')
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
            await callback.message.answer(f"Вы выбрали: {', '.join(nicknames)}")       
            await state.set_state(ActionSelection.add_role)
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
    

