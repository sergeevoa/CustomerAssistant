"""Здесь расположены клавиатуры, связанные с главным меню пользователя"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Клавиатура главного меню бота
main_menu = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Заказать еду 🥡')],
                                          [KeyboardButton(text='Мои заказы 📝')],
                                          [KeyboardButton(text='Редактировать профиль ⚙️')],
                                          [KeyboardButton(text='Сообщить о проблеме ⚠️')],
                                          [KeyboardButton(text='Удалить аккаунт ❌')]], resize_keyboard=True)
