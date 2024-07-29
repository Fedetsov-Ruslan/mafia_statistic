from aiogram import Router, F, types
from aiogram.types import Message
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.kbds.inline import get_callback_btns


class ActionSelection(StatesGroup):
    choice_action = State()
    users = State()
    games = State()
    statistics = State()
    viewing_user = State()


class AddUser(StatesGroup):
    nickname = State()
    sex = State()
    club = State()
    birthdate = State()

user_private_router = Router()

@user_private_router.message(CommandStart())
async def start(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer('Статистика по мафии', reply_markup=get_callback_btns(btns={
        'Игроки': 'users',
        'Игры': 'games',
        'Статистика': 'statistics',
    }))
    await state.set_state(ActionSelection.choice_action)

@user_private_router.message(StateFilter(ActionSelection.choice_action), F.data.startswith('users'))
async def users(callback: types.CallbackQuery, state: FSMContext):
    pass