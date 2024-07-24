"""Здесь расположены клавиатуры, которые могут выполнять разные функции для пользователей с различными ролями"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Клавиатура для выхода в главное меню
to_menu = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='В главное меню 📱')]], resize_keyboard=True)

# Клавиатура с кнопками "Да" и "Нет"
yes_no = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Да ✅'), KeyboardButton(text='Нет ❌')]],
                             resize_keyboard=True)
