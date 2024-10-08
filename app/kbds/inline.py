from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


POINT_IN_GAME = {
        '-0.5': '-0.5',
        '-0.4': '-0.4',
        '-0.3': '-0.3',
        '-0.2': '-0.2',
        '-0.1': '-0.1',
        '0': '0',
        '0.1': '0.1',
        '0.2': '0.2',
        '0.25': '0.25',
        '0.3': '0.3',
        '0.4': '0.4',
        '0.5': '0.5',
        '0.6': '0.6',
        '0.7': '0.7',
        '0.8': '0.8',
        }


def get_start_menu_kbds():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="👤 Игроки", callback_data="users"))
    keyboard.add(InlineKeyboardButton(text="🎮 Игры", callback_data="games"))
    keyboard.add(InlineKeyboardButton(text="📊 Статистика", callback_data="statistics"))
    return keyboard.as_markup()


def get_callback_btns(
        *,
        btns: dict[str,str],
        sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data))
    return keyboard.adjust(*sizes).as_markup()


def get_paginator_keyboard(*, 
                           page: int = 0, 
                           items_per_page: int=10,
                           data: list[str] = [],
                           sizes: tuple[int] = (2,)):
    keyboard = InlineKeyboardBuilder()
    start = page * items_per_page
    end = start + items_per_page
    for user in data[start:end]:
        if user in data:
            keyboard.add(InlineKeyboardButton(text=user, callback_data=f"select_{user}"))
        else:
            keyboard.add(InlineKeyboardButton(text=user, callback_data=f"select_{user}"))

    navigation_buttons = []
    if start > 0:
        navigation_buttons.append(InlineKeyboardButton(text="Предыдущая страница", callback_data=f"page_{page - 1}"))
    if end < len(data):
        navigation_buttons.append(InlineKeyboardButton(text="Следующая страница", callback_data=f"page_{page + 1}"))
    keyboard.add(*navigation_buttons)
    return keyboard.adjust(*sizes).as_markup()


def get_first_dead_kbds(
        *,
        data: list[str] = [],):
    keyboard = InlineKeyboardBuilder()
    for user in data:
        keyboard.add(InlineKeyboardButton(text=user, callback_data=f"fd_{user}"))
    keyboard.add(InlineKeyboardButton(text='ПУ нету', callback_data='no_dead'))
    return keyboard.adjust(5,5,1).as_markup()


def get_club_kbds(
        *,
        data: list[str] = [],):
    keyboard = InlineKeyboardBuilder()
    for club in data:
        keyboard.add(InlineKeyboardButton(text=club, callback_data=club))
    return keyboard.adjust(5,5,1).as_markup()


def get_best_step_kbds(
        *,
        data: list[str] = [],):
    keyboard = InlineKeyboardBuilder()
    for user in data:
        keyboard.add(InlineKeyboardButton(text=user, callback_data=f"bs_{user}"))
    return keyboard.adjust(5,5).as_markup()


def get_add_sheriff_kbds(
        *,
        data: list[str] = [],):
    keyboard = InlineKeyboardBuilder()
    for user in data:
        keyboard.add(InlineKeyboardButton(text=user, callback_data=f"sheriff_{user}"))
    return keyboard.adjust(5,5).as_markup()


def get_add_don_kbds(
        *,
        data: list[str] = [],):
    keyboard = InlineKeyboardBuilder()
    for user in data:
        keyboard.add(InlineKeyboardButton(text=user, callback_data=f"don_{user}"))
    return keyboard.adjust(5,5).as_markup()


def get_add_mafia_kbds(
        *,
        data: list[str] = [],):
    keyboard = InlineKeyboardBuilder()
    for user in data:
        keyboard.add(InlineKeyboardButton(text=user, callback_data=f"mafia_{user}"))
    return keyboard.adjust(5,5).as_markup()


def get_add_point_kbds():
    keyboard = InlineKeyboardBuilder()

    for key, value in POINT_IN_GAME.items():
        keyboard.add(InlineKeyboardButton(text=key, callback_data=value))
    return keyboard.adjust(5,5,5).as_markup()