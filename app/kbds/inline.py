from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

def get_start_menu_kbds():
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="👤 Users", callback_data="users"))
    keyboard.add(InlineKeyboardButton(text="🎮 Games", callback_data="games"))
    keyboard.add(InlineKeyboardButton(text="📊 Statistics", callback_data="statistics"))
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
                           sizes: tuple[int] = (5,)):
    keyboard = InlineKeyboardBuilder()
    start = page * items_per_page
    end = start + items_per_page
    for user in data[start:end]:
        if user in data:
            keyboard.add(InlineKeyboardButton(text=user + " ✅", callback_data=f"select_{user}"))
        else:
            keyboard.add(InlineKeyboardButton(text=user, callback_data=f"select_{user}"))

    navigation_buttons = []
    if start > 0:
        navigation_buttons.append(InlineKeyboardButton(text="Previous", callback_data=f"page_{page - 1}"))
    if end < len(data):
        navigation_buttons.append(InlineKeyboardButton(text="Next", callback_data=f"page_{page + 1}"))

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

def get_best_step_kbds(
        *,
        data: list[str] = [],):
    keyboard = InlineKeyboardBuilder()

    for user in data:
        keyboard.add(InlineKeyboardButton(text=user, callback_data=f"bs_{user}"))
    
    return keyboard.adjust(5,5).as_markup()