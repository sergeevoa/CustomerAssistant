"""Здесь расположены клавиатуры, связанные c ролью менеджера"""

from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
import app.database.requests.orders as rq_ord
import app.database.requests.ordered_meals as rq_ord_m
import app.database.requests.meals as rq_m
import app.database.requests.addresses as rq_addr
import app.database.requests.order_collection_addresses as rq_ord_c_addr

# Клавиатура главного меню бота для менеджеров
man_menu = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Вывести список заказов 🔍')]], resize_keyboard=True)


# Создание клавиатуры со списком заказов, содержащих блюда из ресторана, где работает менеджер
async def all_orders_with_this_restaurant_meals(restaurant_id):
    needed_order_list = []                                      # Сюда будут добавляться заказы, соответствующие условию
    keyboard = InlineKeyboardBuilder()
    addresses = await rq_addr.get_restaurant_addresses(restaurant_id)
    all_placed_orders = await rq_ord.get_all_placed_orders()

    for placed_order in all_placed_orders:
        # Проверка: не был ли уже определен адрес приготовления для блюд этого ресторана из заказа
        address_is_not_chosen = True
        for address in addresses:
            # Если для этого заказа уже указан один из адресов ресторана
            if await rq_ord_c_addr.get_this_restaurant_order_collection_address(address.id, placed_order.id):
                # Значит адрес его приготовления уже был выбран менеджером этого ресторана
                address_is_not_chosen = False
                break

        # Добавляем заказ в необходимые для вывода только если адрес для него еще не был указан
        if address_is_not_chosen:
            ordered_meals = await rq_ord_m.get_all_ordered_meals(placed_order.id)
            for ordered_meal in ordered_meals:
                meal = await rq_m.get_meal(ordered_meal.meal_id)
                if meal.restaurant_id == restaurant_id:
                    needed_order_list.append(placed_order)
                    break

    for order in needed_order_list:
        keyboard.add(InlineKeyboardButton(text=f'Заказ № {order.id}', callback_data=f'man_order_{order.id}'))
    return keyboard.adjust(2).as_markup()


# Создание клавиатуры для взятия заказа
async def order_taking(order_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                                                     [InlineKeyboardButton(text='Установить адрес готовки 🔥',
                                                                           callback_data=f'man_address_choosing_{order_id}')],
                                                     [InlineKeyboardButton(text='Назад 🔙',
                                                                           callback_data='to_order_list')]])
    return keyboard


# Создание клавиатуры для выбора менеджером адреса ресторана, где будет готовиться этот заказ
async def man_address_choosing(restaurant_id, order_id):
    keyboard = InlineKeyboardBuilder()
    restaurant_addresses = await rq_addr.get_restaurant_addresses(restaurant_id)
    for address in restaurant_addresses:
        keyboard.add(InlineKeyboardButton(text=f'{address.district} р-н, ул. {address.street} д. {address.home}',
                                          callback_data=f'set_order_address_{order_id}_{address.id}'))
    keyboard.add(InlineKeyboardButton(text='Назад 🔙', callback_data=f'man_order_{order_id}'))
    return keyboard.adjust(1).as_markup()
