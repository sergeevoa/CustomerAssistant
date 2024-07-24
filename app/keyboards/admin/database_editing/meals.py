"""Здесь расположены клавиатуры, связанные с редактированием объектов блюд в БД"""

from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton

import app.database.requests.meals as rq

# Builder - инструмент для создания нестатичных клавиатур. Полезен при работе с базами данных.
from aiogram.utils.keyboard import InlineKeyboardBuilder


# Создание клавиатуры со списком блюд из категории
async def meals(meal_category_id):
    all_meals = await rq.get_meals(meal_category_id)
    keyboard = InlineKeyboardBuilder()
    for meal in all_meals:
        keyboard.add(InlineKeyboardButton(text=meal.name, callback_data=f'adm_meal_{meal.id}'))
    keyboard.add(InlineKeyboardButton(text='Добавить блюдо ➕',
                                      callback_data=f'add_meal_in_{meal_category_id}'))
    keyboard.add(InlineKeyboardButton(text='Назад 🔙', callback_data=f'ad_meal_category_{meal_category_id}'))
    return keyboard.adjust(2).as_markup()


# Создание клавиатуры для редактирования блюда
async def meal_editing(meal):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Изменить данные ⚙️', callback_data=f'adm_edit_{meal.id}_meal')],
        [InlineKeyboardButton(text='Удалить блюдо ❌', callback_data=f'adm_delete_{meal.id}_meal')],
        [InlineKeyboardButton(text='Назад 🔙', callback_data=f'meals_editing_{meal.category_id}')]
    ])
    return keyboard


# Создание клавиатуры для выбора изменяемого атрибута блюда
async def meal_edit_data_choosing(meal_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Изменить название 📝', callback_data=f'name_editing_meal_{meal_id}')],
        [InlineKeyboardButton(text='Изменить фото 🖼', callback_data=f'photo_editing_meal_{meal_id}')],
        [InlineKeyboardButton(text='Изменить состав 🍄🥕', callback_data=f'compound_editing_meal_{meal_id}')],
        [InlineKeyboardButton(text='Изменить значение калорийности ⚖️',
                              callback_data=f'caloric_capacity_editing_{meal_id}')],
        [InlineKeyboardButton(text='Изменить цену 💵', callback_data=f'price_editing_meal_{meal_id}')],
        [InlineKeyboardButton(text='Назад 🔙', callback_data=f'adm_meal_{meal_id}')]
    ])
    return keyboard


# Создание клавиатуры с кнопкой, возвращающей в меню редактирования блюда
async def back_to_meal(meal_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='К меню блюда 🍔', callback_data=f'adm_meal_{meal_id}')]
    ])
    return keyboard


# Клавиатура с кнопкой, предлагающей не указывать калорийность блюда
caloric_capacity_input_choice = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Не указывать калорийность')]],
                                                    resize_keyboard=True)
