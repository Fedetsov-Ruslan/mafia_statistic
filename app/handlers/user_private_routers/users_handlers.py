from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.filters import or_f

from app.handlers.fsm.states import ActionSelection, AddUser, AddGame
from app.kbds.inline import get_callback_btns, get_start_menu_kbds, get_club_kbds
from app.database.orm_query import orm_add_user, orm_get_all_users, orm_get_clubs

user_router = Router()


@user_router.callback_query(ActionSelection.choice_action, F.data.startswith('users'))
async def users(callback: CallbackQuery, state: FSMContext):
    await state.update_data(choice_action=callback.data)
    await callback.message.edit_text('Статистика по мафии', reply_markup=get_callback_btns(btns={
        'Добавить игрока': 'add_user',
        'Посмотреть всех в клубе': 'get_all_in_club',
        'назад': 'back',
    }, sizes=(2, 1)))
    await state.set_state(ActionSelection.users)


@user_router.callback_query(or_f(ActionSelection.users, AddUser.confirmation), F.data.startswith('add_user'))
async def add_nickname(callback:CallbackQuery, state: FSMContext):
    await callback.message.answer('Введите никнейм')
    await state.set_state(AddUser.nickname)


@user_router.message(AddUser.nickname)
async def add_gender(message:types.Message, state: FSMContext):
    await state.update_data(nickname=message.text)
    await message.answer('Выберите пол', reply_markup=get_callback_btns(btns={
        'Мужской': 'Мужской',
        'Женский': 'Женский',
    }))
    await state.set_state(AddUser.gender)


@user_router.callback_query(AddUser.gender)
async def add_club(callback:CallbackQuery, state: FSMContext):
    await state.update_data(gender=callback.data)
    await callback.message.answer('Введите игровой клуб. Если нет, пропустите и идите дальше.')
    await state.set_state(AddUser.club)


@user_router.message(AddUser.club)
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


@user_router.callback_query(AddUser.confirmation, F.data.startswith('yes'))
async def add_user(callback:CallbackQuery, session: AsyncSession, state: FSMContext):
    data = await state.get_data()
    await orm_add_user(session, data)
    await callback.message.answer(f"Игрок {data['nickname']} добавлен")
    await callback.message.answer('Статистика по мафии', reply_markup=get_start_menu_kbds())
    await state.clear()
    await state.set_state(ActionSelection.choice_action)
    

@user_router.callback_query(ActionSelection.users, F.data.startswith('get_all_in_club'))
async def choose_club(callback:CallbackQuery, state:FSMContext, session: AsyncSession):
    clubs = await orm_get_clubs(session)
    club_list = [club for club in clubs]
    await callback.message.edit_text('Выберите игровой клуб', reply_markup=get_club_kbds(data=club_list))
    await state.set_state(ActionSelection.club)


@user_router.callback_query(ActionSelection.club)
async def get_all_in_club(callback:CallbackQuery, session: AsyncSession, state:FSMContext):
    club = callback.data
    users = await orm_get_all_users(session, club)
    data_users = [f"Ник - {user.nickname}  *  Пол - {user.gender}  *   клуб - {user.club}" for user in users] 
    while data_users != []:
        chunk = data_users[:20]
        await callback.message.answer("\n".join(chunk))
        data_users = data_users[20:]
    await callback.message.answer('Статистика по мафии', reply_markup=get_start_menu_kbds())
    await state.set_state(ActionSelection.choice_action)