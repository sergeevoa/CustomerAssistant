"""Здесь расположены обработчики, связанные с главным меню менеджера"""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import app.keyboards.manager as kb
import app.database.requests.managers as rq
import app.database.requests.restaurants as rq_r
import app.database.requests.orders as rq_ord
import app.database.requests.ordered_meals as rq_ord_m
import app.database.requests.meals as rq_m
import app.database.requests.order_collection_addresses as rq_ord_c
import app.filters as flt
import app.states as st

manager_router = Router()
manager_router.message.filter(flt.CheckManager())
manager_router.callback_query.filter(flt.CheckManager())


# Обработчик команды start для менеджеров
@manager_router.message(Command('manager_start'))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    manager = await rq.get_manager(message.from_user.id)
    restaurant = await rq_r.get_restaurant(manager.restaurant_id)
    await state.set_state(st.ManagerWork.restaurant_id)
    await state.update_data(restaurant_id=restaurant.id)
    await message.answer(f'Приветствую, менеджер {manager.name} {manager.surname} из ресторана {restaurant.name}!',
                         reply_markup=kb.man_menu)


# Обработчик нажатия на кнопку "Вывести список заказов"
@manager_router.message(F.text == 'Вывести список заказов 🔍', st.ManagerWork.restaurant_id)
async def show_orders(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.answer('Список заказов 📝',
                         reply_markup=await kb.all_orders_with_this_restaurant_meals(data["restaurant_id"]))


# Обработчик нажатия на кнопку заказа
@manager_router.callback_query(F.data.startswith('man_order_'), st.ManagerWork.restaurant_id)
async def order_check(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    data = await state.get_data()
    printable_meal_names = ''
    order_id = int(callback.data.split('_')[2])
    ordered_meals = await rq_ord_m.get_all_ordered_meals(order_id)
    for ordered_meal in ordered_meals:
        meal = await rq_m.get_meal(ordered_meal.meal_id)
        if meal.restaurant_id == data["restaurant_id"]:
            printable_meal_names = printable_meal_names + meal.name + ' x1\n'
    await callback.message.answer(f'Заказ № {order_id}, блюда:\n{printable_meal_names}',
                                  reply_markup=await kb.order_taking(order_id))


# Обработчик нажатия на кнопку "Установить адрес готовки"
@manager_router.callback_query(F.data.startswith('man_address_choosing_'), st.ManagerWork.restaurant_id)
async def make_order_cooking(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    data = await state.get_data()
    order_id = int(callback.data.split('_')[3])
    await callback.message.answer('Выберите адрес ресторана, в котором будет приготовлен этот заказ',
                                  reply_markup=await kb.man_address_choosing(data["restaurant_id"], order_id))


# Обработчик нажатия на кнопку адреса готовки
@manager_router.callback_query(F.data.startswith('set_order_address_'),  st.ManagerWork.restaurant_id)
async def place_order_collection_address(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    order_id = int(callback.data.split('_')[3])
    address_id = int(callback.data.split('_')[4])
    await rq_ord_c.add_order_collection_address(order_id, address_id)

    # Проверка: для всех ли ресторанов в заказе указаны адреса:
    unique_restaurant_ids = []                                    # Список уникальных id ресторанов всех заказанных блюд
    # Переменная, показывающая, уникален ли этот restaurant_id рассматриваемого meal
    is_unique = True
    ordered_meals = await rq_ord_m.get_all_ordered_meals(order_id)
    for ordered_meal in ordered_meals:
        meal = await rq_m.get_meal(ordered_meal.meal_id)
        for restaurant_id in unique_restaurant_ids:                # Для каждого id ресторана, уже находящегося в списке
            if restaurant_id == meal.restaurant_id:                # Сравниваем его с id ресторана этого блюда
                is_unique = False
                break
        if is_unique:
            unique_restaurant_ids.append(meal.restaurant_id)        # Если значение уникально, добавляем его в список

    order_collection_addresses = await rq_ord_c.get_order_collection_addresses(order_id)
    # Если длина списка адресов сбора заказа равна длине списка уникальных id ресторанов,
    # значит адреса сбора заказанных блюд из всех ресторанов уже проставлены
    if len(list(order_collection_addresses)) == len(unique_restaurant_ids):
        await rq_ord.change_order_status(order_id, 2)       # И можно поставить заказу статус "готовится"

    await callback.message.answer('Адрес выдачи заказа добавлен ✅')
    await show_orders(callback.message, state)


# Обработчик нажатия на кнопку "Назад" при просмотре заказа
@manager_router.callback_query(F.data.startswith('to_order_list'), st.ManagerWork.restaurant_id)
async def back_to_order_list(callback: CallbackQuery, state: FSMContext):
    await callback.answer('Вы переходите к списку доступных заказов')
    await show_orders(callback.message, state)
