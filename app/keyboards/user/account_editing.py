"""Здесь расположены клавиатуры, связанные с редактированием аккаунта пользователем"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Клавиатура, связанная с выбором редактируемых данных пользователя
data_choosing = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Изменить имя 🗣')],
                                              [KeyboardButton(text='Изменить номер телефона 📲')]],
                                    resize_keyboard=True)

# Клавиатура, появляющаяся при удалении аккаунта
start_keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='/start')]], resize_keyboard=True)
