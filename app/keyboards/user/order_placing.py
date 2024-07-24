"""Здесь расположены клавиатуры, связанные с оформлением заказа пользователем"""

from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton

import app.database.requests.restaurant_categories as rq_res_cat
import app.database.requests.restaurants as rq_res
import app.database.requests.meal_categories as rq_m_cat
import app.database.requests.meals as rq_m
import app.database.requests.ordered_meals as rq_ord_m
import app.database.requests.addresses as rq_addr

# Builder - инструмент для создания нестатичных клавиатур. Полезен при работе с базами данных.
from aiogram.utils.keyboard import InlineKeyboardBuilder


# Создание клавиатуры со списком категорий ресторанов
async def all_restaurant_categories():
    categories = await rq_res_cat.get_restaurant_categories()
    keyboard = InlineKeyboardBuilder()
    for category in categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f'res_category_{category.id}'))
    keyboard.add(InlineKeyboardButton(text='Назад 🔙', callback_data='to_main'))
    return keyboard.adjust(1).as_markup()


# Создание клавиатуры со списком ресторанов
async def restaurants(category_id):
    all_restaurants = await rq_res.get_category_restaurants(category_id)
    keyboard = InlineKeyboardBuilder()
    for restaurant in all_restaurants:
        keyboard.add(InlineKeyboardButton(text=restaurant.name, callback_data=f'restaurant_{restaurant.id}'))
    keyboard.add(InlineKeyboardButton(text='Назад 🔙', callback_data='to_res_categories'))
    return keyboard.adjust(1).as_markup()


# Создание клавиатуры со списком категорий блюд в ресторане
async def meal_categories(restaurant_id, res_category_id):
    categories = await rq_m_cat.get_meal_categories(restaurant_id)
    keyboard = InlineKeyboardBuilder()
    for category in categories:
        keyboard.add(InlineKeyboardButton(text=category.name, callback_data=f'meal_category_{category.id}'))
    keyboard.add(InlineKeyboardButton(text='Назад 🔙', callback_data=f'to_restaurants_{res_category_id}'))
    return keyboard.adjust(1).as_markup()


# Создание клавиатуры со списком блюд из категории
async def meals(meal_category_id, restaurant_id):
    all_meals = await rq_m.get_meals(meal_category_id)
    keyboard = InlineKeyboardBuilder()
    for meal in all_meals:
        keyboard.add(InlineKeyboardButton(text=meal.name, callback_data=f'meal_{meal.id}'))
    keyboard.add(InlineKeyboardButton(text='Назад 🔙', callback_data=f'to_{restaurant_id}_meal_category'))
    return keyboard.adjust(2).as_markup()


# Создание клавиатуры для добавления блюда в корзину
async def add_to_basket(meal_id, meal_category_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Добавить в корзину 🧺', callback_data=f'add_meal_{meal_id}')],
        [InlineKeyboardButton(text='Назад 🔙', callback_data=f'to_meals_{meal_category_id}')]])
    return keyboard


# Клавиатура для выбора следующего шага после добавления товара в корзину
order_next_steps_1 = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Корзина 🧺')],
                                                   [KeyboardButton(text='Указать адрес доставки 🏡')],
                                                   [KeyboardButton(text='Добавить блюдо 🍔')],
                                                   [KeyboardButton(text='Отменить заказ ❌')]], resize_keyboard=True)


# Клавиатура для выбора следующего шага после указания адреса доставки
order_next_steps_2 = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Корзина 🧺')],
                                                   [KeyboardButton(text='Изменить адрес доставки 🏡')],
                                                   [KeyboardButton(text='Перейти к оплате 💵')],
                                                   [KeyboardButton(text='Добавить блюдо 🍔')],
                                                   [KeyboardButton(text='Отменить заказ ❌')]], resize_keyboard=True)


# Создание клавиатуры для блюда в корзине
async def meal_in_basket(meal_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Назад 🔙', callback_data='to_basket')],
        [InlineKeyboardButton(text='Удалить ❌', callback_data=f'delete_ordered_meal_{meal_id}')]])
    return keyboard


# Создание клавиатуры для вывода всех товаров из корзины
async def all_ordered_meals(order_id):
    all_customer_meals = await rq_ord_m.get_all_ordered_meals(order_id)
    keyboard = InlineKeyboardBuilder()
    for customer_meal in all_customer_meals:
        meal = await rq_m.get_meal(customer_meal.meal_id)
        keyboard.add(InlineKeyboardButton(text=meal.name, callback_data=f'ordered_meal_{meal.id}'))
    return keyboard.adjust(3).as_markup()


# Создание клавиатуры для вывода списка адресов пользователя
async def all_addresses(user_id):
    all_user_addresses = await rq_addr.get_user_addresses(user_id)
    keyboard = InlineKeyboardBuilder()
    for address in all_user_addresses:
        if address.entrance and address.apartment:
            keyboard.add(InlineKeyboardButton(text=f'{address.district} р-н, ул. {address.street}, д. {address.home}, '
                                                   f'подъезд {address.entrance}, кв. {address.apartment}',
                                              callback_data=f'user_address_{address.id}'))
        else:
            keyboard.add(InlineKeyboardButton(text=f'{address.district} р-н, ул. {address.street}, д. {address.home}',
                                              callback_data=f'user_address_{address.id}'))
    keyboard.add(InlineKeyboardButton(text='Добавить новый адрес', callback_data='new_address'))
    return keyboard.adjust(1).as_markup()


# Создание клавиатуры для подтверждения доставки заказа
async def deliver_approve(order_id, courier_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Подтвердить доставку', callback_data=f'delivery_approve_{order_id}_{courier_id}')]])
    return keyboard
