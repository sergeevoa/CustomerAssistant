"""Здесь расположены клавиатуры, связанные с редактированием объектов категорий ресторанов в БД"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import app.database.requests.restaurant_categories as rq_res_cat

# Builder - инструмент для создания нестатичных клавиатур. Полезен при работе с базами данных.
from aiogram.utils.keyboard import InlineKeyboardBuilder


# Создание клавиатуры со списком категорий ресторанов
async def all_restaurant_categories():
    categories = await rq_res_cat.get_restaurant_categories()
    keyboard = InlineKeyboardBuilder()
    for category in categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f'adm_res_category_{category.id}'))
    keyboard.add(InlineKeyboardButton(text='Добавить категорию ➕', callback_data='add_res_category'))
    keyboard.add(InlineKeyboardButton(text='Назад 🔙', callback_data='adm_to_main'))
    return keyboard.adjust(1).as_markup()


# Создание клавиатуры меню редактирования категории ресторанов
async def rest_cat_editing(category_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Рестораны категории 🏛', callback_data=f'restaurants_editing_{category_id}')],
        [InlineKeyboardButton(text='Изменить название 📝', callback_data=f'rc_edit_{category_id}')],
        [InlineKeyboardButton(text='Удалить категорию ❌', callback_data=f'rc_delete_{category_id}')],
        [InlineKeyboardButton(text='Назад 🔙', callback_data='to_res_categories_editing')]])
    return keyboard


# Создание клавиатуры для возвращения назад к категории ресторанов
async def back_to_rest_category(category_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Вернуться к категории 🔙', callback_data=f'adm_res_category_{category_id}')]])
    return keyboard


# Создание клавиатуры для возвращения к списку ресторанов категории
async def back_to_category_restaurants(category_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='К ресторанам категории 🏛🔙', callback_data=f'restaurants_editing_{category_id}')]])
    return keyboard
