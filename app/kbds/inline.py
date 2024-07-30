from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData



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
    # buttons = [InlineKeyboardButton(
    #     text=option + (" ✅" if option in data else ""),
    #     callback_data=f"select_{option}"
    # ) for option in data[start:end]]
    # keyboard.add(*buttons)

    navigation_buttons = []
    if start > 0:
        navigation_buttons.append(InlineKeyboardButton(text="Previous", callback_data=f"page_{page - 1}"))
    if end < len(data):
        navigation_buttons.append(InlineKeyboardButton(text="Next", callback_data=f"page_{page + 1}"))

    keyboard.add(*navigation_buttons)
    return keyboard.adjust(*sizes).as_markup()