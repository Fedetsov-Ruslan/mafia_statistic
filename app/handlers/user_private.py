from aiogram import Router, F, types
from aiogram.types import Message
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.orm_query import orm_add_user
from app.kbds.inline import get_callback_btns


class ActionSelection(StatesGroup):
    choice_action = State()
    users = State()
    games = State()
    statistics = State()
    viewing_user = State()


class AddUser(StatesGroup):

    nickname = State()
    gender = State()
    club = State()
    birthdate = State()
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
        'Найти по нику': 'viewing_user',
        'Посмотреть всех в клубе': 'get_all_in_club',
        'назад': 'back',
    }, sizes=(2, 2)))
    await state.set_state(ActionSelection.users)

@user_private_router.callback_query(ActionSelection.users, F.data.startswith('add_user'))
async def add_nickname(callback:types.CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите никнейм')

    await state.set_state(AddUser.nickname)

@user_private_router.message(AddUser.nickname)
async def add_gender(message:types.Message, state: FSMContext):
    await state.update_data(nickname=message.text)
    await message.answer('Выберите пол', reply_markup=get_callback_btns(btns={
        'Мужской': 'male',
        'Женский': 'female',
    }))

    await state.set_state(AddUser.gender)

@user_private_router.callback_query(AddUser.gender)
async def add_club(callback:types.CallbackQuery, state: FSMContext):
    await state.update_data(gender=callback.data)
    await callback.message.answer('Введите игровой клуб. Если нет, пропустите и идите дальше.')

    await state.set_state(AddUser.club)


# async def add_birthdate(message:types.Message, state: FSMContext):
#     await state.update_data(club=message.text)
#     await message.answer('Введите дату рождения. Или пропустите и идите дальше.')

#     await state.set_state(AddUser.birthdate)

@user_private_router.message(AddUser.club)
async def add_user(message:types.Message, session: AsyncSession, state: FSMContext):
    await state.update_data(club=message.text)
    data = await state.get_data()


    await orm_add_user(session, data)
    await state.set_state(ActionSelection.choice_action)
    await state.set_state(AddUser.add_complite)
    await message.answer('Статистика по мафии', reply_markup=get_callback_btns(btns={
        'Игроки': 'users',
        'Игры': 'games',
        'Статистика': 'statistics',
    }))


    

