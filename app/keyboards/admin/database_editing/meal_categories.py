"""Здесь расположены клавиатуры, связанные с редактированием объектов категорий блюд в БД"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import app.database.requests.meal_categories as rq_m_cat

# Builder - инструмент для создания нестатичных клавиатур. Полезен при работе с базами данных.
from aiogram.utils.keyboard import InlineKeyboardBuilder


# Создание клавиатуры со списком категорий блюд в ресторане
async def meal_categories(restaurant_id):
    categories = await rq_m_cat.get_meal_categories(restaurant_id)
    keyboard = InlineKeyboardBuilder()
    for category in categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f'ad_meal_category_{category.id}'))
    keyboard.add(InlineKeyboardButton(text='Добавить категорию блюд ➕',
                                      callback_data=f'add_meal_category_in_{restaurant_id}'))
    keyboard.add(InlineKeyboardButton(text='Назад 🔙', callback_data=f'adm_restaurant_{restaurant_id}'))
    return keyboard.adjust(1).as_markup()


# Создание клавиатуры для редактирования категории блюд
async def meal_category_editing(meal_category):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Блюда категории 🍔', callback_data=f'meals_editing_{meal_category.id}')],
        [InlineKeyboardButton(text='Изменить данные ⚙️', callback_data=f'meal_category_edit_{meal_category.id}')],
        [InlineKeyboardButton(text='Удалить категорию ❌', callback_data=f'meal_category_delete_{meal_category.id}')],
        [InlineKeyboardButton(text='Назад 🔙', callback_data=f'meal_categories_editing_{meal_category.restaurant_id}')]
    ])
    return keyboard


# Создание клавиатуры для выбора изменяемого атрибута категории блюд
async def meal_category_data_choosing(category_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Изменить название 📝', callback_data=f'meal_cat_name_editing_{category_id}')],
        [InlineKeyboardButton(text='Изменить фото 🖼', callback_data=f'meal_cat_photo_editing_{category_id}')]
    ])
    return keyboard


# Создание клавиатуры с кнопкой, возвращающей в меню редактирования категории блюд
async def back_to_meal_category(category_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Назад 🔙', callback_data=f'ad_meal_category_{category_id}')]
    ])
    return keyboard


# Создание клавиатуры с кнопкой, возвращающей в меню выбора блюд категории
async def back_to_category_meals(category_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='К блюдам категории 🍽', callback_data=f'meals_editing_{category_id}')]
    ])
    return keyboard
