"""Здесь расположены клавиатуры, связанные с редактированием объектов курьеров в БД"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import app.database.requests.couriers as rq

# Builder - инструмент для создания нестатичных клавиатур. Полезен при работе с базами данных.
from aiogram.utils.keyboard import InlineKeyboardBuilder


# Создание клавиатуры со списком курьеров
async def couriers():
    all_couriers = await rq.get_all_couriers()
    keyboard = InlineKeyboardBuilder()
    for courier in all_couriers:
        keyboard.add(InlineKeyboardButton(text=f'{courier.id}. {courier.name} {courier.surname}',
                                          callback_data=f'courier_{courier.id}'))
    keyboard.add(InlineKeyboardButton(text='Добавить курьера ➕',
                                      callback_data=f'add_courier'))
    keyboard.add(InlineKeyboardButton(text='Назад 🔙', callback_data=f'adm_to_main'))
    return keyboard.adjust(2).as_markup()


# Создание клавиатуры с кнопкой, возвращающей в меню редактирования курьера
async def back_to_courier(courier_id):
    courier = await rq.get_courier_by_id(courier_id)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='К окну курьера 🚴‍♂️', callback_data=f'courier_{courier.id}')]
    ])
    return keyboard
