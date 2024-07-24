"""Здесь расположены клавиатуры, связанные с отправкой запроса пользователем"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# Клавиатура со стандартными проблемами пользователя
common_problems = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='Доставили не мой заказ 😕', callback_data='wrong_order')],
                     [InlineKeyboardButton(text='Курьер заблудился 😶‍🌫️', callback_data='lost_courier')],
                     [InlineKeyboardButton(text='Некорректное поведение курьера 🤬', callback_data='angry_courier')],
                     [InlineKeyboardButton(text='Другая проблема 🤔', callback_data='new_ticket')]])


# Создание клавиатуры для отправки сообщения заблудившемуся курьеру
async def text_to_courier(courier_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Написать курьеру 📝', callback_data=f'text_courier_{courier_id}')]])
    return keyboard
