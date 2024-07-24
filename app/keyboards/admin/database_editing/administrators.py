"""Здесь расположены клавиатуры, связанные с редактированием объектов администраторов в БД"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import app.database.requests.administrators as rq

# Builder - инструмент для создания нестатичных клавиатур. Полезен при работе с базами данных.
from aiogram.utils.keyboard import InlineKeyboardBuilder


# Создание клавиатуры со списком администраторов
async def administrators():
    admins = await rq.get_all_admins()
    keyboard = InlineKeyboardBuilder()
    for admin in admins:
        keyboard.add(InlineKeyboardButton(text=f'{admin.id}. {admin.name} {admin.surname}',
                                          callback_data=f'admin_{admin.id}'))
    keyboard.add(InlineKeyboardButton(text='Добавить администратора ➕',
                                      callback_data=f'add_admin'))
    keyboard.add(InlineKeyboardButton(text='Назад 🔙', callback_data=f'adm_to_main'))
    return keyboard.adjust(1).as_markup()


# Создание клавиатуры с кнопкой, возвращающей в меню редактирования администратора
async def back_to_admin(admin_id):
    admin = await rq.get_admin_by_id(admin_id)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='К окну администратора 👨', callback_data=f'admin_{admin.id}')]
    ])
    return keyboard
