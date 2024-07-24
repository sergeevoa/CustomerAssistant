"""Здесь расположены клавиатуры, связанные c ролью курьера"""

from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import app.database.requests.orders as rq_ord

# Клавиатура главного меню бота для курьеров
courier_main_menu = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Вывести список заказов 🔍')]],
                                        resize_keyboard=True)


# Созданием клавиатуры со списком готовящихся заказов
async def all_cooking_orders():
    keyboard = InlineKeyboardBuilder()
    cooking_orders = await rq_ord.get_all_cooking_orders()
    for order in cooking_orders:
        keyboard.add(InlineKeyboardButton(text=f'Заказ № {order.id}', callback_data=f'get_order_{order.id}'))
    return keyboard.adjust(2).as_markup()


# Создание клавиатуры действий с заказом
async def order_menu(order_id, customer_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Взять заказ ✅', callback_data=f'deliver_order_{order_id}_{customer_id}')],
        [InlineKeyboardButton(text='Назад 🔙', callback_data='cooked_order_list')]])
    return keyboard


# Клавиатура завершения доставки
delivering_end = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Завершить доставку ✅')]], resize_keyboard=True)
