"""Здесь расположены клавиатуры, связанные с ответами на пользовательские запросы"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import app.database.requests.tickets as rq_t

# Builder - инструмент для создания нестатичных клавиатур. Полезен при работе с базами данных.
from aiogram.utils.keyboard import InlineKeyboardBuilder


# Создание клавиатуры со списком пользовательских запросов
async def all_tickets():
    tickets = await rq_t.get_tickets()
    keyboard = InlineKeyboardBuilder()
    for ticket in tickets:
        keyboard.add(InlineKeyboardButton(text=f'Запрос № {ticket.id}', callback_data=f'ticket_{ticket.id}'))
    keyboard.add(InlineKeyboardButton(text='Назад 🔙', callback_data='adm_to_main'))
    return keyboard.adjust(2).as_markup()


# Клавиатура для выхода из состояния пользовательского запроса
ticket_exit = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад 🔙', callback_data='to_ticket_list')],
    [InlineKeyboardButton(text='В главное меню 📱', callback_data='to_main')]])
