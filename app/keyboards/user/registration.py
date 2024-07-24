"""Здесь расположены клавиатуры, связанные с регистрацией пользователя"""

from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton


# Клавиатура для регистрации
register_kb = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='Зарегистрироваться 🚀', callback_data='register')]])

# Клавиатура для запроса номера телефона пользователя.
# Параметр request_contact=True отправляет запрос на получение номера.
get_number = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Отправить номер аккаунта', request_contact=True)]],
                                 input_field_placeholder='Введите свой номер...', resize_keyboard=True)
