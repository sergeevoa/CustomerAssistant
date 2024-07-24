"""Здесь расположены клавиатуры, связанные с редактированием объектов ресторанов в БД"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import app.database.requests.restaurant_categories as rq_res_cat
import app.database.requests.restaurants as rq_res

# Builder - инструмент для создания нестатичных клавиатур. Полезен при работе с базами данных.
from aiogram.utils.keyboard import InlineKeyboardBuilder


# Создание клавиатуры со списком ресторанов
async def restaurants(category_id):
    all_restaurants = await rq_res.get_category_restaurants(category_id)
    keyboard = InlineKeyboardBuilder()
    for restaurant in all_restaurants:
        keyboard.add(InlineKeyboardButton(text=restaurant.name, callback_data=f'adm_restaurant_{restaurant.id}'))
    keyboard.add(InlineKeyboardButton(text='Добавить ресторан ➕', callback_data=f'add_restaurant_in_{category_id}'))
    keyboard.add(InlineKeyboardButton(text='Назад 🔙', callback_data=f'adm_res_category_{category_id}'))
    return keyboard.adjust(1).as_markup()


# Создание клавиатуры для добавления второго и последующих адресов ресторана при его создании
async def add_rest_address(category_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Добавить адрес ➕', callback_data='another_address')],
        [InlineKeyboardButton(text='Назад 🔙', callback_data=f'restaurants_editing_{category_id}')],
        [InlineKeyboardButton(text='В главное меню 📱', callback_data='to_main')]])
    return keyboard


# Создание клавиатуры для редактирования ресторана
async def restaurant_editing(restaurant):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Категории блюд 🥡', callback_data=f'meal_categories_editing_{restaurant.id}')],
        [InlineKeyboardButton(text='Изменить данные ⚙️', callback_data=f'restaurant_edit_{restaurant.id}')],
        [InlineKeyboardButton(text='Удалить ресторан ❌', callback_data=f'restaurant_delete_{restaurant.id}')],
        [InlineKeyboardButton(text='Назад 🔙', callback_data=f'restaurants_editing_{restaurant.category_id}')]])
    return keyboard


# Создание клавиатуры для выбора изменяемого атрибута ресторана
async def restaurant_edit_data_choosing(restaurant_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Изменить название 📝', callback_data=f'rest_name_editing_{restaurant_id}')],
        [InlineKeyboardButton(text='Изменить фото 🖼', callback_data=f'rest_photo_editing_{restaurant_id}')],
        [InlineKeyboardButton(text='Изменить категорию 🥣', callback_data=f'change_category_{restaurant_id}')],
        [InlineKeyboardButton(text='Назад 🔙', callback_data=f'to_rest_{restaurant_id}_editing')]])
    return keyboard


# Создание клавиатуры с кнопкой, возвращающей в меню редактирования ресторана
async def back_to_restaurant(restaurant_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='К меню ресторана 🏛', callback_data=f'adm_restaurant_{restaurant_id}')]
    ])
    return keyboard


# Создание клавиатуры для выбора новой категории ресторана
async def change_category(restaurant_id):
    keyboard = InlineKeyboardBuilder()
    restaurant = await rq_res.get_restaurant(restaurant_id)
    categories = await rq_res_cat.get_all_categories_except_this(restaurant.category_id)
    for category in categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f'new_restaurant_category_{category.id}'))
    keyboard.add(InlineKeyboardButton(text='Назад 🔙', callback_data=f'adm_restaurant_{restaurant_id}'))
    return keyboard.adjust(1).as_markup()


# Создание клавиатуры с кнопкой, возвращающей в меню выбора категории блюд ресторана
async def back_to_restaurant_meal_categories(restaurant_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='К категориям блюд ресторана 🥡',
                              callback_data=f'meal_categories_editing_{restaurant_id}')]
    ])
    return keyboard
