from aiogram import Router, F
from aiogram.types import  CallbackQuery
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext

from app.kbds.inline import get_callback_btns, get_start_menu_kbds
from app.handlers.user_private_routers.users_handlers import user_router
from app.handlers.user_private_routers.add_game_handlers import add_game_router
from app.handlers.user_private_routers.show_game_handlers import show_game_router
from app.handlers.user_private_routers.statistic_handlers import statistic_router
from app.handlers.fsm.states import ActionSelection, AddGame


user_private_router = Router()

user_private_router.include_router(user_router)
user_private_router.include_router(add_game_router)
user_private_router.include_router(show_game_router)
user_private_router.include_router(statistic_router)

    
@user_private_router.message(CommandStart())
async def start(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Статистика по мафии', reply_markup=get_start_menu_kbds())
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


@user_private_router.callback_query(AddGame.review, F.data.startswith('cancel'))
async def cancel_game(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer('Статистика по мафии', reply_markup=get_start_menu_kbds())
    await state.set_state(ActionSelection.choice_action)



