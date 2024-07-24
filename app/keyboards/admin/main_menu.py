"""Здесь расположены клавиатуры, связанные с главным меню администраторов"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Клавиатура главного меню бота для администраторов
admin_menu = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Вывести список запросов 🔍')],
                                           [KeyboardButton(text='Редактировать базу ресторанов 🏛⚙️')],
                                           [KeyboardButton(text='Редактировать базу пользователей 👨⚙️')],
                                           [KeyboardButton(text='Вывести информацию о курьерах 🚴‍♂️🤖')],
                                           [KeyboardButton(text='Очистить таблицу завершенных заказов 🧹')],
                                           [KeyboardButton(text='Закрыть бота на техобслуживание ⚠️')],
                                           [KeyboardButton(text='Открыть бота для заказов ✅')]],
                                 resize_keyboard=True)
