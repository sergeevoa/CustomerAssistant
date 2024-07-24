"""Здесь расположены клавиатуры, связанные с редактированием объектов менеджеров в БД"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import app.database.requests.managers as rq


# Builder - инструмент для создания нестатичных клавиатур. Полезен при работе с базами данных.
from aiogram.utils.keyboard import InlineKeyboardBuilder


# Создание клавиатуры со списком менеджеров
async def managers(restaurant_id):
    all_managers = await rq.get_all_managers_from_restaurant(restaurant_id)
    keyboard = InlineKeyboardBuilder()
    for manager in all_managers:
        keyboard.add(InlineKeyboardButton(text=f'{manager.id}. {manager.name} {manager.surname}',
                                          callback_data=f'manager_{manager.id}'))
    keyboard.add(InlineKeyboardButton(text='Добавить менеджера ➕',
                                      callback_data=f'add_manager_{restaurant_id}'))
    keyboard.add(InlineKeyboardButton(text='Назад 🔙', callback_data=f'adm_to_main'))
    return keyboard.adjust(1).as_markup()


# Создание клавиатуры с кнопкой, возвращающей в меню редактирования менеджера
async def back_to_manager(manager_id):
    manager = await rq.get_manager_by_id(manager_id)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='К окну менеджера 👨', callback_data=f'manager_{manager.id}')]
    ])
    return keyboard
